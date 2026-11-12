"""
drone_simulator.py
Integrated UAV Mission and Autonomous Telemetry Module for Agri-AI Smart Farming Platform.

Integrates real-time deep learning leaf disease detections directly into
simulated aerial UAV missions, spatial GPS geo-tagging, flight telemetry,
and precision field hotspot monitoring.
"""

import time
import math
from typing import Dict, List, Any, Optional
from datetime import datetime

# Standard Research Farm Base Station
HOME_BASE = {
    "id": 0,
    "name": "Base Station (Launch & Recovery Pad)",
    "lat": 28.61350,
    "lng": 77.20850,
    "altitude": 0.0,
    "crop_zone": "Base Pad",
    "description": "Autonomous Ground Control Station (GCS) and Recovery Pad"
}

# Pre-mapped Agricultural Research Field Sectors
FIELD_SECTORS = {
    "potato_north": {
        "id": 1,
        "sector_code": "Sector A",
        "name": "Sector A - Potato North Field",
        "crop": "Potato",
        "lat": 28.61420,
        "lng": 77.20890,
        "altitude": 30.0,
        "area_ha": 1.2
    },
    "potato_east": {
        "id": 2,
        "sector_code": "Sector B",
        "name": "Sector B - Potato East Buffer",
        "crop": "Potato",
        "lat": 28.61480,
        "lng": 77.21030,
        "altitude": 30.0,
        "area_ha": 0.9
    },
    "tomato_alpha": {
        "id": 3,
        "sector_code": "Sector C",
        "name": "Sector C - Tomato Test Plot Alpha",
        "crop": "Tomato",
        "lat": 28.61560,
        "lng": 77.20960,
        "altitude": 30.0,
        "area_ha": 1.4
    },
    "tomato_south": {
        "id": 4,
        "sector_code": "Sector D",
        "name": "Sector D - Tomato Southern Row",
        "crop": "Tomato",
        "lat": 28.61510,
        "lng": 77.20810,
        "altitude": 30.0,
        "area_ha": 1.1
    },
    "pepper_central": {
        "id": 5,
        "sector_code": "Sector E",
        "name": "Sector E - Bell Pepper Central Field",
        "crop": "Bell Pepper",
        "lat": 28.61460,
        "lng": 77.20780,
        "altitude": 30.0,
        "area_ha": 0.8
    }
}


class IntegratedDroneSimulator:
    """
    Manages autonomous UAV missions bound dynamically to actual leaf disease detections.
    """

    def __init__(self):
        self.drone_id = "UAV-01"
        self.callsign = "AGRI-SCOUT-ALPHA"
        self.home_base = HOME_BASE.copy()
        
        # Flight telemetry state
        self.status = "STANDBY"  # STANDBY, TAKEOFF, EN_ROUTE, SURVEYING_AFFECTED_AREA, RETURNING, COMPLETED, PAUSED
        self.latitude = self.home_base["lat"]
        self.longitude = self.home_base["lng"]
        self.altitude = 0.0
        self.target_altitude = 30.0
        self.speed = 0.0
        self.cruise_speed = 5.2  # m/s
        self.battery = 98.0
        self.heading = 45.0
        self.gps_fix = "3D-DGPS Fixed (14 Sats)"
        self.signal_strength = "98% (-62 dBm)"
        self.payload = "4K Multispectral Crop Sensor"
        
        # Mission state bound to disease detection
        self.is_mission_active = False
        self.is_paused = False
        self.mission_id = "AGRI-UAV-INIT"
        self.mission_name = "Field Surveillance Standby"
        
        # Currently tracked affected target area
        self.target_sector_code = "Sector C"
        self.target_sector_name = "Sector C - Tomato Test Plot Alpha"
        self.target_crop = "Tomato"
        self.detected_disease = "None"
        self.disease_severity = "Healthy"
        self.detection_confidence = 100.0
        self.target_lat = 28.61560
        self.target_lng = 77.20960
        self.is_simulated_gps = True
        self.image_url = ""
        self.detection_timestamp = ""
        
        # Dynamic waypoints for current mission
        self.waypoints: List[Dict[str, Any]] = []
        self.current_waypoint_index = 0
        self.affected_area_polygon: List[List[float]] = []
        
        # Inspection history
        self.inspections: List[Dict[str, Any]] = []
        self.last_update_time = time.time()

        # Initialize with standard grid
        self._build_waypoints_for_target(self.target_lat, self.target_lng, self.target_sector_name, self.target_crop)

    def _build_waypoints_for_target(self, lat: float, lng: float, sector_name: str, crop: str):
        """
        Dynamically constructs an aerial survey flight trajectory specifically
        centered around the affected crop's GPS location.
        """
        # Approach -> Perimeter scan -> Low-altitude hover inspection -> Return
        delta = 0.00065
        self.waypoints = [
            {
                "id": 1,
                "name": "Waypoint 1 - Approach & Elevation",
                "lat": round(self.home_base["lat"] + (lat - self.home_base["lat"]) * 0.4, 6),
                "lng": round(self.home_base["lng"] + (lng - self.home_base["lng"]) * 0.4, 6),
                "altitude": 30.0,
                "action": "Ascent & Transit"
            },
            {
                "id": 2,
                "name": f"Waypoint 2 - {sector_name} Boundary Entry",
                "lat": round(lat - delta * 0.5, 6),
                "lng": round(lng - delta * 0.6, 6),
                "altitude": 25.0,
                "action": "Perimeter Multispectral Scan"
            },
            {
                "id": 3,
                "name": f"Waypoint 3 - {crop} Hotspot Focus",
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "altitude": 20.0,
                "action": "High-Res Canopy Hover Inspection"
            },
            {
                "id": 4,
                "name": f"Waypoint 4 - {sector_name} Buffer Boundary",
                "lat": round(lat + delta * 0.5, 6),
                "lng": round(lng + delta * 0.6, 6),
                "altitude": 25.0,
                "action": "Spread Risk Containment Scan"
            }
        ]

        # Circular polygon bounding the affected crop zone on Leaflet map
        radius = 0.00045
        points = 12
        poly = []
        for i in range(points):
            angle = (2 * math.pi * i) / points
            p_lat = round(lat + (radius * 0.7) * math.sin(angle), 6)
            p_lng = round(lng + radius * math.cos(angle), 6)
            poly.append([p_lat, p_lng])
        self.affected_area_polygon = poly

    def assign_detection_result(self, detection: Dict[str, Any], custom_lat: Optional[float] = None,
                                custom_lng: Optional[float] = None, custom_sector: Optional[str] = None) -> Dict[str, Any]:
        """
        CRITICAL INTEGRATION HOOK:
        Binds the real deep learning disease detection result to the UAV flight mission.
        """
        crop = detection.get("crop", "Tomato")
        disease = detection.get("disease", "Unknown Condition")
        severity = detection.get("severity", "Moderate")
        confidence = float(detection.get("confidence", 95.0))
        image_url = detection.get("image_url", "")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determine field sector based on crop or farmer customization
        valid_custom = False
        target_lat = self.home_base["lat"]
        target_lng = self.home_base["lng"]
        try:
            if custom_lat is not None and custom_lng is not None and not hasattr(custom_lat, 'default'):
                target_lat = float(custom_lat)
                target_lng = float(custom_lng)
                valid_custom = True
        except (ValueError, TypeError):
            valid_custom = False

        if valid_custom:
            target_name = custom_sector or f"Farmer Custom Field ({crop})"
            target_code = "Custom"
            is_simulated = False
        else:
            is_simulated = True
            # Default to crop-specific agricultural research plot sector
            crop_lower = crop.lower()
            if "potato" in crop_lower:
                sec = FIELD_SECTORS["potato_north"]
            elif "pepper" in crop_lower or "capsicum" in crop_lower:
                sec = FIELD_SECTORS["pepper_central"]
            else:
                sec = FIELD_SECTORS["tomato_alpha"]

            target_lat = sec["lat"]
            target_lng = sec["lng"]
            target_name = sec["name"]
            target_code = sec["sector_code"]

        # Update mission state
        self.mission_id = f"UAV-MISSION-{int(time.time()) % 10000:04d}"
        self.mission_name = f"Precision Survey: {crop} ({disease})"
        self.target_crop = crop
        self.detected_disease = disease
        self.disease_severity = severity
        self.detection_confidence = confidence
        self.target_lat = target_lat
        self.target_lng = target_lng
        self.target_sector_name = target_name
        self.target_sector_code = target_code
        self.is_simulated_gps = is_simulated
        self.image_url = image_url
        self.detection_timestamp = now_str
        self.current_waypoint_index = 0
        self.status = "READY_TO_LAUNCH"

        # Re-build trajectory around the actual detected problem
        self._build_waypoints_for_target(target_lat, target_lng, target_name, crop)

        # Log to inspection history
        record = {
            "inspection_id": f"INSP-{len(self.inspections) + 1:03d}",
            "mission_id": self.mission_id,
            "crop": crop,
            "disease": disease,
            "severity": severity,
            "confidence": confidence,
            "sector": target_name,
            "lat": target_lat,
            "lng": target_lng,
            "is_simulated_gps": is_simulated,
            "image_url": image_url,
            "status": "MONITORING_SCHEDULED",
            "timestamp": now_str
        }
        self.inspections.insert(0, record)

        return self.get_mission_info()

    def get_mission_info(self) -> Dict[str, Any]:
        """Returns the synchronized mission parameters coupled to the AI detection."""
        return {
            "success": True,
            "mission_id": self.mission_id,
            "mission_name": self.mission_name,
            "drone_id": self.drone_id,
            "callsign": self.callsign,
            "status": self.status,
            "is_active": self.is_mission_active,
            "is_paused": self.is_paused,
            "target": {
                "crop": self.target_crop,
                "disease": self.detected_disease,
                "severity": self.disease_severity,
                "confidence": self.detection_confidence,
                "sector_name": self.target_sector_name,
                "sector_code": self.target_sector_code,
                "lat": self.target_lat,
                "lng": self.target_lng,
                "is_simulated_gps": self.is_simulated_gps,
                "image_url": self.image_url,
                "timestamp": self.detection_timestamp
            },
            "home_base": self.home_base,
            "waypoints": self.waypoints,
            "total_waypoints": len(self.waypoints),
            "current_waypoint_index": self.current_waypoint_index,
            "cruise_altitude": self.target_altitude,
            "cruise_speed": self.cruise_speed,
            "affected_area_polygon": self.affected_area_polygon,
            "inspections_count": len(self.inspections),
            "field_sectors": [s for s in FIELD_SECTORS.values()]
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns dynamic real-time UAV flight dynamics."""
        now = time.time()
        dt = max(0.1, min(now - self.last_update_time, 2.0))
        self.last_update_time = now

        if self.is_mission_active and not self.is_paused:
            self.battery = max(18.0, round(self.battery - 0.03 * dt, 1))

        current_wp = None
        if 0 <= self.current_waypoint_index < len(self.waypoints):
            current_wp = self.waypoints[self.current_waypoint_index]

        return {
            "drone_id": self.drone_id,
            "callsign": self.callsign,
            "mission_id": self.mission_id,
            "status": self.status,
            "is_active": self.is_mission_active,
            "is_paused": self.is_paused,
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "altitude": round(self.altitude, 1),
            "speed": round(self.speed, 1),
            "battery": round(self.battery, 1),
            "heading": round(self.heading, 1),
            "gps_fix": self.gps_fix,
            "signal_strength": self.signal_strength,
            "sensor_payload": self.payload,
            "target_crop": self.target_crop,
            "detected_disease": self.detected_disease,
            "severity": self.disease_severity,
            "current_waypoint_index": self.current_waypoint_index,
            "current_waypoint": current_wp,
            "timestamp": datetime.now().isoformat()
        }

    def start_mission(self, altitude: float = 30.0, speed: float = 5.2) -> Dict[str, Any]:
        """Launches the UAV to survey the detected disease location."""
        self.is_mission_active = True
        self.is_paused = False
        self.target_altitude = float(altitude)
        self.cruise_speed = float(speed)
        self.status = "IN_TRANSIT"
        self.current_waypoint_index = 0
        self.speed = self.cruise_speed
        self.altitude = self.target_altitude
        
        # Position at first waypoint
        if self.waypoints:
            self.latitude = self.waypoints[0]["lat"]
            self.longitude = self.waypoints[0]["lng"]

        # Update inspection log
        if self.inspections:
            self.inspections[0]["status"] = "SURVEY_IN_PROGRESS"

        return {
            "success": True,
            "status": self.status,
            "message": f"UAV Mission started for {self.target_crop} - {self.detected_disease}",
            "telemetry": self.get_telemetry()
        }

    def pause_mission(self) -> Dict[str, Any]:
        """Pauses or resumes the active UAV mission."""
        if not self.is_mission_active:
            return {"success": False, "message": "No active mission to pause."}

        self.is_paused = not self.is_paused
        self.status = "PAUSED" if self.is_paused else "SURVEYING_AFFECTED_AREA"
        self.speed = 0.0 if self.is_paused else self.cruise_speed

        return {
            "success": True,
            "is_paused": self.is_paused,
            "status": self.status,
            "telemetry": self.get_telemetry()
        }

    def complete_mission(self) -> Dict[str, Any]:
        """Completes the mission and brings the UAV back to base."""
        self.is_mission_active = False
        self.is_paused = False
        self.status = "COMPLETED"
        self.latitude = self.home_base["lat"]
        self.longitude = self.home_base["lng"]
        self.altitude = 0.0
        self.speed = 0.0
        self.heading = 45.0

        if self.inspections:
            self.inspections[0]["status"] = "SURVEY_COMPLETED"

        return {
            "success": True,
            "status": self.status,
            "message": f"UAV Mission completed. Hotspot data recorded for {self.target_sector_name}.",
            "telemetry": self.get_telemetry()
        }

    def reset_mission(self) -> Dict[str, Any]:
        """Resets the drone back to base pad."""
        self.is_mission_active = False
        self.is_paused = False
        self.status = "STANDBY"
        self.latitude = self.home_base["lat"]
        self.longitude = self.home_base["lng"]
        self.altitude = 0.0
        self.speed = 0.0
        self.battery = 98.0
        self.heading = 45.0
        self.current_waypoint_index = 0

        return {
            "success": True,
            "status": self.status,
            "message": "UAV reset to Base Station",
            "telemetry": self.get_telemetry()
        }

    def update_position(self, lat: float, lng: float, altitude: Optional[float] = None,
                        speed: Optional[float] = None, waypoint_index: Optional[int] = None,
                        status: Optional[str] = None) -> Dict[str, Any]:
        """Updates simulated GPS coordinates and waypoint stepping from frontend."""
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
                if self.inspections:
                    self.inspections[0]["status"] = "SURVEY_COMPLETED"

        return self.get_telemetry()

    def set_custom_target(self, lat: float, lng: float, sector_name: str) -> Dict[str, Any]:
        """Allows farmer to customize target GPS coordinates for their own field."""
        self.target_lat = float(lat)
        self.target_lng = float(lng)
        self.target_sector_name = sector_name
        self.is_simulated_gps = False
        self._build_waypoints_for_target(self.target_lat, self.target_lng, sector_name, self.target_crop)
        return self.get_mission_info()

    def get_inspections(self) -> List[Dict[str, Any]]:
        return self.inspections


# Global simulator instance
simulator = IntegratedDroneSimulator()


def get_mission() -> Dict[str, Any]:
    return simulator.get_mission_info()


def get_telemetry() -> Dict[str, Any]:
    return simulator.get_telemetry()


def start_mission(altitude: float = 30.0, speed: float = 5.2) -> Dict[str, Any]:
    return simulator.start_mission(altitude, speed)


def pause_mission() -> Dict[str, Any]:
    return simulator.pause_mission()


def complete_mission() -> Dict[str, Any]:
    return simulator.complete_mission()


def reset_mission() -> Dict[str, Any]:
    return simulator.reset_mission()


def update_telemetry(lat: float, lng: float, altitude: Optional[float] = None,
                     speed: Optional[float] = None, waypoint_index: Optional[int] = None,
                     status: Optional[str] = None) -> Dict[str, Any]:
    return simulator.update_position(lat, lng, altitude, speed, waypoint_index, status)


def assign_detection_to_drone(detection: Dict[str, Any], custom_lat: Optional[float] = None,
                             custom_lng: Optional[float] = None, custom_sector: Optional[str] = None) -> Dict[str, Any]:
    return simulator.assign_detection_result(detection, custom_lat, custom_lng, custom_sector)


def set_custom_field_location(lat: float, lng: float, sector_name: str) -> Dict[str, Any]:
    return simulator.set_custom_target(lat, lng, sector_name)


def get_inspections() -> List[Dict[str, Any]]:
    return simulator.get_inspections()


# Backwards compatibility helper
def record_inspection(waypoint_id: int, prediction_data: Dict[str, Any], image_name: str = "") -> Dict[str, Any]:
    pred = prediction_data.get("prediction", {})
    return assign_detection_to_drone({
        "crop": prediction_data.get("crop", "Crop"),
        "disease": prediction_data.get("disease", pred.get("common_name", "Condition")),
        "severity": prediction_data.get("severity", "Moderate"),
        "confidence": prediction_data.get("confidence", 95.0),
        "image_url": f"/static/uploads/{image_name}" if image_name else ""
    })
