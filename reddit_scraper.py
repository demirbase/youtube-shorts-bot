# reddit_scraper.py
# Fetches top posts from a subreddit and ensures no duplicates are used.

import requests
import os

USED_POSTS_FILE = "used_posts.txt"

def get_top_reddit_post(subreddit: str) -> dict | None:
    """
    Fetches the top post from a subreddit that hasn't been used before.
    
    Args:
        subreddit: The name of the subreddit (e.g., "AskReddit").

    Returns:
        A dictionary containing post details or None if no new post is found.
    """
    print(f"Scraping r/{subreddit} for new top posts...")
    
    # Define a user-agent to avoid potential 429 errors from default 'requests' agent
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    # Construct the .json URL
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=20&t=day"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Load the set of used post IDs
        if not os.path.exists(USED_POSTS_FILE):
            open(USED_POSTS_FILE, 'w').close()
            
        with open(USED_POSTS_FILE, 'r') as f:
            used_post_ids = set(line.strip() for line in f)

        # Find the first post that is not in our used_post_ids set
        for post in data['data']['children']:
            post_data = post['data']
            post_id = post_data['id']
            is_video = post_data.get('is_video', False)
            is_over_18 = post_data.get('over_18', False)

            # Skip videos, NSFW posts, and posts we've already used
            if post_id not in used_post_ids and not is_video and not is_over_18:
                print(f"Found new post: {post_id} - {post_data['title']}")
                
                # Get the top comments for the post body
                post_url = post_data['url']
                comments_url = f"{post_url.rstrip('/')}.json"
                
                comments_response = requests.get(comments_url, headers=headers)
                comments_response.raise_for_status()
                comments_data = comments_response.json()
                
                # comments_data[0] is the post info, comments_data[1] is the comments
                comments = comments_data[1]['data']['children']
                
                # Concatenate top 3 comments
                post_body = ""
                comment_count = 0
                for comment in comments:
                    if comment['kind'] == 't1' and not comment['data'].get('stickied', False):
                        post_body += comment['data']['body'] + "\n\n"
                        comment_count += 1
                        if comment_count >= 3:  # Limit to top 3 comments
                            break
                
                if not post_body:
                    print(f"Post {post_id} has no text comments. Skipping.")
                    continue

                # Add this post ID to our used list
                with open(USED_POSTS_FILE, 'a') as f:
                    f.write(f"{post_id}\n")

                return {
                    "id": post_id,
                    "title": post_data['title'],
                    "body": post_body,
                    "url": post_url
                }
        
        print("No new, eligible top posts found.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error scraping Reddit: {e}")
        return None
