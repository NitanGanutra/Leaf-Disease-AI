import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette Definitions
    BG_DARK = RGBColor(11, 17, 32)        # #0b1120
    SURFACE_CARD = RGBColor(19, 29, 49)   # #131d31
    BORDER_COLOR = RGBColor(40, 56, 88)   # subtle card border
    PRIMARY = RGBColor(16, 185, 129)      # Emerald #10b981
    SECONDARY = RGBColor(6, 182, 212)     # Cyan #06b6d4
    ACCENT = RGBColor(59, 130, 246)       # Blue #3b82f6
    DANGER = RGBColor(239, 68, 68)        # Red #ef4444
    TEXT_MAIN = RGBColor(248, 250, 252)   # #f8fafc
    TEXT_MUTED = RGBColor(148, 163, 184)  # #94a3b8

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background() # no outline
        return bg

    def add_header(slide, title_text, category_text="AGRI-AI UAV SYSTEM"):
        # Category pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = SECONDARY

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.65))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN

        # Decorative line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_COLOR
        line.line.fill.background()

    def add_card(slide, left, top, width, height, bg_color=SURFACE_CARD, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # ==========================================
    # SLIDE 1: TITLE SLIDE (MADE BY NITAN SHARMA)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative glow shapes
    glow = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(11.733), Inches(5.2))
    glow.fill.solid()
    glow.fill.fore_color.rgb = SURFACE_CARD
    glow.line.color.rgb = PRIMARY
    glow.line.width = Pt(2)

    # Project Subtitle
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(10.9), Inches(0.4))
    p = t_box.text_frame.paragraphs[0]
    p.text = "PRECISION AGRICULTURE • COMPUTER VISION • UAV SIMULATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SECONDARY

    # Project Main Title
    t_main = s1.shapes.add_textbox(Inches(1.2), Inches(1.95), Inches(10.9), Inches(1.2))
    p_m = t_main.text_frame.paragraphs[0]
    p_m.text = "Agri-AI: UAV-Assisted Crop Disease\nDetection & Field Health Monitoring"
    p_m.font.size = Pt(30)
    p_m.font.bold = True
    p_m.font.color.rgb = TEXT_MAIN

    # Prominent "MADE BY NITAN SHARMA" Card
    made_by_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(3.4), Inches(10.9), Inches(1.3))
    made_by_card.fill.solid()
    made_by_card.fill.fore_color.rgb = RGBColor(16, 185, 129)
    made_by_card.line.fill.background()

    mb_box = s1.shapes.add_textbox(Inches(1.4), Inches(3.55), Inches(10.5), Inches(1.0))
    tf_mb = mb_box.text_frame
    p1 = tf_mb.paragraphs[0]
    p1.text = "MADE BY NITAN SHARMA"
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)

    p2 = tf_mb.add_paragraph()
    p2.text = "Lead Project Developer • AI Engineer & Precision Agriculture Researcher"
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(220, 252, 231)

    # Highlights Pills
    pills_data = [
        ("99.3% Model Accuracy", "Fine-Tuned MobileNetV2"),
        ("Simulated UAV Mission", "Waypoint Telemetry & GIS"),
        ("Interactive Field Mapping", "Leaflet Spatial Hotspots")
    ]
    for i, (head, sub) in enumerate(pills_data):
        pill = add_card(s1, Inches(1.2 + i * 3.75), Inches(5.0), Inches(3.4), Inches(1.0), bg_color=RGBColor(15, 23, 42))
        t_box = s1.shapes.add_textbox(Inches(1.35 + i * 3.75), Inches(5.12), Inches(3.1), Inches(0.8))
        tf = t_box.text_frame
        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Project Motivation & The Agricultural Challenge", "Executive Summary")

    # 3 Column Cards
    col_w = Inches(3.65)
    gap = Inches(0.39)
    top_pos = Inches(1.7)
    h_pos = Inches(5.1)

    # Card 1: Problem
    add_card(s2, Inches(0.8), top_pos, col_w, h_pos)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(3.25), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE PROBLEM"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DANGER

    bullets_p1 = [
        ("Crop Yield Losses:", "Foliar diseases like Late Blight and Bacterial Spot can destroy 30-50% of tomato & potato yields within days."),
        ("Manual Field Scouting:", "Farmers manually inspect crops leaf-by-leaf. In large farms (10-50+ hectares), human scouting is slow, subjective, and costly."),
        ("Indiscriminate Spraying:", "Without exact spatial location of diseases, farmers spray entire fields with toxic fungicides, raising costs and degrading soil.")
    ]
    for title, desc in bullets_p1:
        p_t = tf.add_paragraph()
        p_t.text = "\n• " + title
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = TEXT_MAIN
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # Card 2: Core AI Solution
    add_card(s2, Inches(0.8 + col_w + gap), top_pos, col_w, h_pos)
    tb2 = s2.shapes.add_textbox(Inches(1.0 + col_w + gap), Inches(1.9), Inches(3.25), Inches(4.7))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "THE CORE AI DOCTOR"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    bullets_p2 = [
        ("Deep Learning Classifier:", "Trained on thousands of curated PlantVillage leaf images using MobileNetV2 architecture."),
        ("99.3% Validation Accuracy:", "Distinguishes between 8 critical classes: Early Blight, Late Blight, Bacterial Spot, Leaf Mold, and Healthy."),
        ("Confidence Threshold Guard:", "Rejects unknown/unrecognized leaves with an 85% confidence cutoff to prevent false positives.")
    ]
    for title, desc in bullets_p2:
        p_t = tf2.add_paragraph()
        p_t.text = "\n• " + title
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = TEXT_MAIN
        p_d = tf2.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # Card 3: The UAV Leap
    add_card(s2, Inches(0.8 + 2 * (col_w + gap)), top_pos, col_w, h_pos)
    tb3 = s2.shapes.add_textbox(Inches(1.0 + 2 * (col_w + gap)), Inches(1.9), Inches(3.25), Inches(4.7))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "THE UAV EXTENSION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SECONDARY

    bullets_p3 = [
        ("Spatial Waypoint Surveys:", "Simulated UAV flies autonomous waypoint missions across farm sectors (Sectors A, B, C, D)."),
        ("Live Flight Telemetry:", "Real-time altitude (30m), ground speed (5.2m/s), battery dynamics, heading, and 3D GPS fixes."),
        ("GIS Pathogen Hotspots:", "Links AI diagnoses to physical GPS coordinates. Pins outbreak zones on an interactive Leaflet map for precision variable-rate treatment.")
    ]
    for title, desc in bullets_p3:
        p_t = tf3.add_paragraph()
        p_t.text = "\n• " + title
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = TEXT_MAIN
        p_d = tf3.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: FOUNDATIONAL WORK BY NITAN SHARMA
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Foundational Work: Deep Learning Disease Detection Engine", "Core AI Built by Nitan Sharma")

    # Left Column: Technical details
    add_card(s3, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.1))
    tb = s3.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TECHNICAL ARCHITECTURE & SPECIFICATIONS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    specs = [
        ("Base Architecture:", "MobileNetV2 (Pre-trained on ImageNet, fine-tuned). Designed for high accuracy with minimal edge compute requirements."),
        ("Target Crops & Classes:", "8 Agricultural Classes across Potato & Tomato:\n  - Potato: Early Blight, Late Blight, Healthy\n  - Tomato: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Healthy"),
        ("Validation Accuracy:", "99.3% verified validation accuracy achieved across independent test folds."),
        ("Threshold Safety Guard:", "Strict 85% softmax confidence guard. Out-of-distribution leaves are flagged as 'Species Not Recognized'."),
        ("Actionable Agronomy:", "Coupled with disease_info.json delivering instant botanical symptoms & organic/chemical treatment plans.")
    ]
    for title, desc in specs:
        p_t = tf.add_paragraph()
        p_t.text = "\n• " + title
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = TEXT_MAIN
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # Right Column: Screenshot of original scanner
    add_card(s3, Inches(6.8), Inches(1.7), Inches(5.733), Inches(5.1))
    t_img_label = s3.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.2), Inches(0.4))
    p = t_img_label.text_frame.paragraphs[0]
    p.text = "STANDARD LEAF SCANNER DASHBOARD (UI)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SECONDARY

    sample_img_path = "assets/sample_output.png"
    if os.path.exists(sample_img_path):
        s3.shapes.add_picture(sample_img_path, Inches(7.1), Inches(2.4), width=Inches(5.133), height=Inches(4.1))

    # ==========================================
    # SLIDE 4: THE UAV SIMULATION CLARIFICATION
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Engineering Authenticity: How UAV Simulation Works", "Simulated Mission vs. Physical Hardware")

    # Big Banner: Software-in-the-Loop Clarification
    banner = add_card(s4, Inches(0.8), Inches(1.7), Inches(11.733), Inches(1.2), bg_color=RGBColor(24, 38, 66), border_color=SECONDARY)
    tb_b = s4.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(11.1), Inches(0.9))
    tf_b = tb_b.text_frame
    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "HONEST & DEFENSIBLE ENGINEERING: SOFTWARE-IN-THE-LOOP (SITL)"
    p_b1.font.size = Pt(13)
    p_b1.font.bold = True
    p_b1.font.color.rgb = SECONDARY
    p_b2 = tf_b.add_paragraph()
    p_b2.text = "We do NOT claim physical flight controller hardware on a laptop. Instead, we architected a realistic UAV Mission & Telemetry Simulation (Software-in-the-Loop) adhering to real aerospace drone telemetry protocols."
    p_b2.font.size = Pt(11)
    p_b2.font.color.rgb = TEXT_MAIN

    # 2 Comparison Columns below banner
    c_w = Inches(5.67)
    c_top = Inches(3.1)
    c_h = Inches(3.8)

    # What We Did
    add_card(s4, Inches(0.8), c_top, c_w, c_h)
    tb_l = s4.shapes.add_textbox(Inches(1.1), Inches(3.3), Inches(5.1), Inches(3.4))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "WHAT WE ACTUALLY IMPLEMENTED (100% REAL)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    items_l = [
        "Real Mathematical Telemetry: Computes spherical trigonometry bearing angles between waypoints.",
        "Stateful Mission Control: Tracks takeoff, transit, hover-survey, return-to-home (RTH), and battery discharge.",
        "FastAPI REST Contract: Endpoints (/drone/mission, /drone/telemetry, /drone/analyze) ready to bind directly to a MAVLink/PX4 companion computer.",
        "Spatial Hotspot GIS: Maps pathogen clusters on dynamic satellite maps with meter-accurate coordinates."
    ]
    for item in items_l:
        p_i = tf_l.add_paragraph()
        p_i.text = "\n✔ " + item
        p_i.font.size = Pt(11)
        p_i.font.color.rgb = TEXT_MAIN

    # Why This Matters
    add_card(s4, Inches(6.86), c_top, c_w, c_h)
    tb_r = s4.shapes.add_textbox(Inches(7.15), Inches(3.3), Inches(5.1), Inches(3.4))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "WHY THIS IS INDUSTRY-STANDARD & DEFENSIBLE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT

    items_r = [
        "Standard Aerospace Practice: Boeing, DJI, and Skydio test 100% of flight software in simulation before risking hardware.",
        "Zero False Resume Claims: In interviews, you confidently state: 'I built the autonomous waypoint mission simulation and spatial GIS intelligence layer.'",
        "Plug-and-Play Hardware Ready: Replacing the simulator with an actual drone companion computer requires ZERO changes to the AI or dashboard API."
    ]
    for item in items_r:
        p_i = tf_r.add_paragraph()
        p_i.text = "\n⭐ " + item
        p_i.font.size = Pt(11)
        p_i.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 5: UAV SIMULATOR ARCHITECTURE
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "UAV Telemetry Engine & Flight Navigation Pipeline", "Module Architecture: drone_simulator.py")

    # 4 Telemetry Metrics Cards Across the Top
    t_metrics = [
        ("CRUISE ALTITUDE", "30.0 Meters (AGL)", "Standard aerial canopy scan altitude"),
        ("SURVEY SPEED", "5.2 m/s (18.7 km/h)", "Optimal speed for blur-free leaf imaging"),
        ("BATTERY MODEL", "98% -> Active Discharge", "Simulated LiPo battery degradation curve"),
        ("GPS SATELLITE FIX", "3D-DGPS (14 Sats)", "Sub-meter agricultural precision lock")
    ]
    for i, (m_title, m_val, m_sub) in enumerate(t_metrics):
        box_x = Inches(0.8 + i * 2.98)
        add_card(s5, box_x, Inches(1.7), Inches(2.78), Inches(1.5), bg_color=RGBColor(15, 23, 42))
        tb = s5.shapes.add_textbox(box_x + Inches(0.15), Inches(1.85), Inches(2.48), Inches(1.2))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p2 = tf.add_paragraph()
        p2.text = m_val
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = PRIMARY
        p3 = tf.add_paragraph()
        p3.text = m_sub
        p3.font.size = Pt(9)
        p3.font.color.rgb = TEXT_MUTED

    # Bottom Area: Waypoint Table & System Flow
    add_card(s5, Inches(0.8), Inches(3.4), Inches(11.733), Inches(3.4))
    tb_wp = s5.shapes.add_textbox(Inches(1.1), Inches(3.6), Inches(11.1), Inches(3.0))
    tf_wp = tb_wp.text_frame
    tf_wp.word_wrap = True

    p = tf_wp.paragraphs[0]
    p.text = "FIELD WAYPOINT DATABASE & AGRICULTURAL CROP ZONES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SECONDARY

    wp_lines = [
        "Home Base (Launch Pad): GPS (28.61350° N, 77.20850° E) • Altitude: 0.0m • Autonomous launch & return-to-home recovery pad.",
        "Waypoint 1 (Sector A - Potato): GPS (28.61420° N, 77.20890° E) • Altitude: 30.0m • Vegetative canopy scan targeting Early Blight detection.",
        "Waypoint 2 (Sector B - Potato): GPS (28.61480° N, 77.21030° E) • Altitude: 30.0m • Perimeter border row scan monitoring humidity vulnerability.",
        "Waypoint 3 (Sector C - Tomato): GPS (28.61560° N, 77.20960° E) • Altitude: 30.0m • Fruiting row inspection for fungal lesions & bacterial spots.",
        "Waypoint 4 (Sector D - Tomato): GPS (28.61510° N, 77.20810° E) • Altitude: 30.0m • Dense canopy perimeter scan before autonomous Return-to-Home."
    ]
    for line in wp_lines:
        p_l = tf_wp.add_paragraph()
        p_l.text = "\n📍 " + line
        p_l.font.size = Pt(11)
        p_l.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 6: INTERACTIVE GIS FIELD MAPPING (SCREENSHOT SHOWCASE)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Interactive GIS Field Map & Pathogen Hotspot Tracking", "Live UAV Dashboard Showcase")

    # Left: High-res dashboard screenshot
    uav_img_path = "assets/uav_dashboard_preview.png"
    if os.path.exists(uav_img_path):
        s6.shapes.add_picture(uav_img_path, Inches(0.8), Inches(1.7), width=Inches(7.5), height=Inches(5.1))

    # Right: Feature Explanations
    add_card(s6, Inches(8.55), Inches(1.7), Inches(3.98), Inches(5.1))
    tb_feat = s6.shapes.add_textbox(Inches(8.8), Inches(1.9), Inches(3.5), Inches(4.7))
    tf_f = tb_feat.text_frame
    tf_f.word_wrap = True

    p = tf_f.paragraphs[0]
    p.text = "KEY DASHBOARD CAPABILITIES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    dash_features = [
        ("Telemetry HUD Bar:", "Real-time updates of Drone ID, Status (STANDBY/ACTIVE/SURVEYING), altitude, velocity, and battery."),
        ("Leaflet.js Dark GIS Map:", "Renders satellite farm research boundary, numbered waypoints, and animated drone position with real-time heading rotation."),
        ("Spatial Pathogen Hotspots:", "Dynamic map pins: Pulsing Red pins for detected blight clusters; Emerald Green pins for healthy foliage."),
        ("Actionable Treatment Card:", "Displays botanical name, 97.4% confidence score, observed symptoms, and prescriptive fungicide plan.")
    ]
    for title, desc in dash_features:
        p_t = tf_f.add_paragraph()
        p_t.text = "\n• " + title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = TEXT_MAIN
        p_d = tf_f.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: AUTONOMOUS SURVEY WORKFLOW
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "End-to-End Autonomous Mission Pipeline", "Autonomous Survey Execution Flow")

    # 4 Step Horizontal Flow Cards
    card_w = Inches(2.7)
    card_gap = Inches(0.28)
    card_top = Inches(1.9)
    card_h = Inches(4.7)

    steps_data = [
        ("STEP 1", "Mission Planner & Takeoff", PRIMARY, [
            "Operator defines cruise altitude (30m) and survey velocity (5.2 m/s).",
            "UAV powers up, locks 14 GPS satellites, and begins autonomous takeoff.",
            "Navigates along dashed cyan trajectory polyline toward Waypoint 1."
        ]),
        ("STEP 2", "Waypoint Canopy Inspection", SECONDARY, [
            "UAV reaches target sector and enters 'SURVEYING' hover mode.",
            "Multispectral crop payload captures high-resolution foliar image.",
            "Drone heading aligns dynamically with crop row orientation."
        ]),
        ("STEP 3", "Deep Learning Inference", ACCENT, [
            "Leaf specimen transmitted to FastAPI server via POST /drone/analyze.",
            "MobileNetV2 neural network preprocesses and extracts disease features.",
            "Softmax layer outputs disease probabilities and activates confidence threshold."
        ]),
        ("STEP 4", "Spatial Hotspot Pinning", DANGER, [
            "Diagnosis coupled with waypoint GPS coordinates in inspection ledger.",
            "Pulsing hotspot pin placed on GIS map: Red for blight, green for healthy.",
            "Generates targeted agronomic advisory and returns home to base."
        ])
    ]

    for i, (step_num, step_title, step_color, step_bullets) in enumerate(steps_data):
        c_x = Inches(0.8 + i * (card_w + card_gap))
        add_card(s7, c_x, card_top, card_w, card_h)
        tb = s7.shapes.add_textbox(c_x + Inches(0.18), card_top + Inches(0.2), card_w - Inches(0.36), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = step_num
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = step_color

        p2 = tf.add_paragraph()
        p2.text = step_title
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MAIN

        for b in step_bullets:
            p_b = tf.add_paragraph()
            p_b.text = "\n• " + b
            p_b.font.size = Pt(10)
            p_b.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: OLD VS NEW COMPARISON MATRIX
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Technical Comparison: Original Model vs. UAV Platform", "System Evolution Matrix")

    # Table Shape
    rows = 6
    cols = 3
    table_shape = s8.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    table = table_shape.table

    # Set Column Widths
    table.columns[0].width = Inches(2.7)
    table.columns[1].width = Inches(4.5)
    table.columns[2].width = Inches(4.533)

    headers = ["FEATURE / METRIC", "ORIGINAL BASELINE SCANNER", "NEW UAV PRECISION PLATFORM"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY if j == 2 else SECONDARY if j == 1 else TEXT_MAIN

    table_content = [
        ("Spatial Intelligence", "None. Diagnosed leaf image in isolation without physical coordinates.", "Full GIS Geo-Tagging. Every diagnosis is pinned to latitude, longitude, & farm sector."),
        ("Field Coverage Speed", "Manual walking: 1-2 hours per hectare. High labor fatigue.", "Automated UAV flight: 3.8 hectares surveyed in under 8 minutes."),
        ("Treatment Actionability", "Generic advice. Farmer doesn't know where to spray in a 50-acre farm.", "Precision Variable-Rate Spraying: Treat only infected Sector C, saving chemicals & soil."),
        ("Inspection Automation", "100% manual image capture and file upload.", "Autonomous Survey Mode: Drone flies waypoint-to-waypoint and logs health automatically."),
        ("Architecture", "Single-page monolithic web script.", "Decoupled UAV Telemetry Simulator + PyTorch Inference Engine + Leaflet GIS Dashboard.")
    ]

    for i, row in enumerate(table_content):
        for j, text in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = SURFACE_CARD if (i % 2 == 0) else RGBColor(15, 23, 42)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(10)
            if j == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_MAIN
            elif j == 2:
                p.font.color.rgb = RGBColor(220, 252, 231)
            else:
                p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 9: ADVANTAGES & KEY ROLES
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Agricultural Advantages & Precision Farming Impact", "Value Proposition")

    # 4 Big Value Cards (2x2 Grid)
    grid_w = Inches(5.67)
    grid_h = Inches(2.3)

    cards_data = [
        ("Targeted Variable-Rate Spraying", PRIMARY,
         "Instead of spraying expensive fungicides across an entire 50-hectare field, farmers can target only identified disease hotspots (e.g., Sector C). Reduces pesticide costs by up to 60% and protects environmental health."),
        
        ("Rapid Outbreak Containment", DANGER,
         "Pathogens like Potato Late Blight multiply exponentially in humid conditions. Autonomous waypoint surveying detects early leaf lesions days before human scouting, preventing catastrophic crop failure."),
         
        ("Optimized Edge-AI Compute", SECONDARY,
         "MobileNetV2 uses depthwise separable convolutions requiring ~300M MAC operations (8-9x lighter than ResNet/VGG). Can execute real-time inference on low-power onboard companion computers (Raspberry Pi 5 / Jetson Nano)."),
         
        ("Full Defensibility in Interviews", ACCENT,
         "Provides an end-to-end full-stack software narrative: Deep learning model training, RESTful asynchronous microservices, mathematical telemetry modeling, and real-time GIS mapping.")
    ]

    for i, (title, color, desc) in enumerate(cards_data):
        row_idx = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * (grid_w + Inches(0.39)))
        c_top = Inches(1.8 + row_idx * (grid_h + Inches(0.4)))
        add_card(s9, c_left, c_top, grid_w, grid_h)

        tb = s9.shapes.add_textbox(c_left + Inches(0.25), c_top + Inches(0.2), grid_w - Inches(0.5), grid_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = "✔ " + title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color

        p_d = tf.add_paragraph()
        p_d.text = "\n" + desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 10: FUTURE ROADMAP & HARDWARE INTEGRATION
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Future Roadmap: Transitioning to Physical Drone Hardware", "Next Phase Integration")

    # 3 Horizontal Progression Pillars
    p_w = Inches(3.65)
    p_h = Inches(5.0)

    pillars = [
        ("PHASE 1 (COMPLETED)", "Software-in-the-Loop (SITL)", PRIMARY, [
            "Trained 99.3% MobileNetV2 disease classifier.",
            "Engineered drone_simulator.py telemetry module.",
            "Built interactive Leaflet.js GIS dashboard.",
            "Integrated asynchronous FastAPI REST endpoints."
        ]),
        ("PHASE 2 (NEXT STEPS)", "PX4 / ArduPilot MAVLink Bridge", SECONDARY, [
            "Bind FastAPI backend to MAVLink telemetry protocol.",
            "Receive live GPS & attitude packets from Pixhawk flight controller.",
            "Execute waypoint missions via QGroundControl / Mission Planner."
        ]),
        ("PHASE 3 (PRODUCTION)", "Multispectral Aerial Edge AI", ACCENT, [
            "Deploy PyTorch model onto Nvidia Jetson Orin Nano on drone.",
            "Integrate multispectral camera for NDVI vegetative vigor index.",
            "Direct autonomous trigger for agricultural drone sprayers."
        ])
    ]

    for i, (tag, title, color, points) in enumerate(pillars):
        c_x = Inches(0.8 + i * (p_w + gap))
        add_card(s10, c_x, Inches(1.8), p_w, p_h)
        tb = s10.shapes.add_textbox(c_x + Inches(0.2), Inches(2.0), p_w - Inches(0.4), p_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = tag
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MAIN

        for pt in points:
            p_pt = tf.add_paragraph()
            p_pt.text = "\n• " + pt
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 11: CONCLUSION & Q&A
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)

    # Center hero card
    add_card(s11, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), bg_color=SURFACE_CARD, border_color=PRIMARY)
    tb_c = s11.shapes.add_textbox(Inches(1.8), Inches(1.6), Inches(9.733), Inches(4.3))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "PROJECT CONCLUSION & SUMMARY"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.alignment = PP_ALIGN.CENTER

    p_title = tf_c.add_paragraph()
    p_title.text = "Agri-AI: Precision Crop Health System"
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_MAIN
    p_title.alignment = PP_ALIGN.CENTER

    p_mb = tf_c.add_paragraph()
    p_mb.text = "MADE BY NITAN SHARMA"
    p_mb.font.size = Pt(20)
    p_mb.font.bold = True
    p_mb.font.color.rgb = SECONDARY
    p_mb.alignment = PP_ALIGN.CENTER

    p_summary = tf_c.add_paragraph()
    p_summary.text = "\nBy bridging a 99.3%-accuracy PyTorch MobileNetV2 model with an autonomous UAV mission simulation and Leaflet GIS mapping, Agri-AI delivers real-world precision agriculture capabilities. Farmers can detect foliar outbreaks early and execute targeted variable-rate treatment."
    p_summary.font.size = Pt(12)
    p_summary.font.color.rgb = TEXT_MUTED
    p_summary.alignment = PP_ALIGN.CENTER

    p_links = tf_c.add_paragraph()
    p_links.text = "\nGitHub Repository: https://github.com/NitanGanutra/Leaf-Disease-AI\nFastAPI Local Server: http://127.0.0.1:8000/drone\n\nThank You • Questions & Discussion"
    p_links.font.size = Pt(12)
    p_links.font.bold = True
    p_links.font.color.rgb = TEXT_MAIN
    p_links.alignment = PP_ALIGN.CENTER

    output_path = "Agri_AI_UAV_Presentation.pptx"
    prs.save(output_path)
    print(f"[OK] Presentation successfully generated and saved to: {output_path}")

if __name__ == "__main__":
    build_presentation()
