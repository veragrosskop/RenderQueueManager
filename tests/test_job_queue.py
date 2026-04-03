from src.job_queue import Job, JobQueue, Priority
from src.file_parser import File
import unittest
from datetime import datetime, timedelta


class TestJobQueue(unittest.TestCase):

    def setUp(self):

        # Dummy file sequence for jobs
        self.filea1 = File("rendera_0001.exr", "/tmp")
        self.filea2 = File("rendera_0002.exr", "/tmp")
        self.filea3 = File("rendera_0003.exr", "/tmp")
        self.filea4 = File("rendera_0004.exr", "/tmp")
        self.sequence_a = [self.filea1, self.filea2, self.filea3, self.filea4]

        # Dummy file sequence for jobs
        self.fileb1 = File("renderb_0001.exr", "/tmp")
        self.fileb2 = File("renderb_0002.exr", "/tmp")
        self.fileb3 = File("renderb_0003.exr", "/tmp")
        self.fileb4 = File("renderb_0004.exr", "/tmp")
        self.sequence_b = [self.fileb1, self.fileb2, self.fileb3, self.fileb4]

    def test_job_creation_defaults(self):
        """Job should default to MEDIUM priority if none is given"""
        job = Job(job_id=0, sequence=self.sequence_a)
        self.assertEqual(job.priority, Priority.MEDIUM)
        self.assertTrue(isinstance(job.submit_time, datetime))

    def test_job_creation_custom_priority(self):
        """Job should accept a custom priority"""
        job = Job(job_id=0, sequence=self.sequence_b, priority=Priority.HIGH)
        self.assertEqual(job.priority, Priority.HIGH)

    def test_job_queue_add(self):
        """Jobs should be added to queue"""
        queue = JobQueue()
        job_a = Job(job_id=0, sequence=self.sequence_a)
        job_b = Job(job_id=1, sequence=self.sequence_b)
        queue.add(job_a)
        queue.add(job_b)
        self.assertEqual(len(queue._heap), 2)
        self.assertIs(queue.get_next_job(), job_a)
        self.assertIs(queue.get_next_job(), job_b)

    def test_queue_priority_sort(self):
        """Sort jobs by priority descending"""
        job_low = Job(0, [self.filea1], priority=Priority.LOW)
        job_high = Job(1, [self.fileb2], priority=Priority.HIGH)
        queue = JobQueue([job_low, job_high])

        # Assert order by priority
        self.assertIs(queue.get_next_job(), job_high)
        self.assertIs(queue.get_next_job(), job_low)

    def test_queue_submit_time_sort(self):
        """Sort jobs by submission time ascending"""
        # Create two jobs with artificial timestamps
        job1 = Job(1, [self.filea3])
        job1.submit_time = job1.submit_time - timedelta(seconds=20)  # simulate earlier submission
        job2 = Job(2, [self.filea2])

        queue = JobQueue([job2, job1])
        self.assertIs(queue.get_next_job(), job1)
        self.assertIs(queue.get_next_job(), job2)

    def test_queue_time_and_priority_sort(self):
        """Sort jobs by submission time ascending"""
        # Create two jobs with artificial timestamps
        job1 = Job(1, [self.filea3], priority=Priority.LOW)
        job1.submit_time = job1.submit_time - timedelta(seconds=20)  # simulate earlier submission
        job2 = Job(2, [self.filea2], priority=Priority.HIGH)
        job2.submit_time = job2.submit_time - timedelta(seconds=10)  # simulate earlier submission
        job3 = Job(3, [self.filea1])
        job4 = Job(4, [self.filea4], priority=Priority.HIGH)

        queue = JobQueue([job1, job2, job3, job4])
        self.assertIs(queue.get_next_job(), job2)
        self.assertIs(queue.get_next_job(), job4)
        self.assertIs(queue.get_next_job(), job3)
        self.assertIs(queue.get_next_job(), job1)


if __name__ == "__main__":
    unittest.main()
