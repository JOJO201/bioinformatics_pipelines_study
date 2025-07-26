import openai
import json
import time

CHATGPT_API_KEY = ""  # Replace with your OpenAI API key
openai.api_key = CHATGPT_API_KEY

def classify_repos_with_chatgpt(input_file, output_file):
    with open(input_file, 'r') as f:
        repos = json.load(f)
    
    classified_repos = []
    
    for repo in repos:
        description = repo.get("description", "")
        if not description:
            continue
        
        # ChatGPT API call to classify the repository
        prompt = (
            f"Here is a description of a bioinformatics repository: {description}.\n\n"
            "Does this repository represent a complete bioinformatics workflow pipeline? "
            "Answer 'yes' if it is a full pipeline, and 'no' if it is a library, framework, utility, or educational repository."
        )
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )
            
            classification = response['choices'][0]['message']['content'].strip().lower()
            
            if "yes" in classification:
                classified_repos.append(repo)
        
        except Exception as e:
            print(f"Error classifying repo {repo['name']}: {e}")
        
        # Sleep between API calls to avoid hitting rate limits
        time.sleep(1)
    
    # Save classified full pipelines to output file
    with open(output_file, 'w') as f:
        json.dump(classified_repos, f, indent=4)
    
    print(f"Identified {len(classified_repos)} repositories as full pipelines.")

if __name__ == "__main__":
    classify_repos_with_chatgpt('filtered_bioinformatics_repos.json', 'classified_bioinformatics_pipelines.json')