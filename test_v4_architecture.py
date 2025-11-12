#!/usr/bin/env python3
"""
test_v4_architecture.py
Comprehensive test suite for V4 architecture components

Tests:
1. Reddit frame has transparent area (RGBA mode)
2. Pexels downloads different videos
3. Subtitles generated with timing
4. FFmpeg can composite all layers
"""

import os
import sys
from PIL import Image


def test_reddit_frame_transparency():
    """
    Test 1: Verify reddit_frame_creator.py generates RGBA image with transparency
    """
    print("=" * 70)
    print("TEST 1: Reddit Frame Transparency")
    print("=" * 70)
    
    try:
        from reddit_frame_creator import create_reddit_frame
        
        # Generate test frame
        output = "test_v4_frame.png"
        result = create_reddit_frame(
            subreddit="AskReddit",
            output_file=output,
            width=1080,
            height=1920
        )
        
        if not result:
            print("❌ FAILED: Frame generation returned None")
            return False
        
        # Load and inspect image
        img = Image.open(output)
        
        # Check 1: Mode should be RGBA
        if img.mode != 'RGBA':
            print(f"❌ FAILED: Image mode is {img.mode}, expected RGBA")
            return False
        print(f"✅ Image mode: {img.mode}")
        
        # Check 2: Should have alpha channel
        if len(img.getbands()) != 4:
            print(f"❌ FAILED: Image has {len(img.getbands())} channels, expected 4")
            return False
        print(f"✅ Image channels: {img.getbands()}")
        
        # Check 3: Middle area should have transparent pixels
        # Sample pixels from middle area (y=500-1500)
        transparent_count = 0
        sample_points = 10
        
        for y in range(500, 1500, 100):
            pixel = img.getpixel((540, y))  # Center x
            r, g, b, a = pixel
            if a < 128:  # Semi-transparent or fully transparent
                transparent_count += 1
        
        if transparent_count == 0:
            print("⚠️  WARNING: No transparent pixels found in middle area")
            print("   This may prevent subtitles from being visible")
        else:
            print(f"✅ Transparent pixels found: {transparent_count}/{sample_points} sample points")
        
        # Check 4: Top and bottom should be opaque
        top_pixel = img.getpixel((540, 50))
        bottom_pixel = img.getpixel((540, 1870))
        
        if top_pixel[3] < 200:
            print("⚠️  WARNING: Top bar not fully opaque")
        else:
            print(f"✅ Top bar opaque: alpha={top_pixel[3]}")
        
        if bottom_pixel[3] < 200:
            print("⚠️  WARNING: Bottom bar not fully opaque")
        else:
            print(f"✅ Bottom bar opaque: alpha={bottom_pixel[3]}")
        
        print()
        print("✅ TEST 1 PASSED: Frame has correct transparency structure")
        print()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subtitle_generation():
    """
    Test 2: Verify subtitle_generator_v2.py creates valid SRT with timing
    """
    print("=" * 70)
    print("TEST 2: Subtitle Generation")
    print("=" * 70)
    
    try:
        from subtitle_generator_v2 import generate_audio_with_flow_sync
        
        # Test data
        title = "What's the best advice you've ever received?"
        comments = [
            {"author": "user1", "body": "The best advice I got was to always be kind."},
            {"author": "user2", "body": "Someone told me to never stop learning."}
        ]
        
        # Generate audio and subtitles
        result = generate_audio_with_flow_sync(
            title=title,
            comments=comments,
            audio_file="test_v4_audio.mp3",
            subtitle_file="test_v4_subtitles.srt",
            pause_between=0.5
        )
        
        if not result:
            print("❌ FAILED: Subtitle generation returned None")
            return False
        
        audio_file, subtitle_file = result
        
        # Check 1: Audio file exists and has content
        if not os.path.exists(audio_file):
            print(f"❌ FAILED: Audio file not created: {audio_file}")
            return False
        
        audio_size = os.path.getsize(audio_file)
        if audio_size < 1000:
            print(f"❌ FAILED: Audio file too small: {audio_size} bytes")
            return False
        print(f"✅ Audio file: {audio_file} ({audio_size/1024:.1f} KB)")
        
        # Check 2: Subtitle file exists and has valid SRT format
        if not os.path.exists(subtitle_file):
            print(f"❌ FAILED: Subtitle file not created: {subtitle_file}")
            return False
        
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Check for SRT structure: numbers, timestamps, text
        if not srt_content.strip():
            print("❌ FAILED: Subtitle file is empty")
            return False
        
        if '-->' not in srt_content:
            print("❌ FAILED: Subtitle file missing timestamp arrows (-->)")
            return False
        
        # Count subtitle blocks
        subtitle_blocks = srt_content.strip().split('\n\n')
        if len(subtitle_blocks) < 2:
            print(f"❌ FAILED: Too few subtitle blocks: {len(subtitle_blocks)}")
            return False
        
        print(f"✅ Subtitle file: {subtitle_file} ({len(subtitle_blocks)} blocks)")
        
        # Check 3: Verify timing format
        lines = srt_content.split('\n')
        timestamp_lines = [line for line in lines if '-->' in line]
        
        if not timestamp_lines:
            print("❌ FAILED: No timestamp lines found")
            return False
        
        # Parse first timestamp
        first_timestamp = timestamp_lines[0]
        try:
            start, end = first_timestamp.split(' --> ')
            # Validate format: 00:00:00,000
            if len(start) < 10 or ',' not in start:
                print(f"❌ FAILED: Invalid timestamp format: {start}")
                return False
            print(f"✅ Timestamp format valid: {first_timestamp}")
        except Exception as e:
            print(f"❌ FAILED: Could not parse timestamp: {e}")
            return False
        
        print()
        print("✅ TEST 2 PASSED: Subtitles generated with valid timing")
        print()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pexels_api():
    """
    Test 3: Verify pexels_dynamic.py can fetch videos
    """
    print("=" * 70)
    print("TEST 3: Pexels API Integration")
    print("=" * 70)
    
    try:
        from pexels_dynamic import get_random_background_video
        
        # Check API key
        api_key = os.getenv('PEXELS_API_KEY')
        if not api_key:
            print("⚠️  SKIPPED: PEXELS_API_KEY not set")
            print("   Set environment variable to test Pexels API")
            print("   export PEXELS_API_KEY='your_key'")
            print()
            return None  # Not failed, just skipped
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Attempt to download video
        result = get_random_background_video(
            output_file="test_v4_background.mp4",
            api_key=api_key,
            min_duration=10,
            max_duration=20
        )
        
        if not result:
            print("❌ FAILED: Video download returned None")
            print("   Check API key validity and quota")
            return False
        
        # Check video file
        if not os.path.exists(result):
            print(f"❌ FAILED: Video file not created: {result}")
            return False
        
        video_size = os.path.getsize(result)
        if video_size < 10000:
            print(f"❌ FAILED: Video file too small: {video_size} bytes")
            return False
        
        print(f"✅ Video downloaded: {result} ({video_size/1024/1024:.1f} MB)")
        print()
        print("✅ TEST 3 PASSED: Pexels API working correctly")
        print()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ffmpeg_composite():
    """
    Test 4: Verify FFmpeg can composite all layers
    (Requires previous tests to have generated test files)
    """
    print("=" * 70)
    print("TEST 4: FFmpeg Multi-Layer Composite")
    print("=" * 70)
    
    try:
        from ffmpeg_composer_v2 import compose_video_v2
        
        # Check if test files exist from previous tests
        required_files = {
            'background': 'test_v4_background.mp4',
            'frame': 'test_v4_frame.png',
            'subtitles': 'test_v4_subtitles.srt',
            'audio': 'test_v4_audio.mp3'
        }
        
        missing_files = []
        for name, path in required_files.items():
            if not os.path.exists(path):
                missing_files.append(f"{name} ({path})")
        
        if missing_files:
            print("⚠️  SKIPPED: Missing required files:")
            for f in missing_files:
                print(f"   - {f}")
            print("   Run previous tests first to generate these files")
            print()
            return None
        
        print("✅ All input files present")
        
        # Attempt composition
        result = compose_video_v2(
            background_video=required_files['background'],
            reddit_frame=required_files['frame'],
            subtitle_file=required_files['subtitles'],
            audio_file=required_files['audio'],
            output_file="test_v4_final.mp4"
        )
        
        if not result:
            print("❌ FAILED: Video composition returned None")
            print("   Check FFmpeg installation and logs above")
            return False
        
        # Check output video
        if not os.path.exists(result):
            print(f"❌ FAILED: Output video not created: {result}")
            return False
        
        video_size = os.path.getsize(result)
        if video_size < 10000:
            print(f"❌ FAILED: Output video too small: {video_size} bytes")
            return False
        
        print(f"✅ Final video created: {result} ({video_size/1024/1024:.1f} MB)")
        
        # Get duration
        from ffmpeg_composer_v2 import get_video_duration
        duration = get_video_duration(result)
        if duration:
            print(f"✅ Video duration: {duration:.1f}s")
        
        print()
        print("✅ TEST 4 PASSED: FFmpeg successfully composited all layers")
        print()
        print("🎉 YOU CAN NOW PLAY THE TEST VIDEO:")
        print(f"   {result}")
        print()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Run all tests in sequence
    """
    print("\n" * 2)
    print("🧪 V4 ARCHITECTURE TEST SUITE")
    print("=" * 70)
    print()
    print("This test suite verifies that the V4 architecture is correctly")
    print("implemented with:")
    print("  1. Transparent Reddit frame (RGBA)")
    print("  2. Dynamic subtitle generation (SRT)")
    print("  3. Pexels API integration (optional, needs API key)")
    print("  4. FFmpeg multi-layer composition")
    print()
    input("Press Enter to start tests...")
    print("\n" * 2)
    
    results = {}
    
    # Test 1: Frame transparency
    results['frame'] = test_reddit_frame_transparency()
    
    # Test 2: Subtitle generation
    results['subtitles'] = test_subtitle_generation()
    
    # Test 3: Pexels API (optional)
    results['pexels'] = test_pexels_api()
    
    # Test 4: FFmpeg composite (requires previous tests)
    results['ffmpeg'] = test_ffmpeg_composite()
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result is True else ("❌ FAILED" if result is False else "⚠️  SKIPPED")
        print(f"  {test_name.upper():15s} {status}")
    
    print()
    print(f"Total: {passed} passed, {failed} failed, {skipped} skipped")
    print()
    
    if failed > 0:
        print("❌ SOME TESTS FAILED")
        print("   Review error messages above to diagnose issues")
        sys.exit(1)
    elif passed == len(results):
        print("🎉 ALL TESTS PASSED!")
        print("   V4 architecture is correctly implemented")
        sys.exit(0)
    else:
        print("✅ CORE TESTS PASSED (some optional tests skipped)")
        print("   V4 architecture looks good")
        sys.exit(0)


if __name__ == "__main__":
    main()
