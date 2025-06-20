from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

# Serve the main page
@app.route('/')
def index():
    return send_from_directory('static', 'auth.html')

# Serve other HTML pages if needed
@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
