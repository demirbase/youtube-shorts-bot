# reddit_image_creator.py
# Creates Reddit-style post images using PIL instead of screenshots
# This avoids Reddit blocking issues entirely

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def create_reddit_post_image(
    post_data: dict,
    output_file: str = "post.png",
    width: int = 1080,
    height: int = 1920
) -> str | None:
    """
    Creates a Reddit-style post image from post data using PIL.
    
    This avoids Reddit blocking by creating our own styled image
    instead of taking a screenshot.
    
    Args:
        post_data: Reddit post data with title, body, subreddit
        output_file: Path to save the image
        width: Image width (default 1080)
        height: Image height (default 1920)
        
    Returns:
        Path to created image, or None on failure
    """
    print("🎨 Creating Reddit-style post image...")
    
    try:
        # Reddit dark mode colors
        BG_COLOR = "#1A1A1B"       # Dark background (Reddit dark mode)
        TEXT_COLOR = "#D7DADC"     # Main text color
        ORANGE = "#FF4500"         # Reddit orange
        GRAY = "#818384"           # Meta text color
        
        # Create image with dark background
        img = Image.new('RGB', (width, height), BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            comment_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            meta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except Exception as e:
            # Fallback to default font
            print(f"   Warning: Could not load custom fonts ({e}), using default font")
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            comment_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()
        
        # Extract post data
        title = post_data.get('title', 'No title')
        body = post_data.get('body', '')
        subreddit = post_data.get('subreddit', 'AskReddit')
        comment_count = len(post_data.get('comments', []))
        
        # Drawing coordinates
        padding = 40
        y_position = padding + 60
        
        # Draw subreddit name
        subreddit_text = f"r/{subreddit}"
        draw.text((padding, padding), subreddit_text, fill=ORANGE, font=meta_font)
        
        # Draw title (wrapped)
        title_chars_per_line = 28
        wrapped_title = textwrap.fill(title, width=title_chars_per_line)
        
        for line in wrapped_title.split('\n'):
            draw.text((padding, y_position), line, fill=TEXT_COLOR, font=title_font)
            y_position += 55
        
        y_position += 20  # Space after title
        
        # Draw body if present (first 500 chars)
        if body and len(body.strip()) > 0:
            body_text = body[:500] + "..." if len(body) > 500 else body
            body_chars_per_line = 35
            wrapped_body = textwrap.fill(body_text, width=body_chars_per_line)
            
            for line in wrapped_body.split('\n')[:10]:  # Max 10 lines
                if y_position > height - 200:  # Leave space at bottom
                    break
                draw.text((padding, y_position), line, fill=TEXT_COLOR, font=body_font)
                y_position += 45
            
            y_position += 30
        
        # Draw top comments
        comments = post_data.get('comments', [])[:3]  # Top 3 comments
        
        if comments:
            y_position += 30
            draw.text((padding, y_position), "Top Comments:", fill=GRAY, font=meta_font)
            y_position += 40
            
            for i, comment in enumerate(comments):
                if y_position > height - 150:
                    break
                
                author = comment.get('author', 'unknown')
                comment_text = comment.get('body', '')[:200]
                
                # Draw author
                draw.text((padding + 20, y_position), f"u/{author}", fill=ORANGE, font=meta_font)
                y_position += 35
                
                # Draw comment text (wrapped)
                comment_chars_per_line = 32
                wrapped_comment = textwrap.fill(comment_text, width=comment_chars_per_line)
                
                for line in wrapped_comment.split('\n')[:3]:  # Max 3 lines per comment
                    if y_position > height - 100:
                        break
                    draw.text((padding + 20, y_position), line, fill=TEXT_COLOR, font=body_font)
                    y_position += 42
                
                y_position += 25  # Space between comments
        
        # Draw metadata at bottom
        meta_y = height - 80
        meta_text = f"↑ Upvote  💬 {comment_count} Comments  🔗 Share"
        draw.text((padding, meta_y), meta_text, fill=GRAY, font=meta_font)
        
        # Draw Reddit-style voting arrows (decorative)
        # Upvote arrow
        arrow_x = padding - 30
        arrow_y = padding + 80
        draw.polygon([
            (arrow_x + 15, arrow_y),
            (arrow_x + 25, arrow_y + 15),
            (arrow_x + 20, arrow_y + 15),
            (arrow_x + 20, arrow_y + 30),
            (arrow_x + 10, arrow_y + 30),
            (arrow_x + 10, arrow_y + 15),
            (arrow_x + 5, arrow_y + 15)
        ], fill=GRAY)
        
        # Save image
        img.save(output_file, 'PNG', quality=95)
        
        print(f"✅ Reddit-style image created: {output_file}")
        print(f"   Size: {os.path.getsize(output_file) / 1024:.1f} KB")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error creating Reddit-style image: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test with sample data
    test_post = {
        'title': 'What is something that everyone should experience at least once in their lifetime?',
        'body': '',
        'subreddit': 'AskReddit',
        'comments': [
            {'author': 'user1', 'body': 'Traveling to a foreign country where you don\'t speak the language. It really opens your eyes.'},
            {'author': 'user2', 'body': 'Working in customer service. You learn patience and empathy.'},
            {'author': 'user3', 'body': 'Living alone for at least a year. You discover so much about yourself.'}
        ]
    }
    
    print("Testing Reddit image creator...")
    result = create_reddit_post_image(test_post, "test_reddit_post.png")
    if result:
        print(f"\n✅ Test successful! Image saved to: {result}")
    else:
        print("\n❌ Test failed.")
