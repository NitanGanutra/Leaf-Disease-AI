import os

# Path to your training folders
data_path = './dataset/train'

if os.path.exists(data_path):
    # This is exactly how PyTorch sorts folders
    folders = sorted([d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))])
    
    print("\n--- COPY AND PASTE THIS INTO YOUR JSON ---")
    for i, folder in enumerate(folders):
        print(f'Index {i} is: {folder}')
else:
    print("Dataset folder not found!")