from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import io
from PIL import Image

# Prediction and UAV Simulator modules
from model.inference import predict_image
from drone_simulator import (
    get_mission,
    get_telemetry,
    start_mission,
    reset_mission,
    update_telemetry,
    record_inspection,
    get_inspections,
)

# 1. Initialize FastAPI
app = FastAPI(
    title="AgriVision AI & UAV Crop Monitoring API",
    description="Precision Agriculture Deep Learning Disease Detection and Autonomous UAV Flight Simulation",
    version="2.0.0"
)

# 2. Link static CSS/JS/assets
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

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

# ==========================================
# Frontend Page Routes
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serves the standard AgriVision leaf diagnosis website."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/drone", response_class=HTMLResponse)
async def read_drone():
    """Serves the simulated UAV mission & precision crop mapping dashboard."""
    with open("static/drone.html", "r", encoding="utf-8") as f:
        return f.read()

# ==========================================
# Original Disease Prediction Endpoint
# ==========================================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Receives an image and returns the 99.3% accurate diagnosis."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        result = predict_image(image)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# UAV Flight & Telemetry Simulation Routes
# ==========================================
@app.get("/drone/mission")
def drone_mission():
    """Returns UAV mission parameters, waypoints, and survey grid."""
    return get_mission()

@app.get("/drone/telemetry")
def drone_telemetry():
    """Returns real-time simulated flight telemetry (GPS, alt, speed, battery)."""
    return get_telemetry()

@app.post("/drone/mission/start")
def drone_mission_start(req: MissionStartRequest = MissionStartRequest()):
    """Starts autonomous waypoint mission."""
    return start_mission(altitude=req.altitude, speed=req.speed)

@app.post("/drone/mission/reset")
def drone_mission_reset():
    """Resets UAV to Home Base in standby mode."""
    return reset_mission()

@app.post("/drone/telemetry")
def drone_update_telemetry(req: TelemetryUpdateRequest):
    """Updates simulated UAV coordinates and flight status."""
    return update_telemetry(
        lat=req.latitude,
        lng=req.longitude,
        altitude=req.altitude,
        speed=req.speed,
        waypoint_index=req.waypoint_index,
        status=req.status,
    )

@app.post("/drone/analyze")
async def drone_analyze_crop(
    file: UploadFile = File(...),
    waypoint_id: Optional[int] = Form(1)
):
    """
    Connects Aerial Crop Capture to Deep Learning AI Model:
    1. Preprocesses leaf specimen image
    2. Runs MobileNetV2 classification
    3. Couples diagnosis & confidence with GPS waypoint coordinates
    4. Records entry in mission hotspot ledger
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        result = predict_image(image)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Prediction failed"))

        # Link diagnosis with physical field coordinates
        filename = file.filename or "aerial_scan.jpg"
        inspection = record_inspection(
            waypoint_id=waypoint_id,
            prediction_data=result,
            image_name=filename
        )

        return {
            "success": True,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "inspection": inspection
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/drone/inspections")
def drone_inspections():
    """Returns all recorded crop disease inspection records."""
    return {"success": True, "inspections": get_inspections()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)