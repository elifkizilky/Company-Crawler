import requests
from celery import Celery, group

# Set up the Celery app with Redis as the message broker
app = Celery("enterprise_crawler", broker="redis://127.0.0.1:6379/0")

# Configure the result backend if you want to track task results
app.conf.result_backend = "redis://127.0.0.1:6379/0"

# Define the Celery task to fetch corporate data
@app.task
def fetch_corporate_page(page):
    query = """
    query Corporates($page: Int, $filters: CorporateFilters, $sortBy: String) {
      corporates(page: $page, filters: $filters, sortBy: $sortBy) {
        rows {
          id
          name
          description
          logo_url
          website_url
          linkedin_url
          twitter_url
          industry
          hq_city
          hq_country
          startup_friendly_badge
          startup_partners_count
        }
        count
      }
    }
    """
    
    variables = {"page": page, "filters": {"industry": [], "hq_city": []}}

    response = requests.post("https://ranking.glassdollar.com/graphql", json={"query": query, "variables": variables})

    if response.status_code == 200:
        data = response.json()
        print(f"Fetched data for page {page}", data.get("data", "No data found").get("corporates", {}).get("count"))
        return data  # You can return the fetched data for further analysis
    else:
        raise Exception(f"Failed to fetch data for page {page}. HTTP status code: {response.status_code}")

