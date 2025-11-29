from flask import Flask, request, jsonify
import logging
from datetime import datetime
import math

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

vehicles_status = {}
location_history = []
ZONES = {
    "downtown": {"min_lat": 40.70, "max_lat": 40.75, "min_lng": -74.00, "max_lng": -73.98},
    "airport": {"min_lat": 40.63, "max_lat": 40.65, "min_lng": -73.78, "max_lng": -73.76},
    "suburbs": {"min_lat": 40.80, "max_lat": 40.85, "min_lng": -73.90, "max_lng": -73.85}
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

def is_point_in_zone(lat, lng, zone):
    """Check if a point is inside a rectangular zone"""
    return (zone['min_lat'] <= lat <= zone['max_lat'] and 
            zone['min_lng'] <= lng <= zone['max_lng'])

def detect_zone(lat, lng):
    """Detect which zone a point is in, returns zone name or None"""
    for zone_name, zone_bounds in ZONES.items():
        if is_point_in_zone(lat, lng, zone_bounds):
            return zone_name
    return None

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate simple Euclidean distance between two points"""
    return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2)

@app.route('/location', methods=['POST'])
def receive_location():
    """
    Receive vehicle location updates
    Expected JSON payload:
    {
        "vehicle_id": "vehicle_123",
        "latitude": 40.71,
        "longitude": -73.99,
        "timestamp": "2023-10-01T12:00:00Z"
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['vehicle_id', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        vehicle_id = data['vehicle_id']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        current_zone = detect_zone(latitude, longitude)
        
        previous_status = vehicles_status.get(vehicle_id, {})
        previous_zone = previous_status.get('current_zone')
        
        event_response = {
            "vehicle_id": vehicle_id,
            "timestamp": timestamp,
            "current_zone": current_zone,
            "event_type": "location_update"
        }
        
        if previous_zone != current_zone:
            if previous_zone is None and current_zone is not None:
                event_response["event_type"] = "zone_entered"
                event_response["zone_entered"] = current_zone
                logger.info(f"Vehicle {vehicle_id} entered zone {current_zone}")
                
            elif previous_zone is not None and current_zone is None:
                event_response["event_type"] = "zone_exited" 
                event_response["zone_exited"] = previous_zone
                logger.info(f"Vehicle {vehicle_id} exited zone {previous_zone}")
                
            elif previous_zone is not None and current_zone is not None and previous_zone != current_zone:
                event_response["event_type"] = "zone_changed"
                event_response["zone_exited"] = previous_zone
                event_response["zone_entered"] = current_zone
                logger.info(f"Vehicle {vehicle_id} changed from {previous_zone} to {current_zone}")
        
        vehicles_status[vehicle_id] = {
            'current_zone': current_zone,
            'last_latitude': latitude,
            'last_longitude': longitude,
            'last_update': timestamp,
            'vehicle_id': vehicle_id
        }
        
        location_history.append({
            'vehicle_id': vehicle_id,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timestamp,
            'zone': current_zone
        })
        
        if len(location_history) > 1000:
            location_history.pop(0)
        
        return jsonify(event_response), 200
        
    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/vehicles/<vehicle_id>/status', methods=['GET'])
def get_vehicle_status(vehicle_id):
    """Get current zone status for a vehicle"""
    if vehicle_id not in vehicles_status:
        return jsonify({"error": "Vehicle not found"}), 404
    
    status = vehicles_status[vehicle_id]
    return jsonify({
        "vehicle_id": vehicle_id,
        "current_zone": status['current_zone'],
        "last_location": {
            "latitude": status['last_latitude'],
            "longitude": status['last_longitude']
        },
        "last_update": status['last_update']
    })

@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    """Get status for all vehicles"""
    return jsonify({
        "vehicles": list(vehicles_status.values()),
        "total_vehicles": len(vehicles_status)
    })

@app.route('/zones', methods=['GET'])
def get_zones():
    """Get all defined zones"""
    return jsonify({"zones": ZONES})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)