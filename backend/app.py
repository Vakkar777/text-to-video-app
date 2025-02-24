from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import uuid

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

UPLOAD_FOLDER = 'generated_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_video(prompt):
    # Use Stable Video Diffusion (simplified example)
    video_id = str(uuid.uuid4())
    output_path = os.path.join(UPLOAD_FOLDER, f"{video_id}.mp4")
    
    # Replace this with your actual model code (see Step 4)
    # For now, create a dummy video using FFmpeg
    subprocess.run(f"ffmpeg -f lavfi -i testsrc=duration=5:size=640x480:rate=30 {output_path}", shell=True)
    
    return output_path

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    video_path = generate_video(prompt)
    return jsonify({'video_url': f'/video/{os.path.basename(video_path)}'})

@app.route('/video/<filename>')
def get_video(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
