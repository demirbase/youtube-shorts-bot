# comment_image_generator.py
# Generates styled PNG images from Reddit comments

import subprocess
import textwrap
import os

def create_comment_image(
    text: str, 
    username: str, 
    output_png: str, 
    width: int = 900,
    is_title: bool = False
) -> str | None:
    """
    Generates a PNG image from a text string by creating
    and "screenshotting" a temporary HTML file.
    
    Args:
        text: The comment or title text
        username: Username or subreddit name (e.g., "r/AskReddit")
        output_png: Output file path
        width: Width of the generated image in pixels
        is_title: If True, uses title styling (larger, different color)
        
    Returns:
        Path to generated PNG, or None on failure
    """
    print(f"🎨 Generating image for: {output_png}")
    
    # Wrap text to prevent overflow (adjust based on font size)
    chars_per_line = 35 if is_title else 40
    wrapped_text = textwrap.fill(text, width=chars_per_line)
    
    # Escape HTML special characters
    wrapped_text = wrapped_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    username = username.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Different styles for title vs comment
    if is_title:
        bg_color = "#FF4500"  # Reddit orange
        username_color = "#FFFFFF"
        text_size = "32px"
        username_size = "22px"
    else:
        bg_color = "#1A1A1B"  # Reddit dark mode
        username_color = "#4FBCFF"  # Reddit blue
        text_size = "28px"
        username_size = "20px"
    
    # Create HTML content with Reddit-style design
    html_content = f"""
    <!DOCTYPE html>
    <html><head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background-color: transparent;
            margin: 0;
            padding: 20px;
        }}
        .comment-box {{
            background-color: {bg_color};
            color: #D7DADC;
            border-radius: 12px;
            padding: 20px 25px;
            border: 2px solid #343536;
            width: {width}px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        .username {{
            font-weight: bold;
            color: {username_color};
            font-size: {username_size};
            margin-bottom: 10px;
        }}
        .comment {{
            font-size: {text_size};
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
    </head><body>
    <div class="comment-box">
        <div class="username">{username}</div>
        <div class="comment">{wrapped_text}</div>
    </div>
    </body></html>
    """
    
    html_file = f"temp_{os.path.basename(output_png)}.html"
    
    try:
        # Write HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Use wkhtmltoimage to "screenshot" the HTML to a transparent PNG
        command = [
            "wkhtmltoimage",
            "--width", str(width + 100),
            "--disable-smart-width",
            "--transparent",  # Make background transparent
            "--quality", "100",
            html_file,
            output_png
        ]
        
        result = subprocess.run(command, capture_output=True, stderr=subprocess.PIPE)
        
        # Clean up temp HTML
        if os.path.exists(html_file):
            os.remove(html_file)
        
        if result.returncode == 0 and os.path.exists(output_png):
            print(f"✅ Successfully created comment image: {output_png}")
            return output_png
        else:
            print(f"❌ wkhtmltoimage failed. Is it installed? (sudo apt-get install wkhtmltopdf)")
            print(f"   Error: {result.stderr.decode()}")
            return None
            
    except FileNotFoundError:
        print("❌ wkhtmltoimage not found. Please install it:")
        print("   Linux: sudo apt-get install wkhtmltopdf")
        print("   macOS: brew install wkhtmltopdf")
        return None
    except Exception as e:
        print(f"❌ Error creating comment image: {e}")
        # Clean up temp HTML on error
        if os.path.exists(html_file):
            os.remove(html_file)
        return None


def create_all_comment_images(post_data: dict, output_dir: str = ".") -> list:
    """
    Creates PNG images for title and all comments from post data.
    
    Args:
        post_data: Reddit post data dictionary
        output_dir: Directory to save images
        
    Returns:
        List of (image_path, duration_hint) tuples
    """
    images = []
    
    # Create title image
    title_img = create_comment_image(
        text=post_data['title'],
        username=f"r/{post_data.get('subreddit', 'AskReddit')}",
        output_png=os.path.join(output_dir, "title.png"),
        is_title=True
    )
    if title_img:
        images.append(title_img)
    
    # Create comment images
    if 'comments' in post_data:
        for i, comment in enumerate(post_data['comments'][:3], 1):  # Max 3 comments
            comment_img = create_comment_image(
                text=comment['body'],
                username=f"u/{comment.get('author', 'anonymous')}",
                output_png=os.path.join(output_dir, f"comment_{i}.png"),
                is_title=False
            )
            if comment_img:
                images.append(comment_img)
    
    return images
