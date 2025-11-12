#!/usr/bin/env python3
"""
reddit_frame_creator.py
Reddit arayüzü çerçevesi oluşturur - metin alanı ŞEFFAF bırakılır
Metin daha sonra FFmpeg tarafından altyazı olarak eklenecek
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Import configuration
try:
    from reddit_image_config import *
except ImportError:
    # Fallback to defaults
    BACKGROUND_COLOR = "#1A1A1B"
    TEXT_COLOR = "#D7DADC"
    ACCENT_COLOR = "#FF4500"
    META_COLOR = "#818384"
    FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    FONT_SIZE_META = 18
    PADDING = 40
    SHOW_UPVOTE_ARROW = True


def create_reddit_frame(
    subreddit: str = "AskReddit",
    output_file: str = "reddit_frame.png",
    width: int = 1080,
    height: int = 1920,
    transparent_area_height: int = 1400  # Şeffaf alan yüksekliği
) -> str | None:
    """
    Reddit arayüzü çerçevesi oluşturur - metin alanı şeffaf bırakılır.
    
    Args:
        subreddit: Subreddit adı (r/AskReddit vb.)
        output_file: Çıktı dosyası
        width: Genişlik
        height: Yükseklik
        transparent_area_height: Şeffaf alan yüksekliği (metin için)
        
    Returns:
        Oluşturulan dosya yolu veya None
    """
    print("🎨 Creating Reddit frame with transparent text area...")
    print(f"   Subreddit: r/{subreddit}")
    print(f"   Transparent area: {transparent_area_height}px")
    
    try:
        # RGBA modunda resim oluştur (Alpha kanalı için)
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Font yükle
        try:
            meta_font = ImageFont.truetype(FONT_PATH_REGULAR, FONT_SIZE_META)
        except Exception as e:
            print(f"   Warning: Could not load font ({e}), using default")
            meta_font = ImageFont.load_default()
        
        # Renkleri RGB tuple'a çevir
        bg_rgb = tuple(int(BACKGROUND_COLOR.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        accent_rgb = tuple(int(ACCENT_COLOR.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        meta_rgb = tuple(int(META_COLOR.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # ÜST BAR: Subreddit adı (opak arka plan)
        top_bar_height = 100
        draw.rectangle(
            [(0, 0), (width, top_bar_height)],
            fill=bg_rgb + (255,)  # Tam opak
        )
        
        # Subreddit metni
        subreddit_text = f"r/{subreddit}"
        draw.text(
            (PADDING, PADDING),
            subreddit_text,
            fill=accent_rgb + (255,),
            font=meta_font
        )
        
        # ORTA ALAN: Şeffaf (metin buraya gelecek)
        # Bu alanı tamamen şeffaf bırak
        transparent_start = top_bar_height
        transparent_end = transparent_start + transparent_area_height
        
        print(f"   Transparent area: {transparent_start}px - {transparent_end}px")
        
        # ALT BAR: Meta bilgiler (opak arka plan)
        bottom_bar_height = 100
        bottom_bar_start = height - bottom_bar_height
        
        draw.rectangle(
            [(0, bottom_bar_start), (width, height)],
            fill=bg_rgb + (255,)
        )
        
        # Meta metni
        meta_text = "↑ Upvote  💬 Comments  🔗 Share"
        draw.text(
            (PADDING, bottom_bar_start + 40),
            meta_text,
            fill=meta_rgb + (255,),
            font=meta_font
        )
        
        # Upvote oku (dekoratif)
        if SHOW_UPVOTE_ARROW:
            arrow_x = PADDING - 25
            arrow_y = transparent_start + 50
            draw.polygon([
                (arrow_x + 15, arrow_y),
                (arrow_x + 25, arrow_y + 15),
                (arrow_x + 20, arrow_y + 15),
                (arrow_x + 20, arrow_y + 30),
                (arrow_x + 10, arrow_y + 30),
                (arrow_x + 10, arrow_y + 15),
                (arrow_x + 5, arrow_y + 15)
            ], fill=meta_rgb + (255,))
        
        # PNG olarak kaydet (Alpha kanalını korur)
        img.save(output_file, 'PNG')
        
        file_size = os.path.getsize(output_file) / 1024
        print(f"✅ Reddit frame created: {output_file}")
        print(f"   Size: {file_size:.1f} KB")
        print(f"   Transparent text area: {transparent_area_height}px tall")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error creating Reddit frame: {e}")
        return None


def create_frame_for_post(post_data: dict, output_file: str = "reddit_frame.png") -> str | None:
    """
    Reddit post verisiyle çerçeve oluşturur.
    
    Args:
        post_data: Reddit post dictionary
        output_file: Çıktı dosyası
        
    Returns:
        Oluşturulan dosya yolu veya None
    """
    subreddit = post_data.get('subreddit', 'AskReddit')
    return create_reddit_frame(
        subreddit=subreddit,
        output_file=output_file
    )


if __name__ == "__main__":
    # Test
    print("🧪 Testing Reddit frame creator...")
    print("=" * 60)
    
    result = create_reddit_frame(
        subreddit="AskReddit",
        output_file="test_frame.png"
    )
    
    if result:
        print()
        print("✅ Test successful!")
        print(f"   Frame created: {result}")
        print()
        print("📝 This frame has:")
        print("   • Top bar with subreddit name")
        print("   • TRANSPARENT middle area (for subtitles)")
        print("   • Bottom bar with meta info")
        print()
        print("🎬 Next step: FFmpeg will burn subtitles into transparent area")
    else:
        print()
        print("❌ Test failed")
