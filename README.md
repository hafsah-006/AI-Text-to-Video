# 🎬 AI Documentary Director

An automated, end-to-end Python pipeline that transforms a single text prompt into a fully produced, multi-scene documentary video. 

Powered by **Gemini 2.5 Flash** (scriptwriting), **Pollinations.ai** (image generation), **gTTS** (voiceover synthesis), and **OpenAI Whisper** (subtitle transcription/alignment), this tool handles scriptwriting, image generation, voiceover synthesis, dynamic subtitle alignment, and video compositing—all orchestrated through a minimalist Gradio web interface.

## ✨ Features
* **Automated Storyboarding:** Gemini instantly breaks down high-level concepts into a structured 3-scene narrative with calculated visual prompts.
* **Resilient Cloud Asset Fetching:** Automatically paces API requests to avoid rate limits and features a graceful fallback system that generates dark-aesthetic local canvases if the image server goes down.
* **Dynamic Audio/Text Syncing:** Leverages OpenAI Whisper to transcribe generated voiceovers and precision-sync subtitles to the visual timeline.
* **Cinematic Ken Burns Effect:** Applies dynamic zooming/panning algorithms to still images to create engaging, documentary-style motion.
* **Web UI:** A clean, local Gradio dashboard to direct and preview your renders.

## 🧠 System Architecture
The backend (`engine.py`) executes a strict linear pipeline:
1. **Step 0 (Directing):** Prompts Gemini to output a strict JSON storyboard.
2. **Step 1 (Asset Generation):** Loops through scenes to request TTS audio and high-res cloud images.
3. **Step 2 (Compositing):** Aligns the Ken Burns visual clips with the TTS audio and overlays Whisper-timed text clips.
4. **Step 3 (Stitching):** Concatenates all composited scenes and master audio tracks into a standard `yuv420p` MP4 file for universal playback.

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/hafsah-006/AI-Text-to-Video.git
cd AI-Text-to-Video
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```
The project also relies on a few packages that aren't yet pinned in `requirements.txt` — install these as well:
```bash
pip install gTTS gradio_client google-genai python-dotenv
```

**3. Install system-level dependencies**
* **FFmpeg** — required by `moviepy` for encoding/decoding video and audio.
  * macOS: `brew install ffmpeg`
  * Ubuntu/Debian: `sudo apt install ffmpeg`
  * Windows: [download a build](https://ffmpeg.org/download.html) and add it to your `PATH`.
* **ImageMagick** — required by `moviepy`'s `TextClip` to render subtitles.
  * Download from [imagemagick.org](https://imagemagick.org/script/download.php).
  * `engine.py` currently hardcodes a Windows install path:
```python
    change_settings({"IMAGEMAGICK_BINARY": r"c:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})
```
    If you're on macOS/Linux, or installed ImageMagick to a different path, update this line to point at your local `magick`/`convert` binary.

**4. Configure environment variables**

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
HF_TOKEN=your_hugging_face_token_here
```
* `GEMINI_API_KEY` — used to call the Gemini 2.5 Flash model that writes the 3-scene storyboard. Get one from [Google AI Studio](https://aistudio.google.com/).
* `HF_TOKEN` — a Hugging Face access token, checked at startup of the asset-generation step. Get one from your [Hugging Face account settings](https://huggingface.co/settings/tokens).

**5. Run the app**
```bash
python app.py
```
Gradio will launch a local web server (by default at `http://127.0.0.1:7860`). Open it in your browser, type in a video concept, and click **Generate Video**.

## 🖥️ Usage

1. Enter a concept in the text box, e.g. *"The architecture of the first programmable computer."*
2. Click **Generate Video**.
3. The pipeline runs through four stages (storyboarding, per-scene asset generation, compositing, stitching) with progress logged to the console.
4. Once complete, the rendered MP4 appears in the **Final Output** video player and is saved locally as `final_render.mp4`.

A full run typically takes a few minutes, since each scene's image request is deliberately rate-limited (a ~15 second pause between scenes) to avoid overloading the Pollinations.ai API.

## 📁 Project Structure
```
AI-Text-to-Video/
├── app.py              # Gradio UI — collects the prompt and displays the final video
├── engine.py           # Core MultiSceneVideoPipeline: storyboarding, assets, compositing, stitching
├── requirements.txt     # Python dependencies
└── .gitignore
```

## ⚙️ How It Works, In Detail

| Stage | What happens |
|---|---|
| **Storyboard** | `raw_idea` is sent to Gemini 2.5 Flash, which returns a strict JSON array of 3 scenes, each with a `script` line and a `visual_prompt`. |
| **Voiceover** | Each scene's script is synthesized to speech with `gTTS` and saved as an MP3. |
| **Visuals** | Each scene's `visual_prompt` is URL-encoded and sent to `image.pollinations.ai`. If the request fails, it retries with increasing timeouts, then falls back to a plain dark-colored placeholder canvas so the pipeline never hard-fails. |
| **Motion** | A subtle Ken Burns zoom is applied to each still image over the duration of its voiceover clip. |
| **Subtitles** | OpenAI Whisper (`tiny` model) transcribes each scene's voiceover locally, and the resulting timed segments are rendered as captions synced to the audio. |
| **Compositing** | Each scene's video, audio, and subtitle clips are composited together. |
| **Stitching** | All scenes are concatenated into a single timeline, encoded as `yuv420p` H.264 MP4 with AAC audio, and temp files are cleaned up. |

## ⚠️ Notes & Limitations
* The image generation step depends on the free Pollinations.ai service — availability and generation speed aren't guaranteed, hence the built-in retry/fallback logic.
* Whisper's `tiny` model favors speed over transcription accuracy; larger models can be swapped in `engine.py` if subtitle precision matters more than render time.
* The ImageMagick path in `engine.py` is hardcoded for Windows and will need to be edited for other operating systems (see Setup step 3 above).
* Generated MP4s and temporary pipeline assets are excluded from version control via `.gitignore`.

## 🤝 Contributing
Issues and pull requests are welcome. If you spot a bug in the pipeline or want to extend it (more scenes, different TTS voices, alternate image providers), feel free to open a PR.

## 📄 License
No license file is currently included in this repository. Add one (e.g., MIT) if you intend for others to reuse this code.
