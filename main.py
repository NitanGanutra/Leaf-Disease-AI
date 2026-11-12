from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import io
import time
import shutil
from datetime import datetime
from PIL import Image

# Import core Prediction Engine & Integrated Drone Simulator
from model.inference import predict_image
from drone_simulator import (
    get_mission,
    get_telemetry,
    start_mission,
    pause_mission,
    complete_mission,
    reset_mission,
    update_telemetry,
    assign_detection_to_drone,
    set_custom_field_location,
    get_inspections,
)

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Agri-AI: Smart Crop Disease Detection & UAV Platform",
    description="Unified Precision Agriculture Deep Learning Diagnostic Engine & Autonomous Drone Monitoring System",
    version="3.0.0"
)

# 2. Ensure directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Shared In-Memory Detection & Mission History
DETECTION_HISTORY: List[Dict[str, Any]] = []

# Request Models
class MissionStartRequest(BaseModel):
    altitude: Optional[float] = 30.0
    speed: Optional[float] = 5.2

class TelemetryUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    waypoint_index: Optional[int] = None
    status: Optional[str] = None

class TargetLocationRequest(BaseModel):
    latitude: float
    longitude: float
    sector_name: str

# ==========================================
# Frontend Page Routes
# ==========================================
@app.get("/", response_class=HTMLResponse)
def read_index():
    """Serves the unified Smart Agriculture dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/drone", response_class=HTMLResponse)
def read_drone():
    """Serves the dedicated UAV mission & monitoring view (shared data)."""
    drone_path = os.path.join(STATIC_DIR, "drone.html")
    with open(drone_path, "r", encoding="utf-8") as f:
        return f.read()

# ==========================================
# Integrated Crop Disease Prediction Endpoint
# ==========================================
@app.post("/predict")
def predict_crop_disease(
    file: UploadFile = File(...),
    crop_hint: Optional[str] = Form("auto"),
    custom_lat: Optional[float] = Form(None),
    custom_lng: Optional[float] = Form(None),
    custom_sector: Optional[str] = Form(None)
):
    """
    Unified AI Disease Detection Endpoint:
    1. Validates & saves leaf image
    2. Runs PyTorch MobileNetV2 / Computer Vision analysis (Tomato, Potato, Bell Pepper)
    3. Calculates disease severity (Healthy, Mild, Moderate, Severe)
    4. Provides comprehensive, crop-specific farmer recommendations
    5. AUTOMATICALLY BINDS result to UAV Mission for aerial GPS field surveillance!
    6. Appends to detection history ledger
    """
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not a valid image.")

    try:
        def safe_float(val):
            if val is None or hasattr(val, 'default'):
                return None
            try:
                s = str(val).strip()
                return float(s) if s else None
            except (ValueError, TypeError):
                return None

        clean_lat = safe_float(custom_lat)
        clean_lng = safe_float(custom_lng)
        clean_sector = str(custom_sector).strip() if (custom_sector is not None and not hasattr(custom_sector, 'default') and str(custom_sector).strip()) else None
        clean_hint = str(crop_hint).strip() if (crop_hint is not None and not hasattr(crop_hint, 'default')) else "auto"

        if hasattr(file, 'file') and hasattr(file.file, 'read'):
            contents = file.file.read()
        elif hasattr(file, 'read'):
            contents = file.read()
        else:
            contents = bytes(file)

        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Save uploaded image locally for history and drone visualization
        timestamp_slug = int(time.time() * 1000)
        safe_filename = f"leaf_{timestamp_slug}.jpg"
        save_path = os.path.join(UPLOADS_DIR, safe_filename)
        image.save(save_path, format="JPEG", quality=90)
        image_url = f"/static/uploads/{safe_filename}"

        # Run Deep Learning Crop Diagnostic Engine
        result = predict_image(image, crop_hint=clean_hint)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Inference failed"))

        # Add image preview URL to diagnostic payload
        result["image_url"] = image_url
        result["filename"] = safe_filename
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # CRITICAL INTEGRATION: Automatically pass detection result to drone simulator
        uav_mission = assign_detection_to_drone(
            detection=result,
            custom_lat=clean_lat,
            custom_lng=clean_lng,
            custom_sector=clean_sector
        )

        # Record in persistent detection history
        history_entry = {
            "id": f"SCAN-{len(DETECTION_HISTORY) + 1:04d}",
            "timestamp": result["timestamp"],
            "image_url": image_url,
            "crop": result.get("crop", "Unknown"),
            "disease": result.get("disease", "Unknown"),
            "severity": result.get("severity", "Moderate"),
            "confidence": result.get("confidence", 0.0),
            "sector": uav_mission["target"]["sector_name"],
            "lat": uav_mission["target"]["lat"],
            "lng": uav_mission["target"]["lng"],
            "is_simulated_gps": uav_mission["target"]["is_simulated_gps"],
            "drone_mission_id": uav_mission["mission_id"],
            "drone_status": uav_mission["status"]
        }
        DETECTION_HISTORY.insert(0, history_entry)

        # Return fully enriched, unified response
        return {
            "success": True,
            "crop": result.get("crop"),
            "disease": result.get("disease"),
            "name": result.get("name"),
            "common_name": result.get("common_name"),
            "scientific_name": result.get("scientific_name"),
            "severity": result.get("severity"),
            "confidence": result.get("confidence"),
            "is_reliable": result.get("is_reliable", True),
            "causes": result.get("causes"),
            "symptoms": result.get("symptoms"),
            "treatment": result.get("treatment"),
            "recommended_actions": result.get("recommended_actions", {}),
            "prediction": result.get("prediction", {}),
            "image_url": image_url,
            "drone_mission": uav_mission,
            "history_entry": history_entry
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# UAV Flight & Telemetry Simulation Routes
# ==========================================
@app.get("/drone/mission")
def drone_mission():
    """Returns currently active UAV mission data (dynamically tied to detected disease)."""
    return get_mission()

@app.get("/drone/telemetry")
def drone_telemetry():
    """Returns dynamic real-time simulated flight telemetry."""
    return get_telemetry()

@app.post("/drone/mission/start")
def drone_mission_start(req: MissionStartRequest = MissionStartRequest()):
    """Starts autonomous UAV mission to monitor the affected crop sector."""
    res = start_mission(altitude=req.altitude, speed=req.speed)
    if DETECTION_HISTORY:
        DETECTION_HISTORY[0]["drone_status"] = "SURVEY_IN_PROGRESS"
    return res

@app.post("/drone/mission/pause")
def drone_mission_pause():
    """Pauses or resumes active UAV mission."""
    return pause_mission()

@app.post("/drone/mission/complete")
def drone_mission_complete():
    """Completes the UAV survey and records completion."""
    res = complete_mission()
    if DETECTION_HISTORY:
        DETECTION_HISTORY[0]["drone_status"] = "SURVEY_COMPLETED"
    return res

@app.post("/drone/mission/reset")
def drone_mission_reset():
    """Resets UAV back to base pad."""
    return reset_mission()

@app.post("/drone/mission/target")
def drone_set_target(req: TargetLocationRequest):
    """Allows farmer to customize target GPS coordinates for their own field."""
    return set_custom_field_location(req.latitude, req.longitude, req.sector_name)

@app.post("/drone/telemetry")
def drone_update_telemetry(req: TelemetryUpdateRequest):
    """Updates simulated UAV coordinates and flight status from client loop."""
    return update_telemetry(
        lat=req.latitude,
        lng=req.longitude,
        altitude=req.altitude,
        speed=req.speed,
        waypoint_index=req.waypoint_index,
        status=req.status,
    )

@app.post("/drone/analyze")
def drone_analyze_crop(
    file: UploadFile = File(...),
    crop_hint: Optional[str] = Form("auto"),
    waypoint_id: Optional[int] = Form(1)
):
    """
    UAV In-Flight Analysis Route:
    Receives an aerial crop photo, runs diagnosis, and binds to active mission.
    """
    return predict_crop_disease(file=file, crop_hint=crop_hint)

# ==========================================
# Detection History Routes
# ==========================================
@app.get("/history")
def get_detection_history():
    """Returns list of all historical disease detections and drone missions."""
    return {
        "success": True,
        "count": len(DETECTION_HISTORY),
        "history": DETECTION_HISTORY
    }

@app.delete("/history/clear")
def clear_detection_history():
    """Clears detection history records."""
    global DETECTION_HISTORY
    DETECTION_HISTORY = []
    return {"success": True, "message": "Detection history cleared successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
