from flask import Flask, send_from_directory, jsonify, request
from trotro_router import TrotroRouter

app = Flask(__name__, static_folder='static')
router = TrotroRouter()

# Serve main page (default to trotro route planner)
@app.route('/')
def index():
    return send_from_directory('static', 'trotro.html')

# Serve trotro map interface
@app.route('/trotro')
def trotro_ui():
    return send_from_directory('static', 'trotro.html')

# API Endpoints
@app.route('/api/trotro/stops', methods=['GET'])
def get_stops():
    """Get list of all trotro stops, optionally filtered by city or query"""
    city = request.args.get('city')
    query = request.args.get('q', '').lower()

    stops = list(router.stops.values())
    if city:
        stops = [s for s in stops if s['city'].lower() == city.lower()]
    if query:
        stops = [s for s in stops if query in s['name'].lower() or query in s['city'].lower()]

    return jsonify({"status": "success", "count": len(stops), "stops": stops})

@app.route('/api/trotro/routes', methods=['GET'])
def get_routes():
    """Get list of all trotro routes"""
    routes = list(router.routes.values())
    return jsonify({"status": "success", "count": len(routes), "routes": routes})

@app.route('/api/trotro/nearest_stop', methods=['GET'])
def nearest_stop():
    """Find nearest trotro pickup stop to given lat/lng"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Valid lat and lng query params are required"}), 400

    stops = router.find_nearest_stop(lat, lng, limit=5)
    return jsonify({"status": "success", "nearest_stops": stops})

@app.route('/api/trotro/route', methods=['POST'])
def calculate_route():
    """
    Calculate trotro route given JSON body:
    { "origin": {"lat": 5.5, "lng": -0.2}, "destination": {"lat": 5.6, "lng": -0.1} }
    OR
    { "origin_stop_id": "acc_circle", "dest_stop_id": "acc_madina" }
    """
    data = request.get_json() or {}

    if "origin_stop_id" in data and "dest_stop_id" in data:
        result = router.find_route_by_stop_ids(data["origin_stop_id"], data["dest_stop_id"])
    elif "origin" in data and "destination" in data:
        orig = data["origin"]
        dest = data["destination"]
        if "lat" not in orig or "lng" not in orig or "lat" not in dest or "lng" not in dest:
            return jsonify({"status": "error", "message": "Origin and Destination must include lat and lng"}), 400
        result = router.find_route_by_coords(orig["lat"], orig["lng"], dest["lat"], dest["lng"])
    else:
        return jsonify({"status": "error", "message": "Please provide origin and destination coordinates or stop IDs"}), 400

    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 404

    return jsonify({"status": "success", "journey": result})

# Serve other HTML/static files
@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
