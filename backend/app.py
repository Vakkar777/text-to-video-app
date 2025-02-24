from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from diffusers import StableVideoDiffusionPipeline  # <-- Add this
import torch  # <-- Add this

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'generated_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_video(prompt):
    # Initialize the Stable Video Diffusion pipeline
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion",
        torch_dtype=torch.float16,
        variant="fp16"
    )
    
    # Offload the model to the GPU (if available)
    if torch.cuda.is_available():
        pipe.enable_model_cpu_offload()
    else:
        raise RuntimeError("GPU not available. This model requires a GPU.")

    # Generate frames
    frames = pipe(prompt, num_frames=24, decode_chunk_size=8).frames[0]

    # Save the video
    video_id = str(uuid.uuid4())
    output_path = os.path.join(UPLOAD_FOLDER, f"{video_id}.mp4")
    
    # Save frames as an MP4 (example uses PIL's save method)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,  # Adjust duration between frames (in milliseconds)
        loop=0
    )

    return output_path

# Keep the rest of the Flask routes (e.g., /generate, /video/<filename>)
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    try:
        video_path = generate_video(prompt)
        return jsonify({'video_url': f'/video/{os.path.basename(video_path)}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video/<filename>')
def get_video(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
