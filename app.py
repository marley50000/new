from flask import Flask, send_from_directory, request, jsonify, abort
import os
import cv2
import numpy as np
from flash_tag.detector import FlashTagDetector

app = Flask(__name__, static_folder='static')
detector = FlashTagDetector()

# Serve the main page
@app.route('/')
def index():
    # Only allow serving index.html or auth.html
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
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

# Restrict file serving to static directory
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # Default to 5000 for standard environments, 3000 if configured otherwise via env var
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
