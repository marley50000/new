from flask import Flask, send_from_directory, request, jsonify
import os
import cv2
import numpy as np
from flash_tag.detector import FlashTagDetector

app = Flask(__name__, static_folder='static')
detector = FlashTagDetector()

# Serve the main page
@app.route('/')
def index():
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    elif os.path.exists('auth.html'):
        return send_from_directory('.', 'auth.html')
    return send_from_directory('static', 'auth.html')

# Serve the FlashTag demo
@app.route('/flashtag')
def flashtag_demo():
    return send_from_directory('static', 'flashtag_demo.html')

# API for FlashTag detection
@app.route('/detect_flashtag', methods=['POST'])
def detect_flashtag():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Read image from stream
    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Invalid image'}), 400

    tags = detector.detect(img)

    # Format results for JSON
    results = []
    for tag in tags:
        results.append({
            'id': tag['id'],
            'center': tag['center']
        })

    return jsonify({'tags': results})

# Safe file serving for assets
@app.route('/<path:filename>')
def serve_file(filename):
    # Try serving from static first, then from root (only allowed files)
    if os.path.exists(os.path.join('static', filename)):
        return send_from_directory('static', filename)

    # List of allowed files in root
    allowed_root_files = [
        'index.html', 'auth.html', 'login.html', 'chatbot.html',
        'user_chat.html', 'img.html', 'Homepage.html',
        'Registration As Agent.html', 'Registration old.html',
        'Chat function.html', 'trial form.html'
    ]
    if filename in allowed_root_files and os.path.exists(filename):
        return send_from_directory('.', filename)

    # Serve media files from root
    if filename.endswith(('.mp4', '.png', '.jpg', '.jpeg', '.svg')):
        if os.path.exists(filename):
            return send_from_directory('.', filename)

    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
