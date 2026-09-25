"""
drone_simulator.py
Simulated UAV Mission and Autonomous Telemetry Module for Agri-AI Leaf Disease Detection.

This module provides simulated waypoint navigation, UAV telemetry (GPS, altitude,
speed, battery, flight status), and integration hooks between aerial survey coordinates
and PyTorch leaf disease diagnostic inference.
"""

import time
import math
from typing import Dict, List, Any, Optional
from datetime import datetime

# Agricultural Field Waypoints (Simulated Farm Survey Grid)
HOME_BASE = {
    "id": 0,
    "name": "Home Base (Launch Pad)",
    "lat": 28.61350,
    "lng": 77.20850,
    "altitude": 0.0,
    "crop_zone": "Base Station",
    "expected_crop": "None",
    "description": "Autonomous Launch & Recovery Station"
}

DEFAULT_WAYPOINTS = [
    {
        "id": 1,
        "name": "Waypoint 1 - North Potato Zone",
        "lat": 28.61420,
        "lng": 77.20890,
        "altitude": 30.0,
        "crop_zone": "Sector A (Potato)",
        "expected_crop": "Potato (Solanum tuberosum)",
        "description": "Vegetative canopy scan - target early blight detection"
    },
    {
        "id": 2,
        "name": "Waypoint 2 - East Field Buffer",
        "lat": 28.61480,
        "lng": 77.21030,
        "altitude": 30.0,
        "crop_zone": "Sector B (Potato)",
        "expected_crop": "Potato (Solanum tuberosum)",
        "description": "Border row surveillance - humidity vulnerability zone"
    },
    {
        "id": 3,
        "name": "Waypoint 3 - Tomato Test Plot Alpha",
        "lat": 28.61560,
        "lng": 77.20960,
        "altitude": 30.0,
        "crop_zone": "Sector C (Tomato)",
        "expected_crop": "Tomato (Solanum lycopersicum)",
        "description": "Fruiting row inspection - bacterial and fungal check"
    },
    {
        "id": 4,
        "name": "Waypoint 4 - Tomato Southern Row",
        "lat": 28.61510,
        "lng": 77.20810,
        "altitude": 30.0,
        "crop_zone": "Sector D (Tomato)",
        "expected_crop": "Tomato (Solanum lycopersicum)",
        "description": "Dense foliage scan - lower leaf inspection"
    }
]


class DroneSimulator:
    """Manages stateful UAV mission simulation and inspection telemetry."""

    def __init__(self):
        self.drone_id = "UAV-01"
        self.callsign = "AGRI-SCOUT-1"
        self.mission_id = "AGRI-UAV-001"
        self.mission_name = "Autonomous Precision Crop Health Survey"
        self.field_name = "GreenValley Research Farm - Plot 4"
        self.home_base = HOME_BASE.copy()
        self.waypoints = [w.copy() for w in DEFAULT_WAYPOINTS]
        
        # Flight telemetry state
        self.status = "STANDBY"  # STANDBY, TAKING_OFF, IN_TRANSIT, SURVEYING, RETURNING, COMPLETED
        self.latitude = self.home_base["lat"]
        self.longitude = self.home_base["lng"]
        self.altitude = 0.0
        self.target_altitude = 30.0
        self.speed = 0.0
        self.cruise_speed = 5.2  # m/s
        self.battery = 98.0
        self.heading = 45.0
        self.gps_fix = "3D-DGPS (14 Sats)"
        self.signal_strength = "98% (Signal: -62 dBm)"
        self.sensor_payload = "4K Multispectral Crop Sensor"
        
        # Mission progress
        self.current_waypoint_index = 0
        self.is_mission_active = False
        self.mission_start_time = None
        self.last_update_time = time.time()
        
        # Inspection log: stores disease predictions tied to GPS waypoints
        self.inspections: List[Dict[str, Any]] = []

    def get_mission_info(self) -> Dict[str, Any]:
        """Returns mission metadata, waypoint coordinates, and field parameters."""
        return {
            "mission_id": self.mission_id,
            "mission_name": self.mission_name,
            "drone_id": self.drone_id,
            "callsign": self.callsign,
            "field_name": self.field_name,
            "status": self.status,
            "is_active": self.is_mission_active,
            "home_base": self.home_base,
            "waypoints": self.waypoints,
            "total_waypoints": len(self.waypoints),
            "current_waypoint_index": self.current_waypoint_index,
            "cruise_altitude": self.target_altitude,
            "cruise_speed": self.cruise_speed,
            "field_coverage_ha": 3.8,
            "ground_sampling_distance": "1.2 cm/px"
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns real-time UAV flight telemetry."""
        now = time.time()
        dt = max(0.1, min(now - self.last_update_time, 2.0))
        self.last_update_time = now

        # Dynamic simulation adjustments when active
        if self.is_mission_active and self.status in ["IN_TRANSIT", "SURVEYING"]:
            self.battery = max(15.0, round(self.battery - 0.04 * dt, 1))

        current_wp = None
        if 0 <= self.current_waypoint_index < len(self.waypoints):
            current_wp = self.waypoints[self.current_waypoint_index]

        return {
            "drone_id": self.drone_id,
            "callsign": self.callsign,
            "mission_id": self.mission_id,
            "status": self.status,
            "is_active": self.is_mission_active,
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "altitude": round(self.altitude, 1),
            "speed": round(self.speed, 1),
            "battery": round(self.battery, 1),
            "heading": round(self.heading, 1),
            "gps_fix": self.gps_fix,
            "signal_strength": self.signal_strength,
            "sensor_payload": self.sensor_payload,
            "current_waypoint_index": self.current_waypoint_index,
            "current_waypoint": current_wp,
            "inspections_count": len(self.inspections),
            "timestamp": datetime.now().isoformat()
        }

    def start_mission(self, cruise_altitude: float = 30.0, speed: float = 5.2) -> Dict[str, Any]:
        """Initializes and begins a simulated UAV survey mission."""
        self.is_mission_active = True
        self.target_altitude = float(cruise_altitude)
        self.cruise_speed = float(speed)
        self.status = "IN_TRANSIT"
        self.current_waypoint_index = 0
        self.mission_start_time = datetime.now()
        
        # Position at first waypoint
        if self.waypoints:
            first_wp = self.waypoints[0]
            self.latitude = first_wp["lat"]
            self.longitude = first_wp["lng"]
            self.altitude = self.target_altitude
            self.speed = self.cruise_speed

        return {
            "success": True,
            "message": "UAV Mission started successfully",
            "telemetry": self.get_telemetry()
        }

    def reset_mission(self) -> Dict[str, Any]:
        """Resets the UAV back to home base in standby mode."""
        self.is_mission_active = False
        self.status = "STANDBY"
        self.current_waypoint_index = 0
        self.latitude = self.home_base["lat"]
        self.longitude = self.home_base["lng"]
        self.altitude = 0.0
        self.speed = 0.0
        self.battery = 98.0
        self.heading = 45.0
        self.inspections = []
        return {
            "success": True,
            "message": "UAV Mission reset to Home Base",
            "telemetry": self.get_telemetry()
        }

    def update_position(self, lat: float, lng: float, altitude: Optional[float] = None,
                        speed: Optional[float] = None, waypoint_index: Optional[int] = None,
                        status: Optional[str] = None) -> Dict[str, Any]:
        """Updates simulated coordinates and status."""
        self.latitude = lat
        self.longitude = lng
        if altitude is not None:
            self.altitude = altitude
        if speed is not None:
            self.speed = speed
        if waypoint_index is not None:
            self.current_waypoint_index = waypoint_index
        if status is not None:
            self.status = status
            if status == "COMPLETED":
                self.is_mission_active = False

        return self.get_telemetry()

    def record_inspection(self, waypoint_id: int, prediction_data: Dict[str, Any],
                          image_name: str = "") -> Dict[str, Any]:
        """
        Associates a deep learning crop disease diagnosis with a physical GPS waypoint.
        """
        target_wp = None
        for wp in self.waypoints:
            if wp["id"] == waypoint_id:
                target_wp = wp
                break
        
        if not target_wp:
            target_wp = {
                "id": waypoint_id,
                "name": f"Survey Point {waypoint_id}",
                "lat": self.latitude,
                "lng": self.longitude,
                "crop_zone": "Custom Sector",
                "expected_crop": "Unknown"
            }

        pred = prediction_data.get("prediction", {})
        raw_name = pred.get("name", "Unknown")
        common_name = pred.get("common_name", "Unknown Disease")
        confidence = prediction_data.get("confidence", 0.0)

        # Classify health status for field mapping
        if "healthy" in raw_name.lower():
            health_status = "HEALTHY"
            severity_color = "#10b981"  # Emerald Green
            risk_label = "Optimal Plant Vigor"
        elif "not recognized" in raw_name.lower() or "missing" in raw_name.lower():
            health_status = "UNKNOWN"
            severity_color = "#f59e0b"  # Amber
            risk_label = "Unclassified Foliage"
        else:
            health_status = "DISEASE_DETECTED"
            severity_color = "#ef4444"  # Red Alert
            risk_label = "Pathogen Detected - Action Recommended"

        inspection_record = {
            "inspection_id": f"INSP-{len(self.inspections) + 1:03d}",
            "waypoint_id": target_wp["id"],
            "waypoint_name": target_wp["name"],
            "crop_zone": target_wp.get("crop_zone", "General Field"),
            "lat": target_wp["lat"],
            "lng": target_wp["lng"],
            "altitude": self.altitude if self.altitude > 0 else 30.0,
            "crop_scanned": target_wp.get("expected_crop", "Field Crop"),
            "disease_name": raw_name,
            "common_name": common_name,
            "confidence": confidence,
            "health_status": health_status,
            "severity_color": severity_color,
            "risk_label": risk_label,
            "symptoms": pred.get("symptoms", "No symptoms reported."),
            "treatment": pred.get("treatment", "Standard agronomic monitoring."),
            "image_name": image_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Check if an inspection already exists for this waypoint; update if so, else append
        existing_idx = None
        for i, item in enumerate(self.inspections):
            if item["waypoint_id"] == waypoint_id:
                existing_idx = i
                break
        
        if existing_idx is not None:
            self.inspections[existing_idx] = inspection_record
        else:
            self.inspections.append(inspection_record)

        return inspection_record

    def get_inspections(self) -> List[Dict[str, Any]]:
        """Returns all completed waypoint inspections."""
        return self.inspections


# Global simulator instance
simulator = DroneSimulator()


def get_mission() -> Dict[str, Any]:
    return simulator.get_mission_info()


def get_telemetry() -> Dict[str, Any]:
    return simulator.get_telemetry()


def start_mission(altitude: float = 30.0, speed: float = 5.2) -> Dict[str, Any]:
    return simulator.start_mission(altitude, speed)


def reset_mission() -> Dict[str, Any]:
    return simulator.reset_mission()


def update_telemetry(lat: float, lng: float, altitude: Optional[float] = None,
                     speed: Optional[float] = None, waypoint_index: Optional[int] = None,
                     status: Optional[str] = None) -> Dict[str, Any]:
    return simulator.update_position(lat, lng, altitude, speed, waypoint_index, status)


def record_inspection(waypoint_id: int, prediction_data: Dict[str, Any], image_name: str = "") -> Dict[str, Any]:
    return simulator.record_inspection(waypoint_id, prediction_data, image_name)


def get_inspections() -> List[Dict[str, Any]]:
    return simulator.get_inspections()
