/**
 * static/app.js
 * Unified Smart Agriculture Application Client
 * Integrates:
 * 1. Deep Learning Foliar Diagnosis (Tomato, Potato, Bell Pepper)
 * 2. Farmer-Specific Action Recommendations
 * 3. Autonomous UAV Drone Mission Simulation & Spatial GIS Mapping
 * 4. Detection History Ledger
 */

// Global Application State
let map = null;
let droneMarker = null;
let flightPathPolyline = null;
let hotspotMarker = null;
let affectedAreaLayer = null;

let currentSelectedFile = null;
let currentCropFilter = "auto";
let currentDetectionData = null;

let isFlying = false;
let isPaused = false;
let flightInterval = null;
let missionWaypoints = [];
let currentLegIndex = 0;

// Base Coordinates
const HOME_COORDS = { lat: 28.61350, lng: 77.20850 };

document.addEventListener('DOMContentLoaded', () => {
    initLeafletMap();
    initCropSelectorTabs();
    initUploadAndDragDrop();
    initFlightControls();
    initLocationCustomizer();
    fetchDetectionHistory();
    fetchInitialMission();
});

/**
 * Initializes the integrated Leaflet GIS Map with high-res dark satellite tiles
 */
function initLeafletMap() {
    map = L.map('unifiedFieldMap', {
        center: [28.61480, 77.20900],
        zoom: 16,
        zoomControl: true
    });

    // Dark Matter tile layer for high-contrast agricultural HUD aesthetics
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    // Draw Research Field Boundary Polygon
    const fieldBoundary = [
        [28.61380, 77.20740],
        [28.61630, 77.20750],
        [28.61640, 77.21120],
        [28.61390, 77.21140]
    ];
    L.polygon(fieldBoundary, {
        color: '#15803d',
        weight: 1.5,
        dashArray: '4, 6',
        fillColor: '#22c55e',
        fillOpacity: 0.05
    }).addTo(map).bindTooltip("Research Field Area (3.8 Ha)", { permanent: false, direction: 'center' });

    // Home Base / Ground Control Station Marker
    const homeIcon = L.divIcon({
        className: 'home-base-marker',
        html: `<div style="background:#0284c7; width:18px; height:18px; border-radius:50%; border:3px solid #ffffff; box-shadow:0 0 10px #0284c7;"></div>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
    });

    L.marker([HOME_COORDS.lat, HOME_COORDS.lng], { icon: homeIcon })
        .addTo(map)
        .bindPopup(`<b>Base Station (Launch & Recovery Pad)</b><br>GPS: ${HOME_COORDS.lat}, ${HOME_COORDS.lng}`);

    // Drone Marker
    const droneDivIcon = L.divIcon({
        className: 'uav-drone-leaflet-icon',
        html: `<div id="droneVisualDiv" style="transform: rotate(45deg); display:inline-block;"><i class='bx bxs-navigation' style='font-size:28px; color:#0284c7; filter: drop-shadow(0 0 8px #0284c7);'></i></div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });

    droneMarker = L.marker([HOME_COORDS.lat, HOME_COORDS.lng], {
        icon: droneDivIcon,
        zIndexOffset: 1000
    }).addTo(map);
}

/**
 * Initializes the Crop Filter Tabs (All Crops, Tomato, Potato, Bell Pepper)
 */
function initCropSelectorTabs() {
    const tabs = document.querySelectorAll('.crop-tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentCropFilter = tab.getAttribute('data-crop');
        });
    });
}

/**
 * Drag & Drop, File Upload, and Preview Logic
 */
function initUploadAndDragDrop() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const retakeBtn = document.getElementById('retakeBtn');
    const runDiagnosisBtn = document.getElementById('runDiagnosisBtn');

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    retakeBtn.addEventListener('click', () => {
        currentSelectedFile = null;
        fileInput.value = "";
        document.getElementById('previewContainer').classList.add('hidden');
        document.getElementById('dropZone').classList.remove('hidden');
    });

    runDiagnosisBtn.addEventListener('click', executeDiagnosis);
}

function handleSelectedFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (JPG, PNG).');
        return;
    }
    currentSelectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        const previewImg = document.getElementById('leafPreviewImg');
        previewImg.src = e.target.result;
        document.getElementById('dropZone').classList.add('hidden');
        document.getElementById('previewContainer').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

/**
 * Sends leaf image to backend API for AI diagnosis & automated drone linkage
 */
async function executeDiagnosis() {
    if (!currentSelectedFile) {
        alert('Please select or capture a crop leaf image first.');
        return;
    }

    const loader = document.getElementById('scannerLoader');
    const previewContainer = document.getElementById('previewContainer');
    loader.classList.remove('hidden');
    previewContainer.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', currentSelectedFile);
    formData.append('crop_hint', currentCropFilter);

    // Optional custom sector data from inputs
    const sectorVal = document.getElementById('sectorSelect').value;
    if (sectorVal === 'custom') {
        const cLat = document.getElementById('customLatInput').value;
        const cLng = document.getElementById('customLngInput').value;
        if (cLat && cLng) {
            formData.append('custom_lat', cLat);
            formData.append('custom_lng', cLng);
            formData.append('custom_sector', 'Farmer Custom Field');
        }
    }

    try {
        // Short UX delay for neural network scanner effect
        await new Promise(r => setTimeout(r, 600));

        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Diagnostic evaluation failed.');
        }

        currentDetectionData = data;

        // 1. Render Disease Analysis
        renderDiseaseAnalysis(data);

        // 2. Render Recommended Actions for Farmers
        renderFarmerRecommendations(data);

        // 3. Update Integrated Drone Monitoring Section
        if (data.drone_mission) {
            updateDroneMissionPanel(data.drone_mission);
        }

        // 4. Refresh History
        fetchDetectionHistory();

        // 5. Smooth scroll down to analysis & drone panel
        document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        console.error('Diagnosis Error:', err);
        alert('Error analyzing leaf image: ' + err.message);
    } finally {
        loader.classList.add('hidden');
        previewContainer.classList.remove('hidden');
    }
}

/**
 * Renders Section 3: Disease Analysis
 */
function renderDiseaseAnalysis(data) {
    const analysisSection = document.getElementById('analysis');
    analysisSection.classList.remove('hidden');

    document.getElementById('diagDiseaseName').textContent = data.disease || data.common_name;
    document.getElementById('diagScientificName').textContent = data.scientific_name || data.name;

    // Crop badge
    const cropBadge = document.getElementById('diagCropBadge');
    const crop = data.crop || 'Crop';
    let icon = '🌱';
    if (crop.toLowerCase().includes('tomato')) icon = '🍅';
    else if (crop.toLowerCase().includes('potato')) icon = '🥔';
    else if (crop.toLowerCase().includes('pepper')) icon = '🫑';
    cropBadge.textContent = `${icon} ${crop}`;

    // Severity badge
    const sevBadge = document.getElementById('diagSeverityBadge');
    const severity = data.severity || 'Moderate';
    sevBadge.className = `badge-severity ${severity.toLowerCase()}`;
    sevBadge.innerHTML = `<i class='bx bx-pulse'></i> Severity: ${severity}`;

    // Confidence badge
    document.getElementById('diagConfidenceBadge').textContent = `${data.confidence.toFixed(1)}% Confidence`;

    // Symptoms and Causes
    document.getElementById('diagSymptomsText').textContent = data.symptoms || 'No symptoms reported.';
    document.getElementById('diagCausesText').textContent = data.causes || 'No specific biological cause identified.';
}

/**
 * Renders Section 4: Recommended Actions for Farmers
 */
function renderFarmerRecommendations(data) {
    const recSection = document.getElementById('recommendations');
    recSection.classList.remove('hidden');

    const actions = data.recommended_actions || {};

    renderListItems('actionImmediateList', actions.immediate_actions || ["Prune visibly infected lower leaves immediately.", "Avoid handling plants when wet."]);
    renderListItems('actionOrganicList', actions.organic_options || ["Apply certified organic copper or Bacillus subtilis bio-fungicide.", "Maintain beneficial soil biology."]);
    renderListItems('actionTreatmentList', actions.treatment_methods || ["Apply registered protective sprays following verified label directions.", "Ensure thorough coverage across lower leaf surfaces."]);
    renderListItems('actionIrrigationList', actions.irrigation_fertilizer || ["Deliver water strictly at root level with drip irrigation.", "Avoid excessive nitrogen top-dressing."]);
    renderListItems('actionPreventionList', actions.prevention || ["Implement a 3-year non-solanaceous crop rotation.", "Apply clean organic mulch."]);

    const expertText = actions.when_to_consult_expert || "Consult your local Krishi Vigyan Kendra (KVK) or extension specialist if symptoms expand across more than 15% of the total canopy within 48 hours.";
    document.getElementById('actionExpertText').textContent = expertText;
}

function renderListItems(elementId, items) {
    const ul = document.getElementById(elementId);
    if (!ul) return;
    ul.innerHTML = '';
    (items || []).forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        ul.appendChild(li);
    });
}

/**
 * Renders Section 5: Integrated UAV Drone Monitoring
 */
function updateDroneMissionPanel(mission) {
    const target = mission.target || {};
    document.getElementById('uavTargetHeading').textContent = `Target: ${target.sector_name || 'Agricultural Field'}`;
    document.getElementById('uavTargetDisease').textContent = `${target.crop || ''} (${target.disease || 'General Foliage'})`;
    document.getElementById('uavTargetStatus').textContent = mission.status || 'Ready for Launch';

    // Simulated vs Actual GPS badge
    const gpsBadge = document.getElementById('gpsTypeBadge');
    if (target.is_simulated_gps) {
        gpsBadge.innerHTML = `<i class='bx bx-crosshair'></i> Simulated GPS Coordinates`;
        gpsBadge.className = 'gps-badge-simulated';
    } else {
        gpsBadge.innerHTML = `<i class='bx bx-check-circle'></i> Verified Farmer Field GPS`;
        gpsBadge.className = 'badge-conf';
    }

    // Telemetry HUD updates
    updateTelemetryHUD(mission.status, mission.cruise_altitude || 30.0, 0.0, 98.0, target.lat, target.lng, 45);

    // Update Map
    renderMissionOnMap(mission);
}

/**
 * Updates Leaflet GIS Map with target hotspot, boundary polygon, and flight path
 */
function renderMissionOnMap(mission) {
    const target = mission.target || {};
    const lat = target.lat || HOME_COORDS.lat;
    const lng = target.lng || HOME_COORDS.lng;
    const severity = (target.severity || 'Moderate').toLowerCase();

    // Determine hotspot pin color
    let pinColor = '#f59e0b';
    let pinSymbol = '!';
    if (severity === 'healthy') {
        pinColor = '#10b981';
        pinSymbol = '✓';
    } else if (severity === 'severe') {
        pinColor = '#ef4444';
        pinSymbol = '✕';
    }

    // 1. Remove previous hotspot marker if any
    if (hotspotMarker) {
        map.removeLayer(hotspotMarker);
    }
    if (affectedAreaLayer) {
        map.removeLayer(affectedAreaLayer);
    }

    // 2. Draw Highlighted Affected Zone Polygon
    if (mission.affected_area_polygon && mission.affected_area_polygon.length) {
        affectedAreaLayer = L.polygon(mission.affected_area_polygon, {
            color: pinColor,
            weight: 2,
            dashArray: '3, 6',
            fillColor: pinColor,
            fillOpacity: 0.15
        }).addTo(map);
    }

    // 3. Place Dynamic Hotspot Pin
    const hotspotIcon = L.divIcon({
        className: 'disease-hotspot-pin-live',
        html: `<div style="background:${pinColor}; width:24px; height:24px; border-radius:50%; border:2px solid #fff; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:bold; color:#fff; box-shadow:0 0 10px ${pinColor};">${pinSymbol}</div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    hotspotMarker = L.marker([lat, lng], { icon: hotspotIcon }).addTo(map);
    hotspotMarker.bindPopup(`
        <div style="font-family:'Outfit', sans-serif; min-width:200px;">
            <b style="color:${pinColor}; font-size:13px;">${target.crop}: ${target.disease}</b><br>
            <span style="font-size:11px; color:#64748b;">Sector: ${target.sector_name}</span><br>
            <span style="font-size:11px; color:#64748b;">GPS: ${lat.toFixed(5)}, ${lng.toFixed(5)}</span><br>
            <span style="font-size:11px; font-weight:bold; color:${pinColor};">Severity: ${target.severity} (${(target.confidence || 0).toFixed(1)}%)</span>
        </div>
    `).openPopup();

    // 4. Draw Waypoints Flight Path Polyline
    missionWaypoints = [
        { lat: HOME_COORDS.lat, lng: HOME_COORDS.lng },
        ...(mission.waypoints || []),
        { lat: HOME_COORDS.lat, lng: HOME_COORDS.lng }
    ];

    if (flightPathPolyline) {
        map.removeLayer(flightPathPolyline);
    }

    const polyCoords = missionWaypoints.map(w => [w.lat, w.lng]);
    flightPathPolyline = L.polyline(polyCoords, {
        color: '#0284c7',
        weight: 2.5,
        dashArray: '6, 8',
        opacity: 0.85
    }).addTo(map);

    // Pan map to encompass target and home base
    map.fitBounds(flightPathPolyline.getBounds(), { padding: [40, 40] });
}

/**
 * Telemetry HUD Updater
 */
function updateTelemetryHUD(status, altitude, speed, battery, lat, lng, heading) {
    const badge = document.getElementById('hudStatusBadge');
    badge.textContent = status;
    badge.className = `status-indicator-badge ${status.toLowerCase()}`;

    document.getElementById('hudAltitudeVal').textContent = `${altitude.toFixed(1)} m`;
    document.getElementById('hudSpeedVal').textContent = `${speed.toFixed(1)} m/s`;
    document.getElementById('hudBatteryVal').textContent = `${Math.round(battery)}%`;

    document.getElementById('mapOverlayLat').textContent = lat ? lat.toFixed(6) : HOME_COORDS.lat.toFixed(6);
    document.getElementById('mapOverlayLng').textContent = lng ? lng.toFixed(6) : HOME_COORDS.lng.toFixed(6);
    document.getElementById('mapOverlayHeading').textContent = `${Math.round(heading)}°`;
    document.getElementById('mapOverlayMode').textContent = status;
}

/**
 * Calculates bearing angle between two coordinates
 */
function calculateHeading(startLat, startLng, endLat, endLng) {
    const dLng = (endLng - startLng) * (Math.PI / 180);
    const lat1 = startLat * (Math.PI / 180);
    const lat2 = endLat * (Math.PI / 180);
    const y = Math.sin(dLng) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
    const brng = Math.atan2(y, x) * (180 / Math.PI);
    return (brng + 360) % 360;
}

/**
 * Flight Controls (Start, Pause, Complete, Reset)
 */
function initFlightControls() {
    const btnLaunch = document.getElementById('btnLaunchMission');
    const btnPause = document.getElementById('btnPauseMission');
    const btnComplete = document.getElementById('btnCompleteMission');
    const btnReset = document.getElementById('btnResetMission');

    btnLaunch.addEventListener('click', startUAVFlightLoop);
    btnPause.addEventListener('click', togglePauseUAV);
    btnComplete.addEventListener('click', completeUAVMission);
    btnReset.addEventListener('click', resetUAVToBase);
}

function startUAVFlightLoop() {
    if (isFlying && !isPaused) return;

    if (!missionWaypoints || missionWaypoints.length < 2) {
        alert('Please diagnose a crop or select a sector first to generate a flight trajectory.');
        return;
    }

    isFlying = true;
    isPaused = false;
    document.getElementById('btnLaunchMission').innerHTML = `<i class='bx bx-loader-alt bx-spin'></i> Mission Active`;

    fetch('/drone/mission/start', { method: 'POST' }).catch(() => {});

    flySequentialLegs();
}

function togglePauseUAV() {
    if (!isFlying) return;
    isPaused = !isPaused;
    const pauseBtn = document.getElementById('btnPauseMission');
    if (isPaused) {
        pauseBtn.innerHTML = `<i class='bx bx-play'></i> Resume Mission`;
        fetch('/drone/mission/pause', { method: 'POST' }).catch(() => {});
        updateTelemetryHUD("PAUSED", 30.0, 0.0, 95.0, droneMarker.getLatLng().lat, droneMarker.getLatLng().lng, 0);
    } else {
        pauseBtn.innerHTML = `<i class='bx bx-pause-circle'></i> Pause Mission`;
        fetch('/drone/mission/pause', { method: 'POST' }).catch(() => {});
    }
}

function completeUAVMission() {
    clearInterval(flightInterval);
    isFlying = false;
    isPaused = false;

    fetch('/drone/mission/complete', { method: 'POST' })
        .then(() => fetchDetectionHistory())
        .catch(() => {});

    droneMarker.setLatLng([HOME_COORDS.lat, HOME_COORDS.lng]);
    updateTelemetryHUD("COMPLETED", 0.0, 0.0, 92.0, HOME_COORDS.lat, HOME_COORDS.lng, 45);
    document.getElementById('btnLaunchMission').innerHTML = `<i class='bx bx-play-circle'></i> Start UAV Survey Mission`;
    document.getElementById('btnPauseMission').innerHTML = `<i class='bx bx-pause-circle'></i> Pause Mission`;
}

function resetUAVToBase() {
    clearInterval(flightInterval);
    isFlying = false;
    isPaused = false;
    currentLegIndex = 0;

    fetch('/drone/mission/reset', { method: 'POST' }).catch(() => {});

    droneMarker.setLatLng([HOME_COORDS.lat, HOME_COORDS.lng]);
    const droneIconDiv = document.getElementById('droneVisualDiv');
    if (droneIconDiv) droneIconDiv.style.transform = `rotate(45deg)`;

    updateTelemetryHUD("STANDBY", 0.0, 0.0, 98.0, HOME_COORDS.lat, HOME_COORDS.lng, 45);
    document.getElementById('btnLaunchMission').innerHTML = `<i class='bx bx-play-circle'></i> Start UAV Survey Mission`;
    document.getElementById('btnPauseMission').innerHTML = `<i class='bx bx-pause-circle'></i> Pause Mission`;
}

/**
 * Animated Flight Interpolation
 */
function flySequentialLegs() {
    let batteryLevel = 98.0;

    function moveToNextLeg() {
        if (!isFlying || currentLegIndex >= missionWaypoints.length - 1) {
            completeUAVMission();
            return;
        }

        const startPt = missionWaypoints[currentLegIndex];
        const endPt = missionWaypoints[currentLegIndex + 1];
        const isReturning = (currentLegIndex + 1) === (missionWaypoints.length - 1);

        const heading = calculateHeading(startPt.lat, startPt.lng, endPt.lat, endPt.lng);
        const droneIconDiv = document.getElementById('droneVisualDiv');
        if (droneIconDiv) droneIconDiv.style.transform = `rotate(${heading}deg)`;

        const legStatus = isReturning ? "RETURNING_TO_BASE" : (currentLegIndex === 2 ? "SURVEYING_AFFECTED_AREA" : "EN_ROUTE");
        const steps = 30;
        let stepCount = 0;

        flightInterval = setInterval(() => {
            if (isPaused) return;

            stepCount++;
            const t = stepCount / steps;
            const currentLat = startPt.lat + (endPt.lat - startPt.lat) * t;
            const currentLng = startPt.lng + (endPt.lng - startPt.lng) * t;
            batteryLevel = Math.max(15, batteryLevel - 0.04);

            droneMarker.setLatLng([currentLat, currentLng]);
            updateTelemetryHUD(legStatus, 30.0, 5.2, batteryLevel, currentLat, currentLng, heading);

            if (stepCount >= steps) {
                clearInterval(flightInterval);
                currentLegIndex++;

                // If at the affected target hotspot, hover longer for multispectral scan
                const isTargetHotspot = (currentLegIndex === 3);
                setTimeout(() => {
                    if (isFlying) moveToNextLeg();
                }, isTargetHotspot ? 1800 : 500);
            }
        }, 100);
    }

    moveToNextLeg();
}

/**
 * Field Location Customizer
 */
function initLocationCustomizer() {
    const sectorSelect = document.getElementById('sectorSelect');
    const customLat = document.getElementById('customLatInput');
    const customLng = document.getElementById('customLngInput');
    const btnUpdate = document.getElementById('btnUpdateLocation');

    sectorSelect.addEventListener('change', () => {
        if (sectorSelect.value === 'custom') {
            customLat.classList.remove('hidden');
            customLng.classList.remove('hidden');
        } else {
            customLat.classList.add('hidden');
            customLng.classList.add('hidden');
        }
    });

    btnUpdate.addEventListener('click', async () => {
        const val = sectorSelect.value;
        let lat, lng, sectorName;

        if (val === 'custom') {
            lat = parseFloat(customLat.value);
            lng = parseFloat(customLng.value);
            sectorName = "Farmer Custom Plot";
            if (!lat || !lng) {
                alert('Please enter valid numerical Latitude and Longitude values.');
                return;
            }
        } else {
            const sectors = {
                "potato_north": { lat: 28.61420, lng: 77.20890, name: "Sector A - Potato North Field" },
                "potato_east": { lat: 28.61480, lng: 77.21030, name: "Sector B - Potato East Buffer" },
                "tomato_alpha": { lat: 28.61560, lng: 77.20960, name: "Sector C - Tomato Test Plot Alpha" },
                "tomato_south": { lat: 28.61510, lng: 77.20810, name: "Sector D - Tomato Southern Row" },
                "pepper_central": { lat: 28.61460, lng: 77.20780, name: "Sector E - Bell Pepper Central" }
            };
            const s = sectors[val] || sectors["tomato_alpha"];
            lat = s.lat;
            lng = s.lng;
            sectorName = s.name;
        }

        try {
            const res = await fetch('/drone/mission/target', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude: lat, longitude: lng, sector_name: sectorName })
            });
            const data = await res.json();
            updateDroneMissionPanel(data);
            alert(`Target field location updated to ${sectorName} (${lat}, ${lng})!`);
        } catch (err) {
            console.error('Update Target Error:', err);
        }
    });
}

/**
 * Section 6: Fetch & Render Detection History
 */
async function fetchDetectionHistory() {
    try {
        const res = await fetch('/history');
        if (!res.ok) return;
        const data = await res.json();
        renderHistoryTable(data.history || []);
    } catch (err) {
        console.warn('Could not load history:', err);
    }

    const btnClear = document.getElementById('btnClearHistory');
    btnClear.onclick = async () => {
        if (!confirm('Clear all detection history records?')) return;
        await fetch('/history/clear', { method: 'DELETE' });
        fetchDetectionHistory();
    };
}

function renderHistoryTable(items) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    if (!items.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding:2.5rem; color:var(--text-muted);">
                    <i class='bx bx-folder-open' style="font-size:2rem; display:block; margin-bottom:6px;"></i>
                    No detection records logged yet. Upload a leaf image to generate your first precision diagnosis and UAV mission.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    items.forEach(item => {
        const tr = document.createElement('tr');
        const sevClass = (item.severity || 'Moderate').toLowerCase();

        tr.innerHTML = `
            <td>
                <img src="${item.image_url || '/static/style.css'}" onerror="this.src='https://placehold.co/52x52?text=Leaf'" class="thumb-preview" alt="Leaf">
            </td>
            <td><strong>${item.crop}</strong></td>
            <td>${item.disease}</td>
            <td><span class="badge-severity ${sevClass}">${item.severity}</span></td>
            <td><strong>${(item.confidence || 0).toFixed(1)}%</strong></td>
            <td><small>${item.sector || 'Field'}</small></td>
            <td><small style="color:var(--text-muted);">${item.timestamp}</small></td>
            <td><span class="status-indicator-badge active">${item.drone_status || 'SCHEDULED'}</span></td>
            <td>
                <button class="btn-mini-action" onclick="focusMissionFromHistory('${item.lat}', '${item.lng}', '${item.sector}', '${item.crop}', '${item.disease}')">
                    <i class='bx bx-crosshair'></i> View on Map
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function focusMissionFromHistory(latStr, lngStr, sector, crop, disease) {
    const lat = parseFloat(latStr);
    const lng = parseFloat(lngStr);
    if (!lat || !lng) return;

    document.getElementById('uav-monitoring').scrollIntoView({ behavior: 'smooth' });
    map.setView([lat, lng], 17);
}

/**
 * Loads current mission on initial startup
 */
async function fetchInitialMission() {
    try {
        const res = await fetch('/drone/mission');
        if (res.ok) {
            const data = await res.json();
            updateDroneMissionPanel(data);
        }
    } catch (e) {
        console.warn('Initial mission fetch error:', e);
    }
}

/**
 * Synthetic Canvas Presets for Instant 1-Click Testing of Tomato, Potato, and Bell Pepper
 */
async function loadSamplePreset(presetKey) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');

    // Generate leaf texture based on preset
    const grad = ctx.createLinearGradient(0, 0, 256, 256);

    let cropHint = "auto";

    if (presetKey === 'tomato_early_blight') {
        cropHint = "tomato";
        grad.addColorStop(0, '#15803d');
        grad.addColorStop(0.5, '#166534');
        grad.addColorStop(1, '#451a03');
    } else if (presetKey === 'tomato_healthy') {
        cropHint = "tomato";
        grad.addColorStop(0, '#22c55e');
        grad.addColorStop(0.6, '#16a34a');
        grad.addColorStop(1, '#15803d');
    } else if (presetKey === 'potato_late_blight') {
        cropHint = "potato";
        grad.addColorStop(0, '#166534');
        grad.addColorStop(0.4, '#3f220f');
        grad.addColorStop(1, '#1e1005');
    } else if (presetKey === 'potato_healthy') {
        cropHint = "potato";
        grad.addColorStop(0, '#16a34a');
        grad.addColorStop(0.5, '#22c55e');
        grad.addColorStop(1, '#15803d');
    } else if (presetKey === 'pepper_bacterial_spot') {
        cropHint = "bell_pepper";
        grad.addColorStop(0, '#15803d');
        grad.addColorStop(0.4, '#166534');
        grad.addColorStop(0.8, '#78350f');
        grad.addColorStop(1, '#451a03');
    } else if (presetKey === 'pepper_healthy') {
        cropHint = "bell_pepper";
        grad.addColorStop(0, '#16a34a');
        grad.addColorStop(0.5, '#4ade80');
        grad.addColorStop(1, '#15803d');
    }

    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 256);

    // Draw realistic leaf shape
    ctx.beginPath();
    ctx.moveTo(128, 25);
    ctx.bezierCurveTo(220, 50, 230, 180, 128, 240);
    ctx.bezierCurveTo(25, 180, 35, 50, 128, 25);
    ctx.fillStyle = grad;
    ctx.fill();

    // Central vein
    ctx.beginPath();
    ctx.moveTo(128, 30);
    ctx.lineTo(128, 230);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Add diseased necrotic spots if blight or bacterial spot
    if (presetKey.includes('blight') || presetKey.includes('spot')) {
        for (let i = 0; i < 7; i++) {
            const rx = 80 + Math.random() * 95;
            const ry = 70 + Math.random() * 110;
            ctx.beginPath();
            ctx.arc(rx, ry, 12, 0, 2 * Math.PI);
            ctx.fillStyle = 'rgba(69, 26, 3, 0.9)';
            ctx.fill();

            // Concentric target ring or yellow halo
            ctx.beginPath();
            ctx.arc(rx, ry, 6, 0, 2 * Math.PI);
            ctx.fillStyle = presetKey.includes('spot') ? 'rgba(202, 138, 4, 0.85)' : 'rgba(113, 63, 18, 0.9)';
            ctx.fill();
        }
    }

    // Convert canvas to blob & file
    canvas.toBlob((blob) => {
        const file = new File([blob], `${presetKey}.jpg`, { type: 'image/jpeg' });
        currentSelectedFile = file;

        // Set matching crop tab
        currentCropFilter = cropHint;
        document.querySelectorAll('.crop-tab-btn').forEach(b => {
            if (b.getAttribute('data-crop') === cropHint) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });

        const previewImg = document.getElementById('leafPreviewImg');
        previewImg.src = canvas.toDataURL('image/jpeg');
        document.getElementById('dropZone').classList.add('hidden');
        document.getElementById('previewContainer').classList.remove('hidden');

        // Automatically trigger diagnosis
        executeDiagnosis();
    }, 'image/jpeg', 0.92);
}
