document.addEventListener('DOMContentLoaded', () => {
    
    // DOM Elements
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const previewArea = document.getElementById('previewArea');
    const imagePreview = document.getElementById('imagePreview');
    const reselectBtn = document.getElementById('reselectBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    const uploadCard = document.getElementById('uploadCard');
    const loader = document.getElementById('loader');
    const resultsCard = document.getElementById('resultsCard');
    
    const confidenceBadge = document.getElementById('confidenceBadge');
    const diseaseName = document.getElementById('diseaseName');
    const scientificName = document.getElementById('scientificName');
    const symptomsText = document.getElementById('symptomsText');
    const treatmentText = document.getElementById('treatmentText');
    const resetBtn = document.getElementById('resetBtn');

    let currentFile = null;

    // --- Drag and Drop Logic ---
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    // File Input Logic (Camera/Gallery)
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // --- Core Functions ---
    function handleFileSelection(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file (JPG, PNG).');
            return;
        }

        currentFile = file;
        const reader = new FileReader();

        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZone.classList.add('hidden');
            previewArea.classList.remove('hidden');
        };

        reader.readAsDataURL(file);
    }

    reselectBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = "";
        previewArea.classList.add('hidden');
        dropZone.classList.remove('hidden');
    });

    // --- API Communication ---
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI State: Loading
        previewArea.classList.add('hidden');
        loader.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            // Give a 1s artificial delay just to show off the cool scanner UI 
            // since localhost deep learning inference might be too fast visually without weights.
            await new Promise(resolve => setTimeout(resolve, 800));

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data);
            } else {
                throw new Error(data.error || "Failed to analyze image");
            }
        } catch (error) {
            console.error("Analysis Error:", error);
            alert("Error analyzing image: " + error.message);
            // Revert state
            loader.classList.add('hidden');
            previewArea.classList.remove('hidden');
        }
    });

    function displayResults(data) {
        loader.classList.add('hidden');
        uploadCard.classList.add('hidden');
        
        // Populate DOM elements
        const pred = data.prediction;
        confidenceBadge.textContent = `${data.confidence.toFixed(1)}% Match`;
        diseaseName.textContent = pred.common_name;
        scientificName.textContent = pred.name;
        symptomsText.textContent = pred.symptoms;
        treatmentText.textContent = pred.treatment;

        // Adjust badge color based on health status
        if (pred.name.toLowerCase().includes('healthy')) {
            confidenceBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            confidenceBadge.style.color = '#10b981';
            document.querySelector('.disease-info h3').style.color = '#10b981';
        } else {
            confidenceBadge.style.background = 'rgba(239, 68, 68, 0.2)';
            confidenceBadge.style.color = '#ef4444';
            document.querySelector('.disease-info h3').style.color = '#ef4444';
        }

        resultsCard.classList.remove('hidden');
        resultsCard.classList.add('fade-in');
    }

    resetBtn.addEventListener('click', () => {
        // Reset full UI state back to start
        resultsCard.classList.add('hidden');
        resultsCard.classList.remove('fade-in');
        
        currentFile = null;
        fileInput.value = "";
        dropZone.classList.remove('hidden');
        uploadCard.classList.remove('hidden');
    });

});
