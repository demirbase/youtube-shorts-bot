#!/usr/bin/env python3
"""
Demo: How to customize Reddit image appearance
Shows before/after with config changes
"""

import os
from reddit_image_creator import create_reddit_post_image

# Sample post data
sample_post = {
    'title': "What's a small change that improved your life dramatically?",
    'body': "I started drinking more water and going to bed earlier. Within a week I felt completely different.",
    'subreddit': 'AskReddit',
    'comments': [
        {'author': 'healthy_habits', 'body': 'I started meal prepping on Sundays. Saves so much time and money during the week!'},
        {'author': 'productivity_pro', 'body': 'Turned off all phone notifications except calls. My focus improved 10x.'},
        {'author': 'morning_person', 'body': 'Wake up 30 minutes earlier to exercise. Best decision ever.'},
    ]
}

print("🎨 Reddit Image Creator - Customization Demo")
print("=" * 60)
print()
print("CURRENT SETTINGS (from reddit_image_config.py):")
print()

# Show current config
try:
    from reddit_image_config import (
        BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR, META_COLOR,
        FONT_SIZE_TITLE, FONT_SIZE_BODY, PADDING, MAX_COMMENTS_SHOWN
    )
    print(f"  Colors:")
    print(f"    Background: {BACKGROUND_COLOR}")
    print(f"    Text:       {TEXT_COLOR}")
    print(f"    Accent:     {ACCENT_COLOR}")
    print(f"    Meta:       {META_COLOR}")
    print()
    print(f"  Fonts:")
    print(f"    Title:      {FONT_SIZE_TITLE}pt")
    print(f"    Body:       {FONT_SIZE_BODY}pt")
    print()
    print(f"  Layout:")
    print(f"    Padding:    {PADDING}px")
    print(f"    Comments:   Show top {MAX_COMMENTS_SHOWN}")
except ImportError:
    print("  ⚠️  reddit_image_config.py not found (using defaults)")

print()
print("─" * 60)
print()

# Generate demo image
print("📸 Generating demo image with current settings...")
result = create_reddit_post_image(
    post_data=sample_post,
    output_file="demo_current.png",
    width=1080,
    height=1920
)

if result:
    print(f"✅ Demo image created: {result}")
    print()
    print("📋 To customize:")
    print()
    print("  1. Open: reddit_image_config.py")
    print("  2. Edit any values (colors, fonts, spacing)")
    print("  3. Save the file")
    print("  4. Run this script again to see changes")
    print()
    print("  View the image: open demo_current.png")
    print()
    print("💡 Examples:")
    print()
    print("  • Light mode: Change BACKGROUND_COLOR to '#FFFFFF'")
    print("  • Bigger text: Increase all FONT_SIZE_* values")
    print("  • More comments: Set MAX_COMMENTS_SHOWN = 5")
    print("  • Tighter layout: Reduce PADDING and LINE_HEIGHT_* values")
    print()
    print("  See docs/CUSTOMIZE_IMAGE.md for full guide!")
else:
    print("❌ Failed to create demo image")
