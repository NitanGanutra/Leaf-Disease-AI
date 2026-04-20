import torch
import torch.nn as nn
from torchvision import transforms, models
import json
import io
from PIL import Image
from pathlib import Path

# 1. Setup Directories
BASE_DIR = Path(__file__).resolve().parent

# 2. Load Disease Information
# This must contain the descriptions, symptoms, and treatments for each class
with open(BASE_DIR / 'disease_info.json', 'r') as f:
    DISEASE_INFO = json.load(f)

NUM_CLASSES = len(DISEASE_INFO)

# 3. Model Initialization
def load_model():
    """
    Loads the MobileNetV2 architecture and maps the trained weights.
    """
    # Initialize architecture
    model = models.mobilenet_v2(weights=None) 
    model.classifier[1] = nn.Linear(model.last_channel, NUM_CLASSES)
    
    model_path = BASE_DIR / "disease_model.pth"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if model_path.exists():
        # Load the weights you generated in train.py
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"✅ Model weights loaded successfully on {device}")
    else:
        print(f"⚠️ WARNING: {model_path} not found. Model will use random weights (Inference will be garbage).")
    
    model.to(device)
    model.eval()
    return model, device

# Global instance to avoid reloading the model for every single click
MODEL, DEVICE = load_model()

# 4. Standardized Image Preprocessing
# Note: These values MUST match the 'val' transforms in train.py
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def predict_image(image: Image.Image):
    """
    Runs an image through the CNN and returns verified disease info.
    Includes a threshold guard to prevent misidentification of unknown leaves.
    """
    try:
        # Preprocess and move to same device as model
        input_tensor = preprocess(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = MODEL(input_tensor)
            # Softmax turns raw scores into 0.0 - 1.0 probability percentages
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
        confidence, predicted_idx = torch.max(probabilities, 0)
        
        confidence_score = confidence.item()
        class_idx = str(predicted_idx.item())

        # ==========================================
        # 🛡️ CONFIDENCE THRESHOLD GUARD
        # ==========================================
        # Change the threshold to 0.85 (85%)
        if confidence_score < 0.85:
          return {
             "success": True,
            "prediction": {
              "name": "Species Not Recognized",
              "common_name": "Unknown Plant",
              "symptoms": "The AI is not confident. This leaf might be a species the model hasn't seen (like Apple or Pepper).",
              "treatment": "Please scan a Potato or Tomato leaf for an accurate diagnosis."
        },
        "confidence": round(confidence_score * 100, 2)
    }
        # If confident, fetch the actual data from disease_info.json
        result_info = DISEASE_INFO.get(class_idx, {
            "name": "Class Missing",
            "common_name": "Unknown",
            "symptoms": "No data in disease_info.json for this index.",
            "treatment": "Check your JSON mapping."
        })
        
        return {
            "success": True,
            "prediction": result_info,
            "confidence": round(confidence_score * 100, 2),
            "is_reliable": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Inference Error: {str(e)}"
        }