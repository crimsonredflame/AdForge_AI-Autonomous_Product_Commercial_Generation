import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip, AudioFileClip
import os
import requests

def generate_voiceover(target_path="voiceover.mp3"):
    """Pings ElevenLabs to generate a cinematic narrator voiceover."""
    if os.path.exists(target_path):
        print("🎙️ Using cached voiceover track...")
        return True
        
    print("🎙️ Generating cinematic voiceover via ElevenLabs...")
    
    api_key = "sk_4c795a794e5962319805dd513d45bb732d020f6db29f7cb0" 
    
    voice_id = "9TtqcvK8HhZVwt6fJY2Y"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": "The Nike Revolution. Lightweight design. Maximum comfort. Step into the future.",
        "model_id": "eleven_multilingual_v2", # <-- This is the only line that changed
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(response.content)
            print(" Voiceover generated and saved locally!")
            return True
        else:
            print(f" ElevenLabs API Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f" Could not generate voiceover: {e}")
    return False

def build_commercial(v, p, f, o):
    c = []
    for path in v:
        cl = VideoFileClip(path).resize(height=1080).crossfadein(0.5).crossfadeout(0.5)
        c.append(cl)

    # 1. Stitch video clips together
    s = concatenate_videoclips(c, padding=-0.5, method="compose")

    # 2. Create the Main Title using Bebas Neue
    t = TextClip(p, fontsize=70, color='white', font='BebasNeue-Regular.ttf', stroke_color='black', stroke_width=2)
    t = t.set_position(('center', 50)).set_duration(s.duration).crossfadein(1.0)

    # 3. Create the Lower-Third Background Box
    b = ColorClip(size=(s.w, 120), color=(0,0,0)).set_opacity(0.6).set_position(('center', 'bottom')).set_duration(s.duration - 1).set_start(1)
    
    # 4. Create the Flowing Details Text
    d = TextClip(f, fontsize=40, color='white', font='BebasNeue-Regular.ttf')
    d = d.set_position(('center', s.h - 80)).set_start(1).set_duration(s.duration - 1).crossfadein(1.0)

    # 5. Composite visual layers together
    fv = CompositeVideoClip([s, t, b, d])

    # 6. Auto-fetch and inject Voiceover
    if generate_voiceover("voiceover.mp3"):
        print("🎙️ Syncing voiceover to the timeline...")
        audio = AudioFileClip("voiceover.mp3")
        
        # If the VO is longer than the video, cut it. If the video is longer, let the VO play and fade out.
        if audio.duration > s.duration:
            audio = audio.subclip(0, s.duration)
            
        fv = fv.set_audio(audio)
    else:
        print(" Rendering silent video due to missing audio stream.")

    # 7. Render final file
    fv.write_videofile(o, fps=8, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    r = ["AnimateDiff_00001.gif", "AnimateDiff_00002.gif", "AnimateDiff_00003.gif", "AnimateDiff_00004.gif", "AnimateDiff_00005.gif"] 
    if all(os.path.exists(i) for i in r):
        build_commercial(r, "NIKE REVOLUTION", "Lightweight Design | Maximum Comfort", "Final_Commercial.mp4")
