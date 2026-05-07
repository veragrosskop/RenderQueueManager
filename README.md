# 📦 Render Queue Manager

A Python-based render queue and file sequence management system designed to simulate and automate a production-style render pipeline.  

The system parses rendered image sequences, detects missing frames, and processes jobs asynchronously using a threaded job queue.

---

# 🚀 Overview & Architecture

This project simulates a lightweight render farm pipeline with the following modular components:

- **File Parser** → Detects and validates image sequences  
- **Job Queue** → Manages job scheduling and prioritization  
- **Server** → Executes jobs concurrently  
- **Logger** → Tracks system activity and debugging information  
- **Main** → Orchestrates full workflow and initializes test data generation
- **Tests** → Additional automated testing with PyTest

This separation allows each system to be extended independently (e.g. swapping queue logic, adding real render execution, or integrating a GUI).

---

## 🛠️ Tech Stack

- Python
- Threading / ThreadPoolExecutor
- heapq (priority queue)
- Regex (file parsing)
- JSON (job reporting)
---
## ⚙️ More in Depth Features

### 📁 File Sequence Management
- Parses image sequences from directories (e.g. `render_1001.png`)
- Supports multiple sequences per folder
- Extracts metadata (name, frame, extension)
- Detects missing frames in sequences
- Generates structured validation reports

### 🧠 Job Queue System
- Priority-based job scheduling (LOW / MEDIUM / HIGH)
- Thread-safe queue implementation using a heap structure
- Job lifecycle tracking (QUEUED → PROCESSING → FINISHED / ERROR)
- Unique job ID generation and tracking

### 🖥️ Render Server
- Multithreaded execution using `ThreadPoolExecutor`
- Concurrent job processing
- Automatic job status updates
- Error handling with structured reporting
- Simulated render execution pipeline

### 📊 Logging System
- File + console logging separation
- Timestamped logs per component (Server, Worker, Queue)
- Organized log directories per session

# ⚙️ Setting up the project

## What happens when you run main.py ?
- Sample render sequences are generated automatically
- File sequences are parsed and validated
- Missing frames are detected and reported
- Jobs are created per sequence
- Jobs are submitted to a priority queue
- A threaded server processes jobs concurrently
- Job status reports are written to disk
- Logs are generated for debugging and monitoring

#### 1. Clone the repository
```bash
git clone https://github.com/veragrosskop/RenderQueueManager.git
cd RenderQueueManager
```
#### 2. Run the application
```bash
python main.py
```
---

## 🧩 Future Improvements

- More extensive naming conventions
- GUI-based queue monitoring tool
- Distributed render nodes (networked execution)
- Persistent database-backed job tracking
- Plugin system for custom job types
- Integration with real render engines (Blender/Houdini)
- Advanced scheduling policies (fair queue, deadline-based execution)

> 💡This project was made as a stand alone, but could be integrated into my more extensive pipeline project.
> Check out the repo under: https://github.com/veragrosskop/pipeline

---

>## 📎 Notes
>This project is intended as a learning and simulation environment for production pipeline systems used in VFX and animation studios. It focuses on architecture, concurrency, and automation rather than actual rendering.

---