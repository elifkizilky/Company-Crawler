# Company-Crawling

This repository contains the source code for data crawling study, which includes a multi-stage process to fetch, analyze, and serve enterprise and startup data using FastAPI, Celery, and Redis within a Dockerized environment.

## Getting Started

### Prerequisites
Ensure you have the following installed on your system:
- Docker
- Docker Compose
- Python (if running scripts locally outside Docker)

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/elifkizilky/Company-Crawling.git
   cd your-repository-directory
2. **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
This command builds the Docker images for the FastAPI server, Celery worker, and Redis, and starts the containers.

### Usage

1. **First Phase: Data Fetching**

Run the first phase script to fetch initial corporate data:

    python first_phase.py

This script saves the fetched data to _top_ranked_corporates.json_.

2. **Second Phase: Data Processing with Celery**

Ensure Redis and Celery are running:

    ./start_redis.sh  # Starts the Redis server
    ./start_celery.sh  # Starts the Celery worker

Execute the second phase script to fetch data for all companies:
    
    python second_phase.py

This will create a JSON file _results_data_second_phase.json_ containing data for 848 companies.

3. **Third Phase: FastAPI Server**
Ensure docker is running:

    docker-compose up --build

The FastAPI server can be accessed at http://127.0.0.1:8000 after starting the Docker containers. Use the following API endpoints:

- POST /trigger-data-fetch/:
Triggers the data fetching and analysis operation. Returns a task ID.

    curl -X POST "http://127.0.0.1:8000/trigger-data-fetch/"

- GET /task-status/{task_id}:
Retrieves the status of the data fetching and analysis operation using the provided task ID.

    curl -X GET "http://127.0.0.1:8000/task-status/{task_id}"


