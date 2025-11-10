# reddit_scraper.py
# Fetches top posts from a subreddit and ensures no duplicates are used.

import requests
import os
import time
import random

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
    
    # Use a more realistic user-agent and additional headers to avoid blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    # Construct the .json URL
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=20&t=day"

    try:
        # Add a small random delay to appear more human-like
        time.sleep(random.uniform(1, 3))
        
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 403:
            print("⚠️ Reddit blocked the request (403 Forbidden)")
            print("This is expected when using GitHub Actions runners.")
            print("Trying alternative method: old.reddit.com...")
            
            # Try old.reddit.com as fallback
            alt_url = f"https://old.reddit.com/r/{subreddit}/top.json?limit=20&t=day"
            time.sleep(random.uniform(2, 4))
            response = requests.get(alt_url, headers=headers, timeout=15)
            print(f"Alternative attempt status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch from Reddit. Status: {response.status_code}")
            print(f"Response preview: {response.text[:500]}")
            return None
            
        response.raise_for_status()
        data = response.json()
        
        # Debug: Print how many posts were fetched
        posts_count = len(data.get('data', {}).get('children', []))
        print(f"✅ Successfully fetched {posts_count} posts from Reddit")

        # Load the set of used post IDs
        if not os.path.exists(USED_POSTS_FILE):
            open(USED_POSTS_FILE, 'w').close()
            
        with open(USED_POSTS_FILE, 'r') as f:
            used_post_ids = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        
        print(f"📝 Already used {len(used_post_ids)} posts")

        # Find the first post that is not in our used_post_ids set
        for post in data['data']['children']:
            post_data = post['data']
            post_id = post_data['id']
            is_video = post_data.get('is_video', False)
            is_over_18 = post_data.get('over_18', False)
            
            print(f"  Checking post {post_id}: video={is_video}, nsfw={is_over_18}, used={post_id in used_post_ids}")

            # Skip videos, NSFW posts, and posts we've already used
            if post_id not in used_post_ids and not is_video and not is_over_18:
                print(f"✅ Found new post: {post_id}")
                print(f"   Title: {post_data['title'][:80]}...")
                
                # Get the top comments for the post body
                post_url = post_data['url']
                comments_url = f"{post_url.rstrip('/')}.json"
                
                print(f"   Fetching comments...")
                time.sleep(random.uniform(1, 2))  # Rate limiting
                
                comments_response = requests.get(comments_url, headers=headers, timeout=15)
                
                if comments_response.status_code != 200:
                    print(f"   ⚠️ Failed to fetch comments (status {comments_response.status_code}). Skipping post.")
                    continue
                    
                comments_response.raise_for_status()
                comments_data = comments_response.json()
                
                # comments_data[0] is the post info, comments_data[1] is the comments
                comments = comments_data[1]['data']['children']
                
                # Concatenate top 3 comments
                post_body = ""
                comment_count = 0
                for comment in comments:
                    if comment['kind'] == 't1' and not comment['data'].get('stickied', False):
                        comment_text = comment['data']['body']
                        # Skip very short comments
                        if len(comment_text) > 20:
                            post_body += comment_text + "\n\n"
                            comment_count += 1
                            if comment_count >= 3:  # Limit to top 3 comments
                                break
                
                if not post_body:
                    print(f"   ⚠️ Post {post_id} has no substantial text comments. Skipping.")
                    continue

                print(f"   ✅ Successfully scraped post with {comment_count} comments")

                # Add this post ID to our used list
                with open(USED_POSTS_FILE, 'a') as f:
                    f.write(f"{post_id}\n")

                return {
                    "id": post_id,
                    "title": post_data['title'],
                    "body": post_body,
                    "url": post_url
                }
        
        print("⚠️ No new, eligible top posts found.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping Reddit: {e}")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None
