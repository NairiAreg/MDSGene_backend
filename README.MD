## Running with Docker

This project can be run using Docker and Docker Compose for easier setup and consistent environments.

### Prerequisites

1.  **Docker Desktop:** Install Docker Desktop for your OS ([https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)).
2.  **Ollama Models (Initial Pull):** While the Ollama service will run in Docker, you need to pull the models *once* after starting the Ollama container.

### Setup

1.  **Clone the repository (if not already done):**
    ```bash
    git clone <your-repo-url>
    cd qc_project
    ```

2.  **Create Environment File for Docker:**
    Copy the example `.env.docker.example` (you'll create this from the content below) to `.env.docker` in the project root and fill in your `GEMINI_API_KEY`:
    ```env
    # Filename: .env.docker
    OLLAMA_BASE_URL=http://ollama:11434
    AI_PROCESSOR_SERVICE_URL=http://ai-processor:8001
    VECTOR_STORE_SERVICE_URL=http://vector-store:8002
    GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
    GEMINI_MODEL="gemini-1.5-pro-preview-03-25"
    EMBEDDING_MODEL_NAME="mxbai-embed-large"
    TIMEOUT_EMBEDDING_SECONDS=60
    CHUNK_SIZE=500
    CHUNK_OVERLAP=100
    USE_VECTOR_STORE=true
    EXCEL_FOLDER=excel
    PROPERTIES_DIR=properties
    TEMP_UPLOAD_DIR=temp_uploads
    VECTOR_STORE_PATH=vector_store/faiss_index
    MODEL_SAVE_PATH=Model/RF_model.pkl
    ```

3.  **Create necessary host directories (if they don't exist):**
    These directories will be mounted into the containers.
    ```bash
    mkdir -p excel properties temp_uploads vector_store/faiss_index cache .questions Model
    ```
    (On Windows, use `mkdir` equivalent in PowerShell or Command Prompt)

### Building and Running

1.  **Build and Start Services:**
    From the project root (`D:\QualityControl\qc_project`), run:
    ```bash
    docker compose up --build -d
    ```
    This will build the Python application image and start all services (Ollama, Vector Store, AI Processor, Main App) in detached mode.

2.  **Pull Ollama Models (First Time Only):**
    After the services are up (especially `ollama_service`), open a new terminal and run:
    ```bash
    docker compose exec ollama ollama pull mxbai-embed-large
    # Add other models if needed, e.g.:
    # docker compose exec ollama ollama pull mistral
    ```
    These models will be stored in a Docker volume (`ollama_data`) and persist.

3.  **Accessing Services:**
    *   **Main Application:** `http://localhost:8000`
    *   **AI Processor Service:** `http://localhost:8001` (Health: `http://localhost:8001/health`)
    *   **Vector Store Service:** `http://localhost:8002` (Health: `http://localhost:8002/health`)
    *   **Ollama API:** `http://localhost:11434` (accessible from your host for direct interaction if needed)

4.  **Viewing Logs:**
    ```bash
    docker compose logs -f # View logs for all services
    docker compose logs -f main-app # View logs for a specific service
    ```

5.  **Stopping Services:**
    ```bash
    docker compose down
    ```
    To remove volumes (like Ollama models, vector store data - use with caution):
    ```bash
    docker compose down -v
    ```

### Health Checks

*   Main App: `http://localhost:8000/health` (You'll need to add this endpoint to `main.py`)
*   AI Processor: `http://localhost:8001/health`
*   Vector Store: `http://localhost:8002/health`