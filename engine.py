import os
import json
import shutil
import whisper
import PIL.Image
from gtts import gTTS
from gradio_client import Client
from google import genai
from google.genai import types
import urllib.request
import urllib.parse
import time
                                  
from moviepy.config import change_settings
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, concatenate_audioclips

                                
change_settings({"IMAGEMAGICK_BINARY": r"c:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

                                   
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from dotenv import load_dotenv
load_dotenv()

class MultiSceneVideoPipeline:
    def __init__(self, raw_idea, output_file="multi_scene_output.mp4"):
        self.raw_idea = raw_idea
        self.output_file = output_file
        
                          
        self.scenes_data = []
        self.video_clips = []
        self.audio_clips = []
        
                                      
        self.temp_dir = "pipeline_temp"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def step_0_generate_storyboard(self):
        """
        Objective: Deconstruct a raw idea into an explicit, multi-scene storyboard.
        Reasoning: Linear structure eliminates monotony. Each array item represents a unique shot.
        """
        print("\n[0/4] Directing Storyboard with Gemini API...")
        if "GEMINI_API_KEY" not in os.environ:
            raise ValueError("GEMINI_API_KEY missing from environment variables.")
            
        client = genai.Client()
        
        system_prompt = f"""
        Convert this video concept into an engaging 3-scene historical documentary script.
        Concept: {self.raw_idea}
        
        Return a strict JSON array containing exactly 3 objects. Each object MUST have these two keys:
        "script": A single, impactful sentence spoken by the narrator.
        "visual_prompt": A highly detailed, descriptive image prompt for an AI generator.
        
        CRITICAL RULES FOR OUTPUT:
        1. Return ONLY raw, valid JSON.
        2. Do NOT wrap the output in ```json or ``` markdown blocks.
        3. Do NOT include trailing commas at the end of lists or objects.
        4. Do NOT include any comments or introductory text.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
                                                                                 
        clean_text = response.text.strip()
        
                                                                            
        if clean_text.startswith("```"):
            clean_text = "\n".join(clean_text.split("\n")[1:-1]).strip()
            
                                  
        self.scenes_data = json.loads(clean_text, strict=False)
        print(f"      -> Successfully structured {len(self.scenes_data)} cinematic scenes.")

    def step_1_process_individual_scenes(self):
        """
        Objective: Render unique assets for every block on the timeline independently.
        Reasoning: Keeps voice and visuals perfectly locked per segment, avoiding drift.
        """
        if "HF_TOKEN" not in os.environ:
            raise ValueError("HF_TOKEN missing from environment variables.")
            
        whisper_model = whisper.load_model("tiny")
                                                        
        
        
        for index, scene in enumerate(self.scenes_data):
            print(f"\n--- Processing Scene {index + 1} of {len(self.scenes_data)} ---")
            
                               
            scene_voice_path = os.path.join(self.temp_dir, f"voice_{index}.mp3")
            scene_img_path = os.path.join(self.temp_dir, f"image_{index}.webp")
            
                                          
            print("   -> Generating Scene Voiceover...")
            tts = gTTS(text=scene["script"], lang='en')
            tts.save(scene_voice_path)
            
                                                                             
            scene_audio_clip = AudioFileClip(scene_voice_path)
            scene_duration = scene_audio_clip.duration
            
                                                                     
            print("   -> Requesting Cloud Art Assets...")
            
                                                    
            safe_prompt = urllib.parse.quote(scene["visual_prompt"])
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=576&nologo=true"
            
            req = urllib.request.Request(
                image_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            try:
                                                        
                with urllib.request.urlopen(req, timeout=15) as response, open(scene_img_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                print(f"      ⚠️ Primary image generation failed ({e}). Trying fallback prompt...")
                try:
                                                                                                             
                    with urllib.request.urlopen(req, timeout=45) as response, open(scene_img_path, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)
                except Exception as e2:
                    print(f"      ⚠️ Retry failed ({e2}). Resting for 5 seconds before final retry...")
                                                                                                                 
                    time.sleep(5)

                    try:
                        with urllib.request.urlopen(req, timeout=45) as response, open(scene_img_path, 'wb') as out_file:
                            shutil.copyfileobj(response, out_file)
                    except Exception as e3:
                        print(f"      🚨 Cloud API entirely unreachable ({e3}). Generating localized visual canvas asset...")
                        fallback_canvas = PIL.Image.new('RGB', (1024, 576), color=(30, 32, 38))
                        fallback_canvas.save(scene_img_path)

                                                              
            base_image = ImageClip(scene_img_path).resize(width=1280)
            
            
            def render_pan(get_frame, t):
                                                                                       
                scale = 1.0 + (0.08 * (t / scene_duration))
                w, h = base_image.size
                x1, y1 = int((w - w/scale)/2), int((h - h/scale)/2)
                x2, y2 = int(w - x1), int(h - y1)
                return get_frame(t)[y1:y2, x1:x2]
            
            scene_video_clip = base_image.set_duration(scene_duration).fl(render_pan).resize((1280, 720))
            
                                                                                                         
            scene_video_clip = scene_video_clip.set_audio(scene_audio_clip)

                                         
            print("   -> Aligning Local Subtitles...")
            whisper_res = whisper_model.transcribe(scene_voice_path)
            subtitle_clips = []
            
            for segment in whisper_res["segments"]:
                txt_clip = TextClip(segment["text"].strip(), fontsize=44, color='white', font='Arial-Bold', 
                                    bg_color='rgba(0,0,0,0.6)', method='caption', size=(900, None))
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(segment["start"]).set_end(segment["end"])
                subtitle_clips.append(txt_clip)
            
                                                                          
            scene_composite = CompositeVideoClip([scene_video_clip] + subtitle_clips)
            scene_composite = scene_composite.set_audio(scene_audio_clip)
                                                   
            self.video_clips.append(scene_composite)
            self.audio_clips.append(scene_audio_clip)
            
                                                                 
            if index < len(self.scenes_data) - 1:
                print("   -> Pacing API requests (sleeping for 15 seconds)...")
                time.sleep(15)

    def step_2_stitch_timeline(self):
        """
        Objective: Concatenate distinct scene visual chunks into one coherent track.
        """
        print("\n[3/4] Compiling Global Structural Timeline...")
        
                                                   
        final_video = concatenate_videoclips(self.video_clips, method="compose")
        
                                                                                         
        master_audio = concatenate_audioclips(self.audio_clips)
        
                                                                     
        final_video = final_video.set_audio(master_audio)
        
        print("[4/4] Encoding Master Video File...")
        final_video.write_videofile(
            self.output_file, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            remove_temp=True,
            ffmpeg_params=["-pix_fmt", "yuv420p"]
        )
        
                                                                
        final_video.close()
        master_audio.close()
        for clip in self.video_clips: clip.close()
        for audio in self.audio_clips: audio.close()

    def run(self):
        try:
            self.step_0_generate_storyboard()
            self.step_1_process_individual_scenes()
            self.step_2_stitch_timeline()
            print(f"\n✅ Pipeline Complete! Output generated at: {self.output_file}")
            
                                                                          
            return self.output_file 
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            return None
        finally:
                                             
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)