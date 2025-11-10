# comment_image_pil.py
# PIL-based comment image generator (no wkhtmltoimage required)

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def create_comment_image_pil(
    text: str,
    username: str,
    output_png: str,
    width: int = 900,
    is_title: bool = False
) -> str | None:
    """
    Generates a PNG image from text using PIL (no external dependencies).
    
    Args:
        text: The comment or title text
        username: Username or subreddit name
        output_png: Output file path
        width: Width of the generated image
        is_title: If True, uses title styling
        
    Returns:
        Path to generated PNG, or None on failure
    """
    print(f"🎨 Generating image with PIL: {output_png}")
    
    try:
        # Different styles for title vs comment
        if is_title:
            bg_color = (255, 69, 0)  # Reddit orange
            text_color = (255, 255, 255)
            username_color = (255, 255, 255)
            font_size = 42
            username_size = 32
            padding = 30
        else:
            bg_color = (26, 26, 27)  # Reddit dark mode
            text_color = (215, 218, 220)
            username_color = (79, 188, 255)  # Reddit blue
            font_size = 36
            username_size = 28
            padding = 25
        
        # Try to load a nice font, fallback to default
        try:
            # Try common system fonts
            if os.path.exists('/System/Library/Fonts/Helvetica.ttc'):
                # macOS
                title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
                username_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', username_size)
            elif os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
                # Linux
                title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
                username_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', username_size)
            else:
                # Fallback to default
                title_font = ImageFont.load_default()
                username_font = ImageFont.load_default()
        except:
            title_font = ImageFont.load_default()
            username_font = ImageFont.load_default()
        
        # Wrap text
        chars_per_line = 30 if is_title else 35
        wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        
        # Create a temporary image to measure text
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Calculate required height
        line_height = font_size + 10
        text_height = len(wrapped_lines) * line_height
        total_height = padding * 3 + username_size + 10 + text_height + padding
        
        # Create the actual image
        img = Image.new('RGB', (width, int(total_height)), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add rounded corners effect with a border
        border_color = (52, 53, 54)
        draw.rectangle([(0, 0), (width, total_height)], outline=border_color, width=3)
        
        # Draw username
        y_pos = padding
        draw.text((padding, y_pos), username, fill=username_color, font=username_font)
        
        # Draw text lines
        y_pos += username_size + 20
        for line in wrapped_lines:
            draw.text((padding, y_pos), line, fill=text_color, font=title_font)
            y_pos += line_height
        
        # Save the image
        img.save(output_png, 'PNG')
        print(f"✅ Successfully created image: {output_png}")
        return output_png
        
    except Exception as e:
        print(f"❌ Error creating image: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_all_comment_images_pil(post_data: dict, output_dir: str = ".") -> list:
    """
    Creates PNG images for title and all comments using PIL.
    
    Args:
        post_data: Reddit post data dictionary
        output_dir: Directory to save images
        
    Returns:
        List of image file paths
    """
    images = []
    
    # Create title image
    title_img = create_comment_image_pil(
        text=post_data['title'],
        username=f"r/{post_data.get('subreddit', 'AskReddit')}",
        output_png=os.path.join(output_dir, "title.png"),
        is_title=True
    )
    if title_img:
        images.append(title_img)
    
    # Create comment images
    if 'comments' in post_data:
        for i, comment in enumerate(post_data['comments'][:3], 1):
            comment_img = create_comment_image_pil(
                text=comment['body'],
                username=f"u/{comment.get('author', 'anonymous')}",
                output_png=os.path.join(output_dir, f"comment_{i}.png"),
                is_title=False
            )
            if comment_img:
                images.append(comment_img)
    
    return images
