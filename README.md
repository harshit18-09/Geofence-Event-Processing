# Geofence Event Processing System

A real-time location-based service for tracking vehicles and detecting geographic zone crossings. Built for a taxi company to monitor vehicle movements through predefined geographic zones.

##  Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Running

1. **Clone or download the project files**
   - `app.py` (main application)
   - `requirements.txt` (dependencies)

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```
   python app.py
   ```
4. **The service will start on:**
   ```
    http://localhost:5000
   ```
## API Endpoints
1. **POST /location**
- Submit vehicle location updates and receive zone transition events.
- Request-
   ```
   {
      "vehicle_id": "taxi_123",
      "latitude": 40.71,
       "longitude": -73.99,
       "timestamp": "2023-10-01T12:00:00Z"
   }
   ```
- Response-
   ```
   {
       "vehicle_id": "taxi_123",
       "timestamp": "2023-10-01T12:00:00Z",
       "current_zone": "downtown",
       "event_type": "zone_entered",
       "zone_entered": "downtown"
   }
   ```

2. **GET /vehicles/<vehicle_id>/status**
- Get current zone status and last known location for a specific vehicle.
- Response-
   ```
   {
      "vehicle_id": "taxi_123",
      "current_zone": "downtown",
      "last_location": {
      "latitude": 40.71,
      "longitude": -73.99
    },
    "last_update": "2023-10-01T12:00:00Z"
   }
   ```
3. **GET /vehicles**
- Get status for all tracked vehicles.
4. **GET /zones**
- Get all defined geographic zones with their boundaries.
5. **GET /health**
- Health check endpoint to verify service status.

## Defined Zones (Assumed and had a bit less time so I kept zones very simple)
- Downtown: [40.70, -74.00] to [40.75, -73.98]
- Airport: [40.63, -73.78] to [40.65, -73.76]
- Suburbs: [40.80, -73.90] to [40.85, -73.85]

##  Architecture & Design Decisions

### Core Components
- **Flask Web Framework** - Lightweight and efficient for HTTP APIs
- **In-memory Storage** - Simple key-value store for vehicle status
- **Rectangular Geofences** - Simple bounding box detection  
- **Event-driven Logic** - Real-time zone transition detection

### Key Features  
- **Real-time Processing** - Immediate zone detection on location updates
- **Comprehensive Logging** - Structured logging for operational monitoring
- **Error Handling** - Robust validation and meaningful error responses
- **RESTful API** - Standard HTTP interface for easy integration

##  Assumptions
- **Coordinate System** - GPS coordinates in decimal degrees (WGS84)
- **Zone Shapes** - Rectangular bounding boxes (simplified for demo)
- **Vehicle Identification** - Unique string IDs for each vehicle  
- **Time Format** - ISO 8601 timestamps (UTC)
- **Data Persistence** - In-memory storage (suitable for demo scale)

## What I Would Improve With More Time
- Add persistent storage (Redis/PostgreSQL) instead of in-memory dicts.
- Add unit tests for zone transitions and edge cases.
- Expand zone shapes to polygons instead of simple rectangles.
- Add authentication or rate limiting for production use.

  
