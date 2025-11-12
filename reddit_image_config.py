# reddit_image_config.py
# Configuration file for Reddit image styling
# Edit these values to customize the appearance of generated Reddit images

# ============================================================================
# IMAGE DIMENSIONS
# ============================================================================
IMAGE_WIDTH = 1080      # Width in pixels (9:16 aspect ratio for Shorts)
IMAGE_HEIGHT = 1920     # Height in pixels

# ============================================================================
# COLORS (Hex format)
# ============================================================================
# Reddit Dark Mode Theme
BACKGROUND_COLOR = "#1A1A1B"    # Dark gray background
TEXT_COLOR = "#D7DADC"          # Light gray text (title, body, comments)
ACCENT_COLOR = "#FF4500"        # Reddit orange (subreddit name, usernames)
META_COLOR = "#818384"          # Medium gray (metadata, footer)

# Alternative themes (uncomment to use):
# 
# Light Mode:
# BACKGROUND_COLOR = "#FFFFFF"
# TEXT_COLOR = "#1A1A1B"
# ACCENT_COLOR = "#FF4500"
# META_COLOR = "#7C7C7C"
#
# High Contrast:
# BACKGROUND_COLOR = "#000000"
# TEXT_COLOR = "#FFFFFF"
# ACCENT_COLOR = "#FF6A00"
# META_COLOR = "#AAAAAA"

# ============================================================================
# FONTS
# ============================================================================
# Font paths (Ubuntu/Linux - used in GitHub Actions)
FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Font sizes (in points)
FONT_SIZE_SUBREDDIT = 18    # r/AskReddit at top
FONT_SIZE_TITLE = 32        # Post title (bold)
FONT_SIZE_BODY = 24         # Post body text
FONT_SIZE_COMMENT = 20      # Comment text
FONT_SIZE_META = 18         # Usernames, footer

# ============================================================================
# LAYOUT & SPACING
# ============================================================================
PADDING = 40                # Left/right margins from edges
TOP_PADDING = 40            # Top margin
BOTTOM_PADDING = 100        # Bottom margin (leave space for footer)

LINE_HEIGHT_TITLE = 55      # Vertical space per line for title
LINE_HEIGHT_BODY = 45       # Vertical space per line for body
LINE_HEIGHT_COMMENT = 42    # Vertical space per line for comments

SECTION_SPACING = 30        # Space between sections (title → body → comments)
COMMENT_SPACING = 25        # Space between individual comments

# ============================================================================
# TEXT WRAPPING
# ============================================================================
# Characters per line (adjust based on font size)
TITLE_CHARS_PER_LINE = 28   # Wrap title at this many characters
BODY_CHARS_PER_LINE = 35    # Wrap body text at this many characters
COMMENT_CHARS_PER_LINE = 32 # Wrap comments at this many characters

# ============================================================================
# CONTENT LIMITS
# ============================================================================
MAX_BODY_LENGTH = 500       # Maximum characters to show from body
MAX_BODY_LINES = 10         # Maximum lines to show from body
MAX_COMMENT_LENGTH = 200    # Maximum characters per comment
MAX_COMMENT_LINES = 3       # Maximum lines per comment
MAX_COMMENTS_SHOWN = 3      # Number of top comments to display

# ============================================================================
# DECORATIVE ELEMENTS
# ============================================================================
SHOW_UPVOTE_ARROW = True    # Show decorative upvote arrow
SHOW_FOOTER = True          # Show "↑ Upvote 💬 Comments 🔗 Share" footer
SHOW_COMMENT_INDENT = True  # Indent comments slightly (20px)

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
OUTPUT_FORMAT = "PNG"       # Image format (PNG or JPEG)
OUTPUT_QUALITY = 95         # Quality for JPEG (1-100), ignored for PNG
