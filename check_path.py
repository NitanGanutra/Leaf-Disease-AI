import os
from pathlib import Path

# The base path where kagglehub stores things
cache_path = Path(r"C:\Users\rishi\.cache\kagglehub\datasets\emmarex\plantdisease\versions\1")

if cache_path.exists():
    print(f"✅ Found Base Path: {cache_path}")
    subdirs = [d.name for d in cache_path.iterdir() if d.is_dir()]
    print(f"Directories inside: {subdirs}")
    
    # Check deeper if 'PlantVillage' exists
    pv_path = cache_path / "PlantVillage"
    if pv_path.exists():
        print(f"✅ Found PlantVillage Path: {pv_path}")
        classes = [c.name for c in pv_path.iterdir() if c.is_dir()]
        print(f"Total Class Folders found: {len(classes)}")
    else:
        print("❌ 'PlantVillage' folder not found inside version 1.")
else:
    print("❌ Base path does not exist. Did the dataset download finish?")