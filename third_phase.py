from fastapi import FastAPI, BackgroundTasks, HTTPException
from celery.result import AsyncResult
import os
import pandas as pd
import json
from uuid import uuid4
from celery import group
import json
import config
import supplementary_functions
import celery_tasks
import analysis_operation


# Create the FastAPI app
app = FastAPI()

# Dictionary to track task status
task_status = {}


# Function to check Celery task completion and trigger the analysis
def check_task_completion_and_start_analysis(task_id, async_result):
    async_result.join()

    # Collect the data from Celery tasks
    results_data = [result.result["data"]["corporates"]["rows"] for result in async_result if result.successful()]
    flattened_results = [item for sublist in results_data for item in sublist]

    # Define fields to drop
    fields_to_drop = ["logo_url", "website_url", "linkedin_url", "twitter_url", "industry"]

    # Clean the data by dropping unnecessary fields
    data_cleaned = [{k: v for k, v in item.items() if k not in fields_to_drop} for item in flattened_results]

    # Convert to a DataFrame
    df = pd.DataFrame(data_cleaned)

    # Start the analysis function with the cleaned data
    analysis_result = analysis_operation.analyze_crawled_data(df, task_id) 
    print("Analysis result:", analysis_result)
    # Update task status
    task_status[task_id] = {
        "status": "completed",
        "result": analysis_result,
        "celery_id": async_result.id
    }
    # Save the cleaned data to a JSON file
    with open("./results_data.json", "w") as f:
        json.dump(data_cleaned, f, indent=4)


# Endpoint to trigger the data fetching operation
@app.post("/trigger-data-fetch/")
async def trigger_data_fetch(background_tasks: BackgroundTasks):
    # Create a unique task ID
    task_id = str(uuid4())
    
    # Define a group of Celery tasks to fetch data for pages 1 through 27
    crawl_tasks = group(celery_tasks.fetch_corporate_page.s(page) for page in range(1, 28))
    
    # Trigger the group of tasks asynchronously
    async_result = crawl_tasks.apply_async()

    # Store the task ID and the Celery result for tracking
    task_status[task_id] = {
        "status": "in_progress",
        "result": None,
        "celery_id": async_result.id
    }

    # Add a background task to trigger the analysis when the Celery tasks complete
    background_tasks.add_task(check_task_completion_and_start_analysis, task_id, async_result)

    return {"task_id": task_id, "message": "Data fetching started. Check back later for results."}


# Endpoint to check the status of a task
@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_status[task_id]

    if task["status"] == "in_progress":
        return {"status": "in_progress", "message": "Data fetching and analysis in progress. Check back later."}

    return {"status": task["status"], "result": task["result"], "celery_id": task["celery_id"]}

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
