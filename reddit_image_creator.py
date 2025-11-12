# reddit_image_creator.py
# Creates Reddit-style post images using PIL instead of screenshots
# This avoids Reddit blocking issues entirely

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# Import configuration (edit reddit_image_config.py to customize appearance)
try:
    from reddit_image_config import *
except ImportError:
    # Fallback to default values if config file is missing
    print("⚠️  reddit_image_config.py not found, using default values")
    IMAGE_WIDTH = 1080
    IMAGE_HEIGHT = 1920
    BACKGROUND_COLOR = "#1A1A1B"
    TEXT_COLOR = "#D7DADC"
    ACCENT_COLOR = "#FF4500"
    META_COLOR = "#818384"
    FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    FONT_SIZE_TITLE = 32
    FONT_SIZE_BODY = 24
    FONT_SIZE_COMMENT = 20
    FONT_SIZE_META = 18
    PADDING = 40
    LINE_HEIGHT_TITLE = 55
    LINE_HEIGHT_BODY = 45
    LINE_HEIGHT_COMMENT = 42
    SECTION_SPACING = 30
    COMMENT_SPACING = 25
    TITLE_CHARS_PER_LINE = 28
    BODY_CHARS_PER_LINE = 35
    COMMENT_CHARS_PER_LINE = 32
    MAX_BODY_LENGTH = 500
    MAX_BODY_LINES = 10
    MAX_COMMENT_LENGTH = 200
    MAX_COMMENT_LINES = 3
    MAX_COMMENTS_SHOWN = 3
    SHOW_UPVOTE_ARROW = True
    SHOW_FOOTER = True
    SHOW_COMMENT_INDENT = True
    OUTPUT_FORMAT = "PNG"
    OUTPUT_QUALITY = 95

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
    print(f"   Using config: {BACKGROUND_COLOR} bg, {TEXT_COLOR} text, {ACCENT_COLOR} accent")
    
    try:
        # Create image with configured background
        img = Image.new('RGB', (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts from config, fallback to default
        try:
            title_font = ImageFont.truetype(FONT_PATH_BOLD, FONT_SIZE_TITLE)
            body_font = ImageFont.truetype(FONT_PATH_REGULAR, FONT_SIZE_BODY)
            comment_font = ImageFont.truetype(FONT_PATH_REGULAR, FONT_SIZE_COMMENT)
            meta_font = ImageFont.truetype(FONT_PATH_REGULAR, FONT_SIZE_META)
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
        y_position = PADDING + 60
        
        # Draw subreddit name
        subreddit_text = f"r/{subreddit}"
        draw.text((PADDING, PADDING), subreddit_text, fill=ACCENT_COLOR, font=meta_font)
        
        # Draw title (wrapped)
        wrapped_title = textwrap.fill(title, width=TITLE_CHARS_PER_LINE)
        
        for line in wrapped_title.split('\n'):
            draw.text((PADDING, y_position), line, fill=TEXT_COLOR, font=title_font)
            y_position += LINE_HEIGHT_TITLE
        
        y_position += SECTION_SPACING  # Space after title
        
        # Draw body if present
        if body and len(body.strip()) > 0:
            body_text = body[:MAX_BODY_LENGTH] + "..." if len(body) > MAX_BODY_LENGTH else body
            wrapped_body = textwrap.fill(body_text, width=BODY_CHARS_PER_LINE)
            
            for line in wrapped_body.split('\n')[:MAX_BODY_LINES]:
                if y_position > height - 200:  # Leave space at bottom
                    break
                draw.text((PADDING, y_position), line, fill=TEXT_COLOR, font=body_font)
                y_position += LINE_HEIGHT_BODY
            
            y_position += SECTION_SPACING
        
        # Draw top comments
        comments = post_data.get('comments', [])[:MAX_COMMENTS_SHOWN]
        
        if comments:
            y_position += SECTION_SPACING
            draw.text((PADDING, y_position), "Top Comments:", fill=META_COLOR, font=meta_font)
            y_position += 40
            
            comment_indent = 20 if SHOW_COMMENT_INDENT else 0
            
            for i, comment in enumerate(comments):
                if y_position > height - 150:
                    break
                
                author = comment.get('author', 'unknown')
                comment_text = comment.get('body', '')[:MAX_COMMENT_LENGTH]
                
                # Draw author
                draw.text((PADDING + comment_indent, y_position), f"u/{author}", fill=ACCENT_COLOR, font=meta_font)
                y_position += 35
                
                # Draw comment text (wrapped)
                wrapped_comment = textwrap.fill(comment_text, width=COMMENT_CHARS_PER_LINE)
                
                for line in wrapped_comment.split('\n')[:MAX_COMMENT_LINES]:
                    if y_position > height - 100:
                        break
                    draw.text((PADDING + comment_indent, y_position), line, fill=TEXT_COLOR, font=body_font)
                    y_position += LINE_HEIGHT_COMMENT
                
                y_position += COMMENT_SPACING
        
        # Draw metadata footer (if enabled)
        if SHOW_FOOTER:
            meta_y = height - 80
            meta_text = f"↑ Upvote  💬 {comment_count} Comments  🔗 Share"
            draw.text((PADDING, meta_y), meta_text, fill=META_COLOR, font=meta_font)
        
        # Draw decorative upvote arrow (if enabled)
        if SHOW_UPVOTE_ARROW:
            arrow_x = PADDING - 30
            arrow_y = PADDING + 80
            draw.polygon([
                (arrow_x + 15, arrow_y),
                (arrow_x + 25, arrow_y + 15),
                (arrow_x + 20, arrow_y + 15),
                (arrow_x + 20, arrow_y + 30),
                (arrow_x + 10, arrow_y + 30),
                (arrow_x + 10, arrow_y + 15),
                (arrow_x + 5, arrow_y + 15)
            ], fill=META_COLOR)
        
        # Save image with configured format and quality
        if OUTPUT_FORMAT.upper() == "JPEG":
            img.save(output_file, 'JPEG', quality=OUTPUT_QUALITY)
        else:
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
