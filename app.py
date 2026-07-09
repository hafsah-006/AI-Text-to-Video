import gradio as gr
from engine import MultiSceneVideoPipeline

def generate_my_video(user_idea):
    """
    This function bridges the UI and your backend engine.
    It takes the text from the Gradio textbox, feeds it to your pipeline,
    and returns the final .mp4 file to the Gradio video player.
    """
    output_name = "final_render.mp4"
    
    pipeline = MultiSceneVideoPipeline(raw_idea=user_idea, output_file=output_name)
    
    final_video_path = pipeline.run()
    
    return final_video_path

#  UI 
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 AI Documentary Director")
    gr.Markdown("Type a concept below. The AI will write a 3-scene script, generate cinematic assets, synthesize voiceover, align subtitles, and render a final video.")
    
    with gr.Row():
        with gr.Column(scale=1):
            idea_input = gr.Textbox(
                label="What should the video be about?", 
                placeholder="e.g., The architecture of the first programmable computer...",
                lines=4
            )
            generate_btn = gr.Button("Generate Video", variant="primary")
            
        with gr.Column(scale=1):
            video_output = gr.Video(label="Final Output")

    # Link the button to the function
    generate_btn.click(
        fn=generate_my_video,
        inputs=idea_input,
        outputs=video_output
    )

# Launch the app!
if __name__ == "__main__":
    demo.launch()