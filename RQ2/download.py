import requests
import time

GITHUB_API_URL = "https://api.github.com/search/repositories"
GITHUB_API_TOKEN = ""  # Replace with your GitHub API token

def search_bioinformatics_repos():
    query = "bioinformatics"  # You can modify this query if needed
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}
    repos = []
    
    page = 1
    while True:
        # GitHub API search request
        params = {
            "q": f"topic:{query}",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching data from GitHub: {response.status_code}")
            break

        data = response.json()
        repos += data.get("items", [])
        
        # Break if there are no more repositories
        if "items" not in data or len(data["items"]) == 0:
            break
        
        page += 1
        time.sleep(1)  # Respect GitHub API rate limits

    return repos

if __name__ == "__main__":
    repositories = search_bioinformatics_repos()
    print(f"Found {len(repositories)} repositories tagged with 'bioinformatics'.")
    # Optionally, save the results to a file for later steps
    # Example: save repositories to a file for later processing
    with open('bioinformatics_repos.json', 'w') as f:
        import json
        json.dump(repositories, f, indent=4)