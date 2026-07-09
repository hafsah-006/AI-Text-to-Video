# 🎬 AI Documentary Director

An automated, end-to-end Python pipeline that transforms a single text prompt into a fully produced, multi-scene documentary video. 

Powered by **Gemini 2.5 Flash**, **Pollinations.ai**, and **OpenAI Whisper**, this tool handles scriptwriting, image generation, voiceover synthesis, dynamic subtitle alignment, and video compositing—all orchestrated through a minimalist Gradio web interface.

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
git clone [https://github.com/YOUR_USERNAME/ai-video-director.git](https://github.com/YOUR_USERNAME/ai-video-director.git)
cd ai-video-director