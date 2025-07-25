import requests
import re
import time

def get_post_ids_for_keyword(keyword, max_pages=10, delay=2, output_file='post_ids.txt'):
    all_post_ids = set()  # Using a set to store unique post IDs
    page = 1

    while True:
        # Construct the URL for the current page of search results
        search_url = f"https://www.biostars.org/post/search/?query={keyword}&page={page}&order=relevance"
        print(f"Fetching page {page} for keyword '{keyword}'...")

        # Fetch the page content
        response = requests.get(search_url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}, status code: {response.status_code}")
            break

        # Use regex to find all occurrences of /p/[0-9]+/ (post URLs)
        post_urls = re.findall(r'/p/([0-9]+)/', response.text)[:50]  # Extract only the numeric post IDs
        
        # If no post IDs were found, we've likely reached the last page
        if not post_urls:
            print("No more posts found, stopping search.")
            break

        # Add the found post IDs to the set (automatically removes duplicates)
        all_post_ids.update(post_urls)

        # Rest for a specified amount of time before fetching the next page
        print(f"Sleeping for {delay} seconds...")
        time.sleep(delay)

        # Move to the next page
        page += 1

        # Stop if we've reached the maximum number of pages to search
        if page > max_pages:
            print(f"Reached the maximum number of pages ({max_pages}).")
            break

    # Save the post IDs to the output file
    with open(output_file, 'a') as f:
        for post_id in all_post_ids:
            f.write(f"{post_id}\n")

    print(f"Saved {len(all_post_ids)} unique post IDs to {output_file}")

if __name__ == "__main__":
    # Example usage for the keyword 'pipeline'
    keyword = 'workflow'
    get_post_ids_for_keyword(keyword, max_pages=53, delay=2, output_file='wkf_post_ids.txt')