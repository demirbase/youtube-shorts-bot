# video_assembler_v2.py
# V2 video assembly using MoviePy for complex overlays

from moviepy.editor import *
import os

def assemble_short_video(
    background_clip_path: str,
    audio_clips_paths: list,
    image_clips_paths: list,
    output_path: str = "final_short.mp4"
) -> str | None:
    """
    Assembles the final Short video using MoviePy.
    
    Args:
        background_clip_path: Path to background video file
        audio_clips_paths: List of paths to audio files ["title_audio.wav", "comment1_audio.wav"]
        image_clips_paths: List of paths to overlay images ["title.png", "comment_1.png"]
        output_path: Path for output video
        
    Returns:
        Path to created video, or None on failure
    """
    print("🎬 Assembling final video with MoviePy...")
    
    try:
        # 1. Load all audio clips and get their durations
        print("   Loading audio clips...")
        audio_segments = [AudioFileClip(f) for f in audio_clips_paths]
        durations = [seg.duration for seg in audio_segments]
        total_duration = sum(durations)
        
        print(f"   Total duration: {total_duration:.2f}s")
        
        # 2. Load and prepare background video
        print("   Preparing background video...")
        bg = VideoFileClip(background_clip_path)
        
        # Loop if needed to match audio duration
        if bg.duration < total_duration:
            bg = bg.loop(duration=total_duration)
        else:
            bg = bg.subclip(0, total_duration)
        
        # Crop to 9:16 aspect ratio (1080x1920 for Shorts)
        (w, h) = bg.size
        target_aspect = 9/16  # width/height for vertical video
        
        # Calculate crop dimensions
        if w/h > target_aspect:
            # Video is too wide, crop width
            crop_width = int(h * target_aspect)
            x_center = w/2
            bg_cropped = bg.fx(vfx.crop, x_center=x_center, width=crop_width, height=h)
        else:
            # Video is too tall, crop height
            crop_height = int(w / target_aspect)
            y_center = h/2
            bg_cropped = bg.fx(vfx.crop, y_center=y_center, width=w, height=crop_height)
        
        # Resize to final dimensions
        bg_final = bg_cropped.resize((1080, 1920))

        # 3. Create overlay clips for each image
        print("   Creating overlay clips...")
        overlay_clips = []
        current_time = 0
        
        for i, img_path in enumerate(image_clips_paths):
            if i >= len(durations):
                print(f"   ⚠️  Warning: More images than audio clips, skipping {img_path}")
                break
                
            # Load image and set properties
            clip = (ImageClip(img_path)
                   .set_duration(durations[i])
                   .set_start(current_time)
                   .set_position(("center", "center"))
                   .resize(width=950))  # Ensure images fit in 1080 width
            
            overlay_clips.append(clip)
            current_time += durations[i]
            print(f"   Added overlay {i+1}/{len(image_clips_paths)}: {durations[i]:.2f}s")
        
        # 4. Concatenate all audio
        print("   Combining audio tracks...")
        final_audio = concatenate_audioclips(audio_segments)

        # 5. Composite everything: background + overlays
        print("   Compositing video layers...")
        final_video = CompositeVideoClip(
            [bg_final] + overlay_clips,
            size=(1080, 1920)
        ).set_audio(final_audio).set_duration(total_duration)

        # 6. Write the final file
        print(f"   Writing final video to {output_path}...")
        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,
            preset="medium",
            threads=4
        )
        
        # Clean up clips
        for clip in audio_segments:
            clip.close()
        bg.close()
        final_video.close()
        
        print(f"✅ Final Short successfully created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error assembling video: {e}")
        import traceback
        traceback.print_exc()
        return None


def quick_assemble_simple(
    background_video: str,
    audio_file: str,
    text_overlay: str,
    output_path: str = "output.mp4"
) -> str | None:
    """
    Simplified assembly for quick testing.
    
    Args:
        background_video: Path to background video
        audio_file: Path to single audio file
        text_overlay: Text to display as simple overlay
        output_path: Output file path
        
    Returns:
        Path to created video, or None on failure
    """
    try:
        # Load components
        bg = VideoFileClip(background_video)
        audio = AudioFileClip(audio_file)
        
        # Crop and resize background
        (w, h) = bg.size
        crop_width = int(h * (9/16))
        bg_cropped = bg.fx(vfx.crop, x_center=w/2, width=crop_width)
        bg_final = bg_cropped.resize((1080, 1920)).subclip(0, audio.duration)
        
        # Create text clip
        txt_clip = (TextClip(text_overlay, fontsize=40, color='white', 
                            font='Arial-Bold', size=(1000, None))
                   .set_position('center')
                   .set_duration(audio.duration))
        
        # Composite and add audio
        final = CompositeVideoClip([bg_final, txt_clip]).set_audio(audio)
        
        # Export
        final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
        
        print(f"✅ Video created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
