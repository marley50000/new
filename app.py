from flask import Flask, send_from_directory, request, jsonify, abort
import os
import cv2
import numpy as np
import sys

# Ensure the flash_tag directory is in the path for imports
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from flash_tag.detector import FlashTagDetector

app = Flask(__name__, static_folder='static')
detector = FlashTagDetector()

@app.route('/')
def index():
    # Priority for serving the main page
    entry_points = ['index.html', 'auth.html', 'Homepage.html']
    for filename in entry_points:
        full_path = os.path.join(base_dir, filename)
        if os.path.exists(full_path):
            return send_from_directory(base_dir, filename)

    return "No entry point (index.html, auth.html, etc.) found in the root directory.", 404

@app.route('/flashtag')
def flashtag_demo():
    return send_from_directory(os.path.join(base_dir, 'static'), 'flashtag_demo.html')

@app.route('/favicon.ico')
def favicon():
    # Serve from static or return 204 No Content to avoid 404 errors in console
    favicon_path = os.path.join(base_dir, 'static', 'favicon.ico')
    if os.path.exists(favicon_path):
        return send_from_directory(os.path.join(base_dir, 'static'), 'favicon.ico')
    return '', 204

@app.route('/detect_flashtag', methods=['POST'])
def detect_flashtag():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Invalid image'}), 400

    tags = detector.detect(img)
    results = [{'id': tag['id'], 'center': tag['center']} for tag in tags]
    return jsonify({'tags': results})

@app.route('/<path:filename>')
def serve_file(filename):
    # Try root directory
    root_path = os.path.join(base_dir, filename)
    if os.path.exists(root_path) and os.path.isfile(root_path):
        # Security: Do not serve .py files, .db files, or hidden files
        if filename.endswith(('.py', '.pyc', '.db', '.git')) or filename.startswith('.'):
            return abort(403)
        return send_from_directory(base_dir, filename)

    # Try static directory
    static_path = os.path.join(base_dir, 'static', filename)
    if os.path.exists(static_path) and os.path.isfile(static_path):
        return send_from_directory(os.path.join(base_dir, 'static'), filename)

    return abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Using threaded=True to handle multiple requests (like favicon + html) smoothly
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
