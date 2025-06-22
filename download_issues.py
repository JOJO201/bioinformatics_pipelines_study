import requests
import json
import os
from tqdm import tqdm

# GitHub personal access token (use one if you have rate limits to avoid restrictions)
GITHUB_TOKEN = ""
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}"
}

# Load JSON file containing repositories
with open("classified_bioinformatics_pipelines.json", "r") as f:
    repos = json.load(f)

# Create a directory for storing issues
os.makedirs("github_issues", exist_ok=True)

def fetch_issues(repo_full_name):
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo_full_name}/issues"
        params = {"state": "all", "per_page": 100, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch issues for {repo_full_name}: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        issues.extend(data)
        page += 1
    return issues

# Iterate through the repositories and fetch issues
for repo in tqdm(repos, desc="Fetching issues"):
    repo_full_name = repo["full_name"]
    print(f"Fetching issues for {repo_full_name}")
    issues = fetch_issues(repo_full_name)
    if issues:
        # Save issues to a file
        with open(f"github_issues/{repo['name']}_issues.json", "w") as f:
            json.dump(issues, f, indent=2)
        print(f"Saved {len(issues)} issues for {repo_full_name}.")
    else:
        print(f"No issues found for {repo_full_name}.")

print("Done fetching GitHub issues.")
