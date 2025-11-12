#!/usr/bin/env python3
"""
reddit_fetcher.py
Reddit API ile post çekme (PRAW wrapper)
"""

import praw
import os


def authenticate_reddit() -> praw.Reddit | None:
    """
    Reddit API authentication.
    
    Returns:
        praw.Reddit instance or None
    """
    try:
        client_id = os.environ.get('REDDIT_CLIENT_ID', '').strip()
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET', '').strip()
        username = os.environ.get('REDDIT_USERNAME', '').strip()
        password = os.environ.get('REDDIT_PASSWORD', '').strip()
        
        if not all([client_id, client_secret, username, password]):
            print("❌ Reddit credentials not found in environment")
            return None
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=f'python:reddit-shorts-bot:v4.0 (by /u/{username})',
            username=username,
            password=password
        )
        
        # Test authentication
        reddit.user.me()
        print(f"✅ Authenticated as u/{reddit.user.me().name}")
        
        return reddit
        
    except Exception as e:
        print(f"❌ Reddit authentication error: {e}")
        return None


def fetch_popular_post(reddit: praw.Reddit, subreddit_name: str) -> dict | None:
    """
    Fetch a popular post from subreddit.
    
    Args:
        reddit: Authenticated PRAW instance
        subreddit_name: Subreddit name (e.g., "AskReddit")
        
    Returns:
        Post data dictionary or None
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Load used posts
        used_posts = set()
        if os.path.exists('used_posts.txt'):
            with open('used_posts.txt', 'r') as f:
                used_posts = set(line.strip() for line in f if line.strip())
        
        # Fetch hot posts
        for post in subreddit.hot(limit=50):
            # Skip if already used
            if post.id in used_posts:
                continue
            
            # Skip if stickied or not suitable
            if post.stickied or post.over_18:
                continue
            
            # Must have good title
            if len(post.title) < 20:
                continue
            
            # Get top comments
            post.comments.replace_more(limit=0)
            comments = []
            
            for comment in post.comments[:10]:
                if hasattr(comment, 'body') and len(comment.body) > 20:
                    comments.append({
                        'author': str(comment.author) if comment.author else 'deleted',
                        'body': comment.body,
                        'score': comment.score
                    })
            
            # Need at least 3 good comments
            if len(comments) < 3:
                continue
            
            # Return post data
            return {
                'id': post.id,
                'title': post.title,
                'body': post.selftext if hasattr(post, 'selftext') else '',
                'subreddit': subreddit_name,
                'url': f"https://reddit.com{post.permalink}",
                'score': post.score,
                'comments': comments
            }
        
        print("❌ No suitable post found")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching post: {e}")
        return None


def mark_post_as_used(post_id: str):
    """
    Mark a post as used to avoid duplicates.
    """
    try:
        with open('used_posts.txt', 'a') as f:
            f.write(f"{post_id}\n")
        print(f"✅ Post {post_id} marked as used")
    except Exception as e:
        print(f"⚠️  Could not mark post as used: {e}")


if __name__ == "__main__":
    # Test
    print("🧪 Testing Reddit fetcher...")
    print("=" * 60)
    
    reddit = authenticate_reddit()
    if reddit:
        post = fetch_popular_post(reddit, "AskReddit")
        if post:
            print()
            print("✅ Test successful!")
            print(f"   Title: {post['title'][:50]}...")
            print(f"   Comments: {len(post['comments'])}")
        else:
            print()
            print("❌ No post found")
    else:
        print()
        print("❌ Authentication failed")
