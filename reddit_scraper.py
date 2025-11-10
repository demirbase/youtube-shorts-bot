# reddit_scraper.py
# Fetches top posts from a subreddit and ensures no duplicates are used.

import os
import praw

USED_POSTS_FILE = "used_posts.txt"

def get_top_reddit_post(subreddit: str) -> dict | None:
    """
    Fetches the top post from a subreddit that hasn't been used before.
    Uses Reddit's official API (PRAW) for reliable, authenticated access.
    
    Args:
        subreddit: The name of the subreddit (e.g., "AskReddit").

    Returns:
        A dictionary containing post details or None if no new post is found.
    """
    print(f"🔍 Fetching top posts from r/{subreddit} using Reddit API...")
    
    try:
        # Get credentials from environment and strip any whitespace
        client_id = os.environ.get('REDDIT_CLIENT_ID', '').strip()
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET', '').strip()
        username = os.environ.get('REDDIT_USERNAME', '').strip()
        password = os.environ.get('REDDIT_PASSWORD', '').strip()
        
        # Debug: Check if credentials are loaded (without revealing values)
        print(f"🔑 Credential check:")
        print(f"   REDDIT_CLIENT_ID: {'✅ Set (' + str(len(client_id)) + ' chars)' if client_id else '❌ Missing'}")
        print(f"   REDDIT_CLIENT_SECRET: {'✅ Set (' + str(len(client_secret)) + ' chars)' if client_secret else '❌ Missing'}")
        print(f"   REDDIT_USERNAME: {'✅ Set (length: ' + str(len(username)) + ' chars)' if username else '❌ Missing'}")
        if username:
            # Show hex dump of first 20 chars to see hidden characters
            hex_dump = ' '.join(f'{ord(c):02x}' for c in username[:20])
            print(f"   REDDIT_USERNAME (hex): {hex_dump}")
            print(f"   REDDIT_USERNAME should be 'seftalibursa' (13 chars)")
        print(f"   REDDIT_PASSWORD: {'✅ Set (' + str(len(password)) + ' chars)' if password else '❌ Missing'}")
        
        if not all([client_id, client_secret, username, password]):
            print("\n❌ One or more Reddit credentials are missing!")
            print("📖 See REDDIT_API_SETUP.md for setup instructions")
            return None
        
        # Initialize Reddit API client with credentials from environment
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=f'python:reddit-shorts-bot:v2.0 (by /u/{username})',
            username=username,
            password=password
        )
        
        # Test authentication
        print("🔐 Testing Reddit authentication...")
        try:
            reddit.user.me()
            print("✅ Reddit authentication successful!")
        except Exception as auth_err:
            print(f"❌ Reddit authentication failed!")
            print(f"   Error: {str(auth_err)}")
            print("\n🔍 Common causes:")
            print("   1. Wrong Reddit password")
            print("   2. Username includes '/u/' (it shouldn't)")
            print("   3. Client ID or Secret is incorrect")
            print("   4. Reddit app type is not 'script'")
            print("\n💡 Try logging in to https://reddit.com with these credentials to verify")
            return None
        
        # Load the set of used post IDs
        if not os.path.exists(USED_POSTS_FILE):
            open(USED_POSTS_FILE, 'w').close()
            
        with open(USED_POSTS_FILE, 'r') as f:
            used_post_ids = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        
        print(f"📝 Already used {len(used_post_ids)} posts")
        
        # Fetch top posts from the subreddit
        subreddit_obj = reddit.subreddit(subreddit)
        posts_checked = 0
        
        for submission in subreddit_obj.top('day', limit=25):
            posts_checked += 1
            
            # Skip if already used, is a video, or is NSFW
            if submission.id in used_post_ids:
                print(f"  ⏭️  Post {submission.id}: already used")
                continue
                
            if submission.is_video:
                print(f"  ⏭️  Post {submission.id}: is a video")
                continue
                
            if submission.over_18:
                print(f"  ⏭️  Post {submission.id}: NSFW")
                continue
            
            print(f"✅ Found new eligible post: {submission.id}")
            print(f"   Title: {submission.title[:80]}...")
            
            # Get top comments
            submission.comments.replace_more(limit=0)  # Remove "load more comments" objects
            top_comments = submission.comments.list()[:5]  # Get top 5 comments
            
            post_body = ""
            comment_count = 0
            
            for comment in top_comments:
                if hasattr(comment, 'body') and not comment.stickied:
                    comment_text = comment.body
                    # Skip short comments, deleted, or removed
                    if len(comment_text) > 30 and comment_text not in ['[deleted]', '[removed]']:
                        post_body += comment_text + "\n\n"
                        comment_count += 1
                        if comment_count >= 3:  # Limit to 3 substantial comments
                            break
            
            if not post_body:
                print(f"   ⚠️  Post {submission.id} has no substantial comments. Skipping.")
                continue
            
            print(f"   ✅ Successfully fetched post with {comment_count} comments")
            
            # Add this post ID to our used list
            with open(USED_POSTS_FILE, 'a') as f:
                f.write(f"{submission.id}\n")
            
            return {
                "id": submission.id,
                "title": submission.title,
                "body": post_body,
                "url": f"https://reddit.com{submission.permalink}"
            }
        
        print(f"⚠️  No new, eligible posts found (checked {posts_checked} posts)")
        return None
    
    except Exception as e:
        print(f"❌ Error accessing Reddit API: {e}")
        print(f"   Make sure REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, and REDDIT_PASSWORD are set")
        import traceback
        traceback.print_exc()
        return None
