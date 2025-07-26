import requests
import json
import os
from tqdm import tqdm

# Load the classified_bioinformatics_pipelines.json file
with open('classified_bioinformatics_pipelines.json') as f:
    pipelines = json.load(f)

# Define a function to download the repositories
def download_repo(repo_url, save_path):
    """Clone the repository from the given URL into the specified path."""
    os.system(f'git clone {repo_url} {save_path}')

# Create directories to store repositories and metadata
if not os.path.exists('bioinformatics_pipelines'):
    os.makedirs('bioinformatics_pipelines')

# Iterate over each project and download the repository and metadata
for project in tqdm(pipelines):
    project_name = project['name']
    repo_url = project['clone_url']
    save_path = os.path.join('bioinformatics_pipelines', project_name)

    # Skip already downloaded repositories
    if not os.path.exists(save_path):
        print(f'Downloading repository: {project_name}')
        download_repo(repo_url, save_path)
    
    # Save metadata
    metadata_path = os.path.join(save_path, 'metadata.json')
    with open(metadata_path, 'w') as metadata_file:
        json.dump(project, metadata_file, indent=4)

print('All repositories and metadata downloaded.')