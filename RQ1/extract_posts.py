import requests
import json
import time

def fetch_post_info(post_id):
    """
    Fetches post information from the Biostars API for a given post ID.
    """
    api_url = f"https://www.biostars.org/api/post/{post_id}/"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        try:
            return response.json()  # Return the JSON response if valid
        except ValueError:
            print(f"Error parsing JSON for post ID: {post_id}")
            return None
    else:
        print(f"Failed to retrieve post {post_id}, status code: {response.status_code}")
        return None

def collect_post_info_from_list(post_ids, output_folder, delay=2):
    """
    Takes a list of post IDs, fetches post information for each ID using the Biostars API,
    and saves each post's data individually into separate JSON files.
    
    Adds a rest time between each API request to avoid overwhelming the server.
    """
    for post_id in post_ids:
        print(f"Fetching data for post ID: {post_id}")
        post_data = fetch_post_info(post_id)
        
        if post_data:
            # Save each post data into its own file, named with the post ID
            output_file = f"{output_folder}/post_{post_id}.json"
            with open(output_file, 'w') as f:
                json.dump(post_data, f, indent=4)  # Save as pretty-printed JSON
            print(f"Saved post {post_id} to {output_file}")
        else:
            print(f"Failed to fetch data for post ID: {post_id}")

        # Rest for a specified delay before making the next request
        print(f"Resting for {delay} seconds before the next request...")
        time.sleep(delay)

def get_post_ids_from_file(input_file):
    """
    Reads post IDs from a file and returns them as a list.
    """
    with open(input_file, 'r') as f:
        post_ids = [line.strip() for line in f.readlines()]  # Strip any surrounding whitespace/newlines
    return post_ids

if __name__ == "__main__":
    # Extract post IDs from the text file
    input_file = 'wkf_post_ids.txt'  # File with collected post IDs
    post_ids = get_post_ids_from_file(input_file)  # Extract IDs into a list

    # Specify the folder where each post will be saved as a JSON file
    output_folder = 'wkf_posts'  # Folder to save each individual post

    # Call the function with the extracted post IDs and a delay of 2 seconds between requests
    collect_post_info_from_list(post_ids, output_folder, delay=2)  # Set delay to 2 seconds
