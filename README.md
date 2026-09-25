# 🌱 Agri-AI: UAV-Assisted Precision Crop Health Monitoring System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)](https://fastapi.tiangolo.com/)
[![Leaflet](https://img.shields.io/badge/GIS-Leaflet.js-green)](https://leafletjs.com/)

**Agri-AI** is an end-to-end precision agriculture platform combining **Deep Learning (PyTorch MobileNetV2)** with a **Simulated UAV Mission & GIS Field Mapping System**. 

The system achieves **99.3% validation accuracy** across common Potato and Tomato foliar diseases, and bridges aerial waypoint surveillance with localized agronomic pathogen diagnoses.

---

## 🚁 System Architecture

```text
              🚁 SIMULATED UAV
                    │
                    ▼ (GPS / Waypoint Trajectory)
          Mission / Flight Path
                    │
                    ▼ (Aerial Imagery)
          Crop Specimen Capture
                    │
                    ▼
          FastAPI Backend Server
                    │
                    ▼
        Agri-AI Diagnostic Model
          MobileNetV2 + PyTorch
                    │
                    ▼
          Disease Prediction & Confidence
                    │
                    ▼
       📍 Field Disease Hotspots on Map
```

---

## ✨ Key Capabilities

### 1. 🌿 Deep Learning Crop Doctor (99.3% Precision)
- Fine-tuned **MobileNetV2** CNN with transfer learning.
- Identifies 8 agricultural classes across Potato and Tomato crops (Early Blight, Late Blight, Bacterial Spot, Leaf Mold, Healthy).
- Confidence threshold guard prevents misidentifications of unclassified leaves.
- Delivers actionable agronomic symptoms and immediate chemical/organic treatments.

### 2. 🚁 Simulated UAV Autonomous Mission Module
- **Flight Telemetry HUD:** Real-time simulated GPS coordinates, altitude (AGL), ground speed, battery consumption, heading, and 3D satellite fix.
- **Interactive Field GIS Map:** Built with Leaflet.js, featuring satellite research plot boundaries, waypoint pins, and real-time flight path polylines.
- **Autonomous Survey Mode:** Automatically pilots the UAV through 4 agricultural test sectors, captures crop foliage samples at each waypoint, runs inference, and flags disease clusters.
- **Spatial Pathogen Hotspots:** Dynamically plots color-coded disease markers directly onto the field map (pulsing red pins for blight/bacterial spots, emerald pins for optimal plant vigor).

---

## 🛠️ Tech Stack
- **Deep Learning:** PyTorch, TorchVision, MobileNetV2 (Transfer Learning)
- **Backend API:** FastAPI, Uvicorn, Python-Multipart, Pillow
- **Frontend & GIS:** HTML5, CSS3 Glassmorphism, Vanilla JavaScript, Leaflet.js, Boxicons
- **Dataset:** PlantVillage Dataset (Potato & Tomato classes)

---

## 📂 Project Structure

```text
Leaf-Disease-AI/
│
├── dataset/                  # PlantVillage training/validation sets
├── model/               
│   ├── disease_model.pth     # 99.3% accurate trained weights
│   ├── inference.py          # PyTorch inference pipeline & threshold guard
│   └── disease_info.json     # Botanical disease symptoms & treatments
│
├── static/              
│   ├── index.html            # Standard leaf scanner web UI
│   ├── style.css             # Standard scanner styles
│   ├── app.js                # Standard scanner client logic
│   │
│   ├── drone.html            # 🚁 NEW: UAV mission & field map dashboard
│   ├── drone.css             # 🚁 NEW: Telemetry HUD & radar glassmorphism styling
│   └── drone.js              # 🚁 NEW: Leaflet map, flight loop, and AI hotspot plotting
│
├── drone_simulator.py        # 🚁 NEW: Waypoint mission & telemetry engine
├── main.py                   # FastAPI server with UAV & diagnostic endpoints
├── train.py                  # Model training script
└── requirements.txt          # Python dependencies
```

---

## 🚀 Getting Started

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/NitanGanutra/Leaf-Disease-AI.git
cd Leaf-Disease-AI

# Install required packages
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
- **Standard Leaf Scanner:** [http://localhost:8000/](http://localhost:8000/)
- **Simulated UAV Mission Dashboard:** [http://localhost:8000/drone](http://localhost:8000/drone)

---

## 🎯 Defensible Interview & Resume Points
- *"Engineered an autonomous UAV mission simulation module linking aerial waypoint GPS coordinates with a PyTorch MobileNetV2 crop pathology classifier."*
- *"Implemented real-time telemetry tracking (altitude, velocity, battery, flight paths) and visualized field disease hotspots on an interactive Leaflet GIS map."*
- *"Maintained 99.3% classification accuracy with a confidence threshold guard for out-of-distribution leaves."*