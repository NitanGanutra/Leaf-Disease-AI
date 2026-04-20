import os
import shutil
import random
from pathlib import Path

SOURCE_PATH = Path(r"C:\Users\rishi\.cache\kagglehub\datasets\emmarex\plantdisease\versions\1\PlantVillage")
DEST_PATH = Path("./dataset")

# We use simple keywords to find the folders regardless of underscores
TARGET_MAP = {
    "Apple___Apple_scab": ["Apple", "scab"],
    "Apple___healthy": ["Apple", "healthy"],
    "Potato___Early_blight": ["Potato", "Early", "blight"],
    "Potato___Late_blight": ["Potato", "Late", "blight"],
    "Potato___healthy": ["Potato", "healthy"],
    "Tomato___Bacterial_spot": ["Tomato", "Bacterial"],
    "Tomato___Early_blight": ["Tomato", "Early", "blight"],
    "Tomato___Late_blight": ["Tomato", "Late", "blight"],
    "Tomato___Leaf_Mold": ["Tomato", "Mold"],
    "Tomato___healthy": ["Tomato", "healthy"]
}

def setup_dataset():
    print("📂 Starting Smarter Dataset Organization...")
    
    # Get all actual folder names in the cache
    available_folders = [d for d in os.listdir(SOURCE_PATH) if os.path.isdir(SOURCE_PATH / d)]

    for target_name, keywords in TARGET_MAP.items():
        # Find the folder that contains all our keywords
        match = None
        for folder in available_folders:
            if all(k.lower() in folder.lower() for k in keywords):
                match = folder
                break
        
        if not match:
            print(f"❌ Could not find a folder for: {target_name}")
            continue

        src_class_dir = SOURCE_PATH / match
        train_dir = DEST_PATH / "train" / target_name
        val_dir = DEST_PATH / "val" / target_name
        
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(val_dir, exist_ok=True)
        
        images = [f for f in os.listdir(src_class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        random.shuffle(images)
        
        split_idx = int(len(images) * 0.8)
        print(f"🚚 Copying {match} -> {target_name} ({len(images)} images)")
        
        for i, img in enumerate(images):
            target_folder = train_dir if i < split_idx else val_dir
            shutil.copy2(src_class_dir / img, target_folder / img)

    print("\n✅ Setup Complete! Check your 'dataset' folder.")

if __name__ == "__main__":
    setup_dataset()