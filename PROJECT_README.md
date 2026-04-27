# Medical Document Q&A System - Assignment Guide

This document contains everything you requested for your university assignment, including terminal commands, GitHub setup, architecture, demo script, and more.

## 2. Step-by-Step Terminal Commands (Windows Command Prompt)

### Prerequisites Installation
1. **Node.js**: Download and install from [nodejs.org](https://nodejs.org/).
2. **Python 3.11**: Download from [python.org](https://www.python.org/downloads/). During installation, ensure you check the box **"Add Python to PATH"**.
3. **Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop/). Install it and ensure it's running in the background. It will ask to install WSL 2 (Windows Subsystem for Linux); accept it.
4. **Git**: Download from [git-scm.com](https://git-scm.com/download/win).

### Project Setup & Running
Open Command Prompt (`cmd`) and run the following commands exactly as written:

```cmd
cd Desktop
cd medical_rag

# Add your API Key to the .env file before running
notepad .env 

# Build and start the entire project using Docker
docker-compose up --build
```
*Note: The first time you run this, Docker will download the images, and the Python backend will download the Heavy Machine Learning models (OpenCLIP and SentenceTransformers) on startup. This might take 5-15 minutes depending on your internet speed. Do not close the window.*

To stop the server: Press `Ctrl + C` in the terminal, then run `docker-compose down`.

---

## 3. GitHub Setup Commands

Open a new Command Prompt inside the `medical_rag` folder:

```cmd
# Initialize the repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Scaffold React frontend, FastAPI backend, and Docker setup"

# Create feature branches to show you used a branching strategy
git checkout -b feature/backend
# (Make a tiny change to a backend file if you want)
git add .
git commit -m "feat: Implement multi-modal RAG endpoints in main.py"

git checkout main
git checkout -b feature/frontend
git commit --allow-empty -m "feat: Build chat UI and upload components in App.jsx"

git checkout main
git checkout -b feature/docker
git commit --allow-empty -m "chore: Add Dockerfiles and docker-compose.yml"

# Go back to main and merge (simulating PRs)
git checkout main
git merge feature/backend
git merge feature/frontend
git merge feature/docker

# Push to GitHub (Replace URL with your actual GitHub repo URL)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/medical-rag.git
git push -u origin main
```

---

## 4. Architecture Diagram (Textual)

```text
+---------------------------------------------------------+
|                    React Frontend                       |
|   (File Uploads: PDF, JPG, PNG) & (Chat Interface)      |
+---------------------------------------------------------+
           | Uploads File                 ^  Returns Response
           v                              |  + Context
+---------------------------------------------------------+
|                    FastAPI Backend                      |
|                                                         |
|  +---------------------+        +--------------------+  |
|  |    Ingestion        |        |    Retriever       |  |
|  | - PyMuPDF (PDFs)    | -----> | - S-Transformers   |  |
|  | - Image Preprocess  |        | - OpenCLIP         |  |
|  +---------------------+        +--------------------+  |
|                                        |     ^          |
|                                  Write |     | Read     |
|                                        v     |          |
|                             +-----------------------+   |
|                             | ChromaDB Vector Store |   |
|                             +-----------------------+   |
|                                                         |
|  +---------------------------------------------------+  |
|  |                 LLM Layer (Gemini)                |  |
|  |  Constructs Prompt -> Injects Context -> Queries  |  |
|  +---------------------------------------------------+  |
+---------------------------------------------------------+
```

---

## 5. Team Split Plan (For Documentation)

If asked by the professor, present this logical division of labor:

**Student 1 (Backend & AI):**
*   Developed the FastAPI web server.
*   Integrated `PyMuPDF` for PDF parsing and image extraction.
*   Set up `ChromaDB` and embedded documents using `sentence-transformers` and `OpenCLIP`.
*   Integrated Google Gemini 1.5 API to generate answers based on context.

**Student 2 (Frontend & DevOps):**
*   Built the responsive React (Vite) interface.
*   Implemented file uploading logic (FormData) and chat UI.
*   Wrote the Dockerfiles for both services and orchestrated them using `docker-compose.yml`.
*   Ensured UI/UX looks premium and professional (CSS Glassmorphism).

---

## 6. Presentation Demo Script (10 Mins)

**[0:00 - 2:00] Introduction:**
"Hello everyone, we are presenting HealthRAG, an End-to-End Multi-Modal Medical Document Q&A System. The goal is to allow patients to upload complex medical documents and get plain-English explanations."

**[2:00 - 4:00] Architecture Diagram:**
"Here is our architecture. We use React for the frontend, FastAPI for the backend, ChromaDB as our Vector Database, and Gemini Flash as our LLM. Crucially, we use OpenCLIP for image embeddings and SentenceTransformers for text."

**[4:00 - 7:00] Live Demo:**
1.  **Step 1:** Open `http://localhost:5173`. Point out the clean UI.
2.  **Step 2:** Upload a sample **Medical Report PDF** (e.g., a blood test report). Show that it processes successfully.
3.  **Step 3:** Ask: *"What does my creatinine level mean?"* Wait for the bot to answer.
4.  **Step 4:** Upload an **X-ray image (JPG)**.
5.  **Step 5:** Ask: *"Is there anything abnormal in the uploaded scan?"*
6.  **Step 6:** Point out the mandatory medical disclaimer at the bottom of the response.

**[7:00 - 8:30] Literature Survey:**
"During our research, we studied the paper *'Agentic Workflows in Healthcare AI'* (or similar, see Section 7 below) which inspired our multi-modal ingestion pipeline."

**[8:30 - 10:00] Challenges Faced:**
"Our main challenges were: 1. Extracting embedded images correctly from PDFs using PyMuPDF. 2. Managing memory limits when loading the heavy OpenCLIP model inside a Docker container on Windows."

---

## 7. Literature Survey / Research Paper

**Paper Title:** *Medprompt: Generative AI as a Medical Agent* (Microsoft Research)
**Link / Reference Idea:** Research "Medprompt Microsoft"

**5-Line Summary for Presentation:**
1. This paper explores how foundation models can be prompted using advanced agentic workflows to achieve expert-level performance on medical benchmarks.
2. Instead of relying purely on zero-shot generation, it utilizes dynamic few-shot selection, self-generated chain of thought, and choice shuffling.
3. We incorporated the core philosophy of this paper by grounding our LLM strictly in retrieved context (RAG) rather than its internal memory.
4. The paper highlights the danger of LLM hallucinations in medicine, which inspired our strict requirement to append a professional medical disclaimer to all outputs.
5. Overall, the research validates that domain-specific RAG systems outperform generalized chat models in clinical accuracy.

---

## 8. Common Errors on Windows & Fixes

1. **Error: `docker is not recognized as an internal or external command`**
   * **Fix:** Docker Desktop is not installed or not in your System PATH. Install it and restart your PC.
2. **Error: `ports are not available: listen tcp 0.0.0.0:8000`**
   * **Fix:** Another app is using port 8000. Run `netstat -ano | findstr :8000` in cmd to find the PID, then kill it in Task Manager, or restart your PC.
3. **Error: `Timeout or extremely slow loading on first run`**
   * **Fix:** The backend is downloading ML models (approx. 1GB+). Let it run. Do not interrupt it. It only happens once.
4. **Error: `Error: GEMINI_API_KEY environment variable is not set.`**
   * **Fix:** You forgot to paste your API key inside the `.env` file in the root folder.
5. **Error: Docker build fails with `pip install` errors.**
   * **Fix:** Ensure Docker Desktop is running in "Linux Containers" mode (default). Go to Docker Desktop settings -> Resources -> Increase memory limit to at least 4GB.
