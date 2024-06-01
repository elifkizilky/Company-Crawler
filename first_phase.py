import requests
import json

api_url = "https://ranking.glassdollar.com/graphql"

query = """
query TopRankedCorporates {
  topRankedCorporates {
    id
    name
    description
    logo_url
    hq_city
    hq_country
    website_url
    linkedin_url
    twitter_url
    startup_partners_count
    industry
    startup_partners {
      company_name
      logo_url: logo
      city
      website
      country
      theme_gd
      __typename   
    }
    startup_friendly_badge
    __typename
  }
}
"""

response = requests.post(
    api_url,
    json={"query": query},
)

if response.status_code == 200:
    data = response.json()
    with open("./top_ranked_corporates.json", "w") as f:
        json.dump(data, f, indent=4)
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
