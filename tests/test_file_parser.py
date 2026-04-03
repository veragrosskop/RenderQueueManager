import tempfile
import unittest
import os
from src.errors import SequenceError, InvalidFileNameError
from src.file_parser import File, FileSequenceParser


class TestFile(unittest.TestCase):

    def setUp(self):
        # initial testing environment setup
        self.directory = "/tmp"  # dummy directory

    def test_extra_underscore(self):
        """Reject frame with less than or more than 4 digits"""
        with self.assertRaises(InvalidFileNameError):
            File("render_a_123.png", self.directory)
        with self.assertRaises(InvalidFileNameError):
            File("a_render_12345.png", self.directory)

    def test_invalid_frame_digits(self):
        """Reject frame with less than or more than 4 digits"""
        with self.assertRaises(InvalidFileNameError):
            File("render_123.png", self.directory)
        with self.assertRaises(InvalidFileNameError):
            File("render_12345.png", self.directory)

    def test_invalid_extension(self):
        """Reject unsupported file extension"""
        with self.assertRaises(InvalidFileNameError):
            File("render_0001.gif", self.directory)

    def test_invalid_extra_token(self):
        """Reject filenames with extra underscore token"""
        with self.assertRaises(InvalidFileNameError):
            File("render_01_0001.exr", self.directory)

    def test_invalid_order(self):
        """Reject filenames where extension is misplaced"""
        with self.assertRaises(InvalidFileNameError):
            File("render.exr_0001.png", self.directory)


class TestFileSequenceParser(unittest.TestCase):  # dummy directory

    def test_no_frames_exist(self):
        """Reject all missing frames"""

        # initialize empty sequence directory
        with tempfile.TemporaryDirectory() as tmpdir:
            parser = FileSequenceParser(tmpdir)

            # case no files and no given frame range
            with self.assertRaises(SequenceError):
                parser.check_missing_frames()

            parser.frame_range = (1001, 1005)
            with self.assertRaises(SequenceError):
                missing_all = parser.check_missing_frames()

    def test_missing_some_frames(self):
        """Reject missing names"""

        with tempfile.TemporaryDirectory() as tmpdir:
            filenames = [
                "render_0001.exr",
                "render_0002.exr",
                # missing 0003
                "render_0004.exr",
                "render_0005.exr",
                # missing 0006
                "render_0007.exr",
            ]

            for f in filenames:
                open(os.path.join(tmpdir, f), "w").close()

            parser = FileSequenceParser(tmpdir)
            missing = parser.check_missing_frames()
            parser.frame_range = (1, 9)
            missing_end = parser.check_missing_frames()

            self.assertEqual(missing, {"render": [3, 6]})
            self.assertEqual(missing_end, {"render": [3, 6, 8, 9]})

    def test_missing_tail_frames(self):
        """Reject missing tail frames, or accept with no frame range given"""

        with tempfile.TemporaryDirectory() as tmpdir:
            filenames = [
                "render_1002.exr",
                # missing 1003
                "render_1004.exr",
                "render_1005.exr",
                # missing 1006
                "render_1007.exr",
            ]

            for f in filenames:
                open(os.path.join(tmpdir, f), "w").close()

            parser = FileSequenceParser(tmpdir)
            parser.frame_range = (1001, 1007)
            missing_start = parser.check_missing_frames()
            parser.frame_range = (1001, 1009)
            missing_start_end = parser.check_missing_frames()

            self.assertEqual(missing_start, {"render": [1001, 1003, 1006]})
            self.assertEqual(missing_start_end, {"render": [1001, 1003, 1006, 1008, 1009]})

    def test_all_frames_exist(self):
        """Assert all frames exist"""

        with tempfile.TemporaryDirectory() as tmpdir:
            filenames = [
                "render_1001.exr",
                "render_1002.exr",
                "render_1003.exr",
                "render_1004.exr",
                "render_1005.exr",
            ]

            for f in filenames:
                open(os.path.join(tmpdir, f), "w").close()

            parser = FileSequenceParser(tmpdir)
            missing_none = parser.check_missing_frames()

            self.assertEqual(missing_none, {"render": []})

    def test_invalid_file(self):
        """Test it skips over an invalid file"""

        with tempfile.TemporaryDirectory() as tmpdir:
            filenames = [
                "render_1001.exr",
                "some_temp_file.tmp",
                "render_1002.exr",
                "render_1003.exr",
                "README.txt",
                "render_1004.exr",
                "render_1005.exr",
            ]

            for f in filenames:
                open(os.path.join(tmpdir, f), "w").close()

            parser = FileSequenceParser(tmpdir)
            missing = parser.check_missing_frames()

            self.assertEqual(missing, {"render": []})


if __name__ == "__main__":
    unittest.main()
