import json

def filter_repos_by_stars_and_forks(input_file, output_file):
    with open(input_file, 'r') as f:
        repos = json.load(f)
    
    filtered_repos = []
    for repo in repos:
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        if stars >= 100 or forks >= 100:
            filtered_repos.append(repo)
    
    # Save filtered repos to the output file
    with open(output_file, 'w') as f:
        json.dump(filtered_repos, f, indent=4)
    
    print(f"Filtered to {len(filtered_repos)} repositories with more than 100 stars or forks.")

if __name__ == "__main__":
    filter_repos_by_stars_and_forks('bioinformatics_repos.json', 'filtered_bioinformatics_repos.json')