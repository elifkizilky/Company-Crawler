from celery_tasks import app, fetch_corporate_page
from celery import group
import json

# Define a group of tasks to fetch data for pages 1 through 27
crawl_tasks = group(fetch_corporate_page.s(page) for page in range(1, 28))

# Apply the group of tasks asynchronously to execute in parallel
crawl_results = crawl_tasks.apply_async()

# Wait for all crawl tasks to complete
crawl_results.join()  # This blocks until all tasks are complete
results_data = [result.result["data"]["corporates"]["rows"] for result in crawl_results if result.successful()]
flattened_results = [item for sublist in results_data for item in sublist]

with open("./results_data_second_phase.json", "w") as f:
        json.dump(flattened_results, f, indent=4)


print("All crawl tasks completed successfully! The length of the flattened results is:", len(flattened_results))
