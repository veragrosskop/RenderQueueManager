# Render Queue Manager

This application consists of several modules.

- file_parser.py -> Parses file sequences for missing frames.
- job_queue.py -> Queues job for processing on a server according to their priorities.
- logger.py -> contains logging formatting for console and file logging.
- server.py -> simulates a server with multiple workers that process jobs in the queue in parallel.
- main.py -> generates the sample data and processes the tasks on the server.


## Run instructions
1. clone the git repository
2. run main.py
   - sample_data, logs and jobs directories will be created under src/.
3. Additional test_files are included under tests/