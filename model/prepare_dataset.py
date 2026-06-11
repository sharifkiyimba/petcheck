"""
Prepare Dataset Structure for PetCheck AI Training
Run this to create the folder structure for your dataset
"""

import os
import shutil

# Create directory structure
DATASET_DIR = 'dataset'

CLASSES = [
    "Healthy",
    "Skin Infection",
    "Eye Infection",
    "Ear Infection",
    "Ringworm",
    "Wounds",
    "Obesity",
    "Dental Disease"
]

def create_structure():
    """Create the folder structure for dataset"""
    for split in ['train', 'val']:
        split_path = os.path.join(DATASET_DIR, split)
        os.makedirs(split_path, exist_ok=True)
        
        for class_name in CLASSES:
            class_path = os.path.join(split_path, class_name)
            os.makedirs(class_path, exist_ok=True)
            print(f"Created: {class_path}")
    
    print("\n✅ Folder structure created!")
    print("\n📁 Place your images in the following folders:")
    print("   dataset/train/Healthy/          - Healthy pet images")
    print("   dataset/train/Skin Infection/   - Skin infection images")
    print("   dataset/train/Eye Infection/    - Eye infection images")
    print("   dataset/train/Ear Infection/    - Ear infection images")
    print("   dataset/train/Ringworm/         - Ringworm/fungal images")
    print("   dataset/train/Wounds/           - Wound/injury images")
    print("   dataset/train/Obesity/          - Overweight pet images")
    print("   dataset/train/Dental Disease/   - Dental issue images")
    print("\n   (Same structure for dataset/val/ for validation images)")
    print("\n📌 Minimum recommended: 50-100 images per class for good accuracy")

if __name__ == '__main__':
    create_structure()