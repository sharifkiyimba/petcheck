"""
PetCheck Image Fixer
=====================
Renames all images to simple names like 1.jpg, 2.jpg
and removes any corrupted or unreadable image files.

Run: python model/fix_images.py
"""

import os
from PIL import Image

DATASET_DIR = 'dataset'
IMAGE_EXTS  = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

def fix_folder(folder_path, class_name, split_name):
    files = os.listdir(folder_path)
    count = 0
    removed = 0

    for filename in files:
        old_path = os.path.join(folder_path, filename)

        # Skip non-files
        if not os.path.isfile(old_path):
            continue

        # Try to open and verify image is valid
        try:
            img = Image.open(old_path).convert('RGB')
            img.verify()
        except Exception:
            # Corrupted or unreadable — delete it
            try:
                os.remove(old_path)
                removed += 1
            except:
                pass
            continue

        # Rename to simple name
        count += 1
        new_name = f"{count}.jpg"
        new_path = os.path.join(folder_path, new_name)

        if old_path != new_path:
            # Re-save as clean JPEG with simple name
            try:
                img2 = Image.open(old_path).convert('RGB')
                img2.save(new_path, 'JPEG', quality=90)
                if old_path != new_path:
                    os.remove(old_path)
            except Exception as e:
                count -= 1

    return count, removed

def fix_all():
    print("="*55)
    print("  PetCheck Image Fixer")
    print("="*55)
    print(f"{'Split':<8} {'Class':<25} {'OK':>6} {'Removed':>8}")
    print("-"*55)

    total_ok = 0
    total_removed = 0

    for split in ['train', 'val']:
        split_dir = os.path.join(DATASET_DIR, split)
        if not os.path.exists(split_dir):
            continue

        for cls in sorted(os.listdir(split_dir)):
            cls_path = os.path.join(split_dir, cls)
            if not os.path.isdir(cls_path):
                continue

            ok, removed = fix_folder(cls_path, cls, split)
            total_ok      += ok
            total_removed += removed
            print(f"  {split:<8} {cls:<25} {ok:>6} {removed:>8}")

    print("="*55)
    print(f"  Total images fixed: {total_ok}")
    print(f"  Corrupted removed:  {total_removed}")
    print("="*55)
    print("\n  Done! Now run:  python model/train.py")

if __name__ == '__main__':
    fix_all()
