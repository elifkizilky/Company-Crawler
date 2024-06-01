# Entrapeer Case Study
## Before Start
I recommend using the following command to install all the necessary libraries:

    pip install -r requirements.txt

to install all the necessary libraries

## First Phase
During this phase, I analyzed the corresponding website, GlassDollar, and inspected the network activity in the browser's developer tools to identify the required API. I discovered the GraphQL endpoint at [link](https://ranking.glassdollar.com/graphql)  and consulted the documentation and schema to accomplish the task. The related code can be found in the file named _first_phase.py_. The response data is saved to a JSON file named _top_ranked_corporates.json_. To execute this phase, run the following command:

    python first_phase.py
and this will create the top_ranked_corporates.json file.

## Second Phase
In this phase, I established a Celery app using Redis as the message broker and configured a result backend for tracking purposes. The _fetch_corporate_page_ function in the _celery_tasks.py_ file performs the main task of fetching data for a page using the required variables and query from the GraphQL API. To retrieve data for all companies, you can execute the _second_phase.py_ file. This script generates a JSON file named _results_data_second_phase.json_ containing data for 848 companies. Please note that the second phase does not include the analysis part. The analysis is performed separately in the _analysis_operation.py_ file, which will be discussed in the next section. To run the second phase, follow these steps:

    ./start_redis.sh  #to start the redis server
    ./start_celery.sh  #to start the celery
    python second_phase.py

## Analysis Operation
Initially, I verified the suitability of the data for transformation tasks. Then, utilizing the hq_country, startup_partners_count, and startup_friendly_badge fields, I applied K-means clustering to create 24 clusters. Subsequently, I calculated the Silhouette Score (~0.75) to evaluate the meaningfulness of the clusters. Additionally, I generated PCA and t-SNE plots for detailed cluster representation and saved them to the output directory within folders corresponding to their respective task_id. Also, I plot the number of companies in each cluster under the name cluster_count_plot. Finally, I utilized Google Gemini to assign descriptions and titles to each cluster.

## Third Phase
In this phase, I developed a FastAPI server and implemented one POST API (trigger_data_fetch) to initiate the data fetch and analysis operation, and one GET API (get_task_status) to retrieve the status of a specific task. Upon completion of the trigger_data_fetch function, the output of the analysis is stored in the output directory under a folder named after the corresponding task_id, in PDF, HTML, CSV, and TXT formats. The POST API returns the task_id to enable users to check the task status using the GET API.

To start the FastAPI:
      
      uvicorn third_phase:app --host 0.0.0.0 --port 8000 --reload
To try the POST API:

    curl -X POST "http://127.0.0.1:8000/trigger-data-fetch/"

To try the GET API:

    curl -X GET "http://127.0.0.1:8000/task-status/{task_id}"

