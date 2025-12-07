import os
import shutil
from sklearn.model_selection import train_test_split
from pathlib import Path

# Path to your dataset
DATASET_DIR = Path("data/MangoLeafBD Dataset")

# Output folders
OUTPUT_DIR = Path("data/mango_split")
TRAIN_DIR = OUTPUT_DIR / "train"
VAL_DIR = OUTPUT_DIR / "val"

def make_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def split_class(class_folder):
    class_name = class_folder.name
    print(f"Processing: {class_name}")

    images = [f for f in class_folder.glob("*") if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]

    train, val = train_test_split(images, test_size=0.2, random_state=42)

    # make folders
    train_class_dir = TRAIN_DIR / class_name
    val_class_dir = VAL_DIR / class_name
    make_dir(train_class_dir)
    make_dir(val_class_dir)

    for img in train:
        shutil.copy(img, train_class_dir / img.name)

    for img in val:
        shutil.copy(img, val_class_dir / img.name)

    print(f"✔ {class_name}: {len(train)} train, {len(val)} val")

def main():
    print("Scanning dataset...")
    class_folders = [f for f in DATASET_DIR.iterdir() if f.is_dir()]

    make_dir(TRAIN_DIR)
    make_dir(VAL_DIR)

    for class_folder in class_folders:
        split_class(class_folder)

    print("\n🎉 DONE! Dataset split created at:", OUTPUT_DIR)

if __name__ == "__main__":
    print("\nStarting split...")

    # Create output folders
    make_dir(TRAIN_DIR)
    make_dir(VAL_DIR)

    # Loop through each class folder
    for class_folder in DATASET_DIR.iterdir():
        if class_folder.is_dir():
            split_class(class_folder)

    print("\n=== DONE SPLITTING! ===")
    print(f"Train folder: {TRAIN_DIR}")
    print(f"Val folder:   {VAL_DIR}")