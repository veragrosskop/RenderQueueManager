import unittest
from datetime import datetime, timedelta
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
        job = Job(sequence=self.sequence_a)
        self.assertEqual(job.priority, Priority.MEDIUM)
        self.assertTrue(isinstance(job.submit_time, datetime))

    def test_job_creation_custom_priority(self):
        """Job should accept a custom priority"""
        job = Job(sequence=self.sequence_b, priority=Priority.HIGH)
        self.assertEqual(job.priority, Priority.HIGH)

    def test_job_queue_add(self):
        """Jobs should be added to queue"""
        queue = JobQueue()
        job_a = Job(sequence=self.sequence_a)
        job_b = Job(sequence=self.sequence_b)
        queue.add(job_a)
        queue.add(job_b)
        self.assertEqual(len(queue._queue), 2)
        self.assertIs(queue.queue()[1], job_a.job_id)
        self.assertIs(queue.queue()[0], job_b.job_id)

    def test_queue_priority_sort(self):
        """Sort jobs by priority descending"""
        job_low = Job([self.filea1], priority=Priority.LOW)
        job_high = Job([self.fileb2], priority=Priority.HIGH)
        queue = JobQueue([job_low, job_high])

        # Assert order by priority
        self.assertIs(queue.queue()[1], job_high.job_id)
        self.assertIs(queue.queue()[0], job_low.job_id)

    def test_queue_submit_time_sort(self):
        """Sort jobs by submission time ascending"""
        # Create two jobs with artificial timestamps
        job1 = Job([self.filea3])
        job1.submit_time = job1.submit_time - timedelta(seconds=20)  # simulate earlier submission
        job2 = Job([self.filea2])

        queue = JobQueue([job2, job1])
        self.assertIs(queue.queue()[1], job1.job_id)
        self.assertIs(queue.queue()[0], job2.job_id)

    def test_queue_time_and_priority_sort(self):
        """Sort jobs by submission time ascending"""
        # Create two jobs with artificial timestamps
        job1 = Job([self.filea3], priority=Priority.LOW)
        job1.submit_time = job1.submit_time - timedelta(seconds=20)  # simulate earlier submission
        job2 = Job([self.filea2], priority=Priority.HIGH)
        job2.submit_time = job2.submit_time - timedelta(seconds=10)  # simulate earlier submission
        job3 = Job([self.filea1])
        job4 = Job([self.filea4], priority=Priority.HIGH)

        queue = JobQueue([job1, job2, job3, job4])
        self.assertIs(queue.queue()[3], job2.job_id)
        self.assertIs(queue.queue()[2], job4.job_id)
        self.assertIs(queue.queue()[1], job3.job_id)
        self.assertIs(queue.queue()[0], job1.job_id)


if __name__ == "__main__":
    unittest.main()
