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
    # Try common entry points
    for filename in ['index.html', 'auth.html', 'Homepage.html']:
        if os.path.exists(os.path.join(base_dir, filename)):
            print(f"Serving {filename} from root")
            return send_from_directory(base_dir, filename)

    # Fallback to static
    if os.path.exists(os.path.join(base_dir, 'static', 'auth.html')):
        print("Serving auth.html from static")
        return send_from_directory(os.path.join(base_dir, 'static'), 'auth.html')

    return "No entry point (index.html, auth.html, etc.) found in root or static/ folder.", 404

@app.route('/flashtag')
def flashtag_demo():
    return send_from_directory(os.path.join(base_dir, 'static'), 'flashtag_demo.html')

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
    # Try root first
    if os.path.exists(os.path.join(base_dir, filename)):
        # Basic security: don't serve .py files or hidden files
        if filename.endswith('.py') or filename.startswith('.'):
            return abort(403)
        return send_from_directory(base_dir, filename)

    # Try static
    if os.path.exists(os.path.join(base_dir, 'static', filename)):
        return send_from_directory(os.path.join(base_dir, 'static'), filename)

    return abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
