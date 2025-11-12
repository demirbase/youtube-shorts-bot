# How to Customize Reddit Image Appearance

## 🎨 Quick Start

All visual settings are in **`reddit_image_config.py`** - just edit that file!

## 📝 Examples

### Change Colors (Dark → Light Mode)

**Open `reddit_image_config.py` and change:**

```python
# FROM (Dark Mode):
BACKGROUND_COLOR = "#1A1A1B"    # Dark gray
TEXT_COLOR = "#D7DADC"          # Light gray
ACCENT_COLOR = "#FF4500"        # Reddit orange
META_COLOR = "#818384"          # Medium gray

# TO (Light Mode):
BACKGROUND_COLOR = "#FFFFFF"    # White
TEXT_COLOR = "#1A1A1B"          # Dark gray
ACCENT_COLOR = "#FF4500"        # Reddit orange
META_COLOR = "#7C7C7C"          # Medium gray
```

### Make Text Bigger

```python
# Increase all font sizes by 20%:
FONT_SIZE_SUBREDDIT = 22    # was 18
FONT_SIZE_TITLE = 38        # was 32
FONT_SIZE_BODY = 29         # was 24
FONT_SIZE_COMMENT = 24      # was 20
FONT_SIZE_META = 22         # was 18
```

### Show More Comments

```python
# Show top 5 comments instead of 3:
MAX_COMMENTS_SHOWN = 5      # was 3
```

### Change Spacing/Layout

```python
# Make everything more compact:
PADDING = 30                # was 40 (reduce margins)
LINE_HEIGHT_TITLE = 45      # was 55 (tighter title spacing)
LINE_HEIGHT_BODY = 35       # was 45 (tighter body spacing)
SECTION_SPACING = 20        # was 30 (less space between sections)
```

### Disable Decorative Elements

```python
# Hide the upvote arrow and footer:
SHOW_UPVOTE_ARROW = False   # was True
SHOW_FOOTER = False         # was True
```

## 🧪 Testing Your Changes

After editing `reddit_image_config.py`, test immediately:

```bash
# Quick test with sample data:
python reddit_image_creator.py

# Integration test (simulates real bot data):
python test_image_integration.py

# View the generated image:
open test_reddit_post.png
```

## 🎯 Common Customizations

### High Contrast Theme
```python
BACKGROUND_COLOR = "#000000"    # Pure black
TEXT_COLOR = "#FFFFFF"          # Pure white
ACCENT_COLOR = "#FF6A00"        # Brighter orange
META_COLOR = "#AAAAAA"          # Light gray
```

### Larger Text for Readability
```python
FONT_SIZE_TITLE = 40
FONT_SIZE_BODY = 28
LINE_HEIGHT_TITLE = 65
LINE_HEIGHT_BODY = 50
```

### Show More Content
```python
MAX_BODY_LENGTH = 800           # was 500
MAX_BODY_LINES = 15             # was 10
MAX_COMMENTS_SHOWN = 5          # was 3
MAX_COMMENT_LENGTH = 300        # was 200
```

### Wider Margins
```python
PADDING = 60                    # was 40
TOP_PADDING = 60                # was 40
BOTTOM_PADDING = 120            # was 100
```

## 📐 Understanding Text Wrapping

These values control how many characters fit per line:

```python
TITLE_CHARS_PER_LINE = 28       # Wider = longer lines, fewer wraps
BODY_CHARS_PER_LINE = 35        # Narrower = shorter lines, more wraps
COMMENT_CHARS_PER_LINE = 32
```

**Formula:** `chars_per_line ≈ (image_width - 2*padding) / (font_size * 0.6)`

## 🔧 Advanced: Custom Fonts (macOS)

To use custom fonts on macOS for local testing:

1. Install DejaVu fonts:
```bash
brew install --cask font-dejavu
```

2. Or change font paths in config:
```python
# Use macOS system fonts:
FONT_PATH_BOLD = "/System/Library/Fonts/Helvetica.ttc"
FONT_PATH_REGULAR = "/System/Library/Fonts/Helvetica.ttc"
```

## ✅ Validation

After changes, check:
- [ ] Test image generates without errors
- [ ] Text is readable (not too big/small)
- [ ] Colors have good contrast
- [ ] All content fits within image bounds
- [ ] File size is reasonable (~30-50 KB)

## 🚀 Deploy

Changes to `reddit_image_config.py` work immediately:
- **Local testing**: Takes effect on next run
- **GitHub Actions**: Automatically uses the config file
- **No code changes needed**: Just edit config values

## 📖 Full Config Reference

See `reddit_image_config.py` for complete documentation of all available settings.

## 🎨 Example Themes

### Reddit Old Design
```python
BACKGROUND_COLOR = "#CEE3F8"
TEXT_COLOR = "#000000"
ACCENT_COLOR = "#5F99CF"
META_COLOR = "#888888"
```

### OLED Dark Mode (Pure Black)
```python
BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FF4500"
META_COLOR = "#999999"
PADDING = 50                    # More padding looks better on OLED
```

### Accessibility (High Contrast)
```python
BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FFD700"        # Gold (more visible than orange)
META_COLOR = "#CCCCCC"
FONT_SIZE_TITLE = 36            # Larger text
FONT_SIZE_BODY = 26
```

## 💡 Tips

1. **Test incrementally**: Change one thing, test, then change another
2. **Keep backups**: Copy config before major changes
3. **Check contrast**: Use online contrast checkers for accessibility
4. **Mobile preview**: View generated images on phone to check readability
5. **File size**: If images get too large, reduce quality or use JPEG

## 🐛 Troubleshooting

**Text overflows image bounds:**
- Reduce `MAX_BODY_LENGTH` or `MAX_BODY_LINES`
- Increase `CHARS_PER_LINE` values
- Decrease font sizes

**Text too small to read:**
- Increase all `FONT_SIZE_*` values
- Increase corresponding `LINE_HEIGHT_*` values

**Colors look washed out:**
- Use hex codes with full contrast (white on black, etc.)
- Avoid similar colors for text and background
- Test on both light and dark displays

**Font not loading:**
- Check font path exists: `ls -l /path/to/font.ttf`
- Falls back to default font automatically (works but less pretty)
- GitHub Actions uses Ubuntu paths (leave as default for production)
