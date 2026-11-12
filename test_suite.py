import io
import sys
from PIL import Image, ImageDraw

from main import (
    read_index,
    read_drone,
    drone_mission,
    drone_telemetry,
    drone_mission_start,
    drone_mission_pause,
    drone_mission_complete,
    drone_mission_reset,
    drone_set_target,
    predict_crop_disease,
    get_detection_history,
    MissionStartRequest,
    TargetLocationRequest,
)

class MockFile:
    def __init__(self, data, filename="leaf.jpg", content_type="image/jpeg"):
        self.data = data
        self.filename = filename
        self.content_type = content_type
    def read(self):
        return self.data

def create_synthetic_leaf(crop="tomato", diseased=True):
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)
    draw.line([(112, 20), (112, 200)], fill=(20, 100, 20), width=3)
    draw.line([(112, 60), (60, 100)], fill=(20, 100, 20), width=2)
    draw.line([(112, 60), (164, 100)], fill=(20, 100, 20), width=2)

    if diseased:
        draw.ellipse([(60, 60), (105, 105)], fill=(101, 67, 33), outline=(218, 165, 32), width=3)
        draw.ellipse([(120, 120), (165, 165)], fill=(80, 50, 20), outline=(218, 165, 32), width=2)
        draw.ellipse([(130, 50), (160, 80)], fill=(90, 55, 25), outline=(200, 180, 50), width=2)
    
    b = io.BytesIO()
    img.save(b, "JPEG")
    return b.getvalue()

def run_all_tests():
    print("=" * 60)
    print("AGRI-AI 3.0 COMPLETE PLATFORM TEST SUITE")
    print("=" * 60)

    passed = 0
    total = 0

    def check(cond, name):
        nonlocal passed, total
        total += 1
        if cond:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}")
            raise AssertionError(f"Test failed: {name}")

    # 1. Homepage HTML & Structure Verification
    index_html = read_index()
    check("Agri-AI" in index_html, "Section 1: Overview loaded with Agri-AI branding")
    check("Upload Crop Leaf Specimen" in index_html, "Section 2: Crop Disease Detection upload area present")
    check("Deep Learning Disease Analysis" in index_html, "Section 3: Disease Analysis section present")
    check("Recommended Actions for Farmers" in index_html, "Section 4: Dedicated Farmer Actions section present")
    check("UAV Drone Monitoring Panel" in index_html, "Section 5: UAV Drone Monitoring section present")
    check("Detection & UAV Mission History" in index_html, "Section 6: Detection History section present")
    check("Bell Pepper (Capsicum)" in index_html, "Bell Pepper (Capsicum) crop option available")

    # 2. Dedicated Drone View
    drone_html = read_drone()
    check("UAV" in drone_html or "Drone" in drone_html, "Dedicated /drone view intact")

    # 3. Initial Telemetry & Mission
    m_init = drone_mission()
    check("target" in m_init and "waypoints" in m_init, "Drone mission API returns target and waypoints")
    t_init = drone_telemetry()
    check("latitude" in t_init and "battery" in t_init, "Drone telemetry returns GPS and battery status")

    # 4. Disease Detection - Bell Pepper (Capsicum)
    bp_data = create_synthetic_leaf("bell_pepper", diseased=True)
    bp_file = MockFile(bp_data, filename="capsicum_leaf.jpg")
    res_bp = predict_crop_disease(file=bp_file, crop_hint="bell_pepper")

    check(res_bp["success"] is True, "Bell Pepper disease classification succeeds")
    check(res_bp["crop"] == "Bell Pepper", "Crop identified as Bell Pepper")
    check(res_bp["severity"] in ["Healthy", "Mild", "Moderate", "Severe"], f"Severity evaluated: {res_bp['severity']}")
    check(res_bp["confidence"] > 0, f"Confidence score: {res_bp['confidence']}%")
    check(len(res_bp["causes"]) > 0, "Pathology causes provided")
    check(len(res_bp["symptoms"]) > 0, "Symptoms explained")
    
    # Verify 6 categories of Farmer Recommendations
    recs = res_bp["recommended_actions"]
    check(len(recs.get("immediate_actions", [])) > 0, "Farmer actions: Immediate actions present")
    check(len(recs.get("organic_options", [])) > 0, "Farmer actions: Organic treatment options present")
    check(len(recs.get("treatment_methods", [])) > 0, "Farmer actions: Treatment methods present")
    check(len(recs.get("irrigation_fertilizer", [])) > 0, "Farmer actions: Irrigation & fertilizer advice present")
    check(len(recs.get("prevention", [])) > 0, "Farmer actions: Prevention techniques present")
    check(len(recs.get("when_to_consult_expert", "")) > 0, "Farmer actions: Expert consultation criteria present")

    # Check Drone Linkage for Bell Pepper
    dm_bp = res_bp["drone_mission"]
    check(dm_bp["target"]["crop"] == "Bell Pepper", "Drone mission dynamically bound to Bell Pepper")
    check(dm_bp["target"]["sector_code"] == "Sector E", "Drone mission assigned to Sector E (Bell Pepper field)")

    # 5. Disease Detection - Tomato
    tom_data = create_synthetic_leaf("tomato", diseased=True)
    tom_file = MockFile(tom_data, filename="tomato_leaf.jpg")
    res_tom = predict_crop_disease(file=tom_file, crop_hint="tomato")

    check(res_tom["success"] is True, "Tomato disease classification succeeds")
    check(res_tom["crop"] == "Tomato", "Crop identified as Tomato")
    check(res_tom["drone_mission"]["target"]["crop"] == "Tomato", "Drone mission dynamically bound to Tomato")
    check(res_tom["drone_mission"]["target"]["sector_code"] == "Sector C", "Drone mission assigned to Sector C")

    # 6. Disease Detection - Potato
    pot_data = create_synthetic_leaf("potato", diseased=True)
    pot_file = MockFile(pot_data, filename="potato_leaf.jpg")
    res_pot = predict_crop_disease(file=pot_file, crop_hint="potato")

    check(res_pot["success"] is True, "Potato disease classification succeeds")
    check(res_pot["crop"] == "Potato", "Crop identified as Potato")
    check(res_pot["drone_mission"]["target"]["crop"] == "Potato", "Drone mission dynamically bound to Potato")
    check(res_pot["drone_mission"]["target"]["sector_code"] == "Sector A", "Drone mission assigned to Sector A")

    # 7. UAV Mission Control State Machine
    m_start = drone_mission_start(MissionStartRequest(altitude=30.0, speed=5.5))
    check(m_start["status"] in ["IN_TRANSIT", "EN_ROUTE"], "Mission start triggers active flight status")

    m_pause = drone_mission_pause()
    check(m_pause["status"] == "PAUSED", "Mission pause triggers PAUSED status")

    m_comp = drone_mission_complete()
    check(m_comp["status"] == "COMPLETED", "Mission complete triggers COMPLETED status")

    m_reset = drone_mission_reset()
    check(m_reset["status"] == "STANDBY", "Mission reset triggers STANDBY status")

    # 8. Custom Farmer Field GPS Location
    cust_res = drone_set_target(TargetLocationRequest(
        latitude=28.61850,
        longitude=77.21350,
        sector_name="North Greenhouse Plot 3"
    ))
    check(cust_res["success"] is True, "Custom farmer GPS target coordinates accepted")
    m_cust = drone_mission()
    check(m_cust["target"]["lat"] == 28.61850, "Drone target latitude updated to farmer coordinates")
    check(m_cust["target"]["is_simulated_gps"] is False, "Target marked as custom farmer coordinates")

    # 9. Detection History Audit Ledger
    history = get_detection_history()
    check(history["success"] is True, "History ledger endpoint succeeds")
    check(history["count"] >= 3, f"History recorded {history['count']} scan entries")
    first_hist = history["history"][0]
    check("crop" in first_hist and "disease" in first_hist and "severity" in first_hist and "confidence" in first_hist, "History record contains complete diagnostic metadata")
    check("image_url" in first_hist and "drone_status" in first_hist, "History record tracks image preview and drone status")

    print("\n" + "=" * 60)
    print(f"VERIFICATION SUMMARY: {passed}/{total} TESTS PASSED (100% SUCCESS)")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
