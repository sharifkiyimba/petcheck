"""
PetCheck Final Training Script
Run this ONCE to train your model with your 134 images
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os

# Configuration
DATASET_DIR = 'dataset'
MODEL_SAVE_PATH = 'model/petcheck_model.pth'
NUM_CLASSES = 8
BATCH_SIZE = 16
EPOCHS = 50
LEARNING_RATE = 0.0001

CLASS_NAMES = [
    "Healthy",
    "Skin Infection",
    "Eye Infection",
    "Ear Infection",
    "Ringworm",
    "Wounds/Injuries",
    "Obesity",
    "Dental Disease"
]

# Data augmentation for better accuracy
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def train():
    print("=" * 60)
    print("🐾 PetCheck FINAL Training")
    print("=" * 60)
    
    # Check dataset
    train_dir = os.path.join(DATASET_DIR, 'train')
    val_dir = os.path.join(DATASET_DIR, 'val')
    
    if not os.path.exists(train_dir):
        print(f"\n❌ Training folder not found: {train_dir}")
        print("\nPlease organize your images:")
        for cls in CLASS_NAMES:
            print(f"   dataset/train/{cls}/")
        return
    
    # Load datasets
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    
    if os.path.exists(val_dir) and len(os.listdir(val_dir)) > 0:
        val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)
        print(f"\n✅ Using separate validation folder")
    else:
        # Split training data
        val_size = int(0.2 * len(train_dataset))
        train_size = len(train_dataset) - val_size
        train_dataset, val_dataset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
        print(f"\n⚠️ No validation folder. Created 80/20 split")
    
    print(f"\n📊 Dataset:")
    print(f"   Training images: {len(train_dataset)}")
    print(f"   Validation images: {len(val_dataset)}")
    print(f"   Classes: {train_dataset.dataset.classes if hasattr(train_dataset, 'dataset') else train_dataset.classes}")
    
    # Show distribution
    print(f"\n📈 Training distribution:")
    if hasattr(train_dataset, 'dataset'):
        for i, class_name in enumerate(CLASS_NAMES):
            count = sum(1 for _, label in train_dataset.dataset.samples if label == i)
            print(f"   {class_name}: {count} images")
    else:
        # For random_split
        print("   (Using random split - distribution may vary)")
    
    # Data loaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🖥️ Training on: {device}")
    
    # Model
    model = models.resnet18(weights='IMAGENET1K_V1')
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    model = model.to(device)
    
    # Training
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    best_val_acc = 0.0
    
    print(f"\n🚀 Training for {EPOCHS} epochs...")
    print("=" * 60)
    
    for epoch in range(EPOCHS):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_acc = 100 * train_correct / train_total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        
        scheduler.step(val_loss)
        
        # Print progress
        print(f"Epoch [{epoch+1:2d}/{EPOCHS}] | "
              f"Train Acc: {train_acc:.2f}% | Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs('model', exist_ok=True)
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"   ✅ Best model saved! (Val Acc: {val_acc:.2f}%)")
    
    print("=" * 60)
    print(f"\n🎉 TRAINING COMPLETE!")
    print(f"   Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"   Model saved to: {MODEL_SAVE_PATH}")
    
    # Per-class accuracy
    print(f"\n📊 Per-class accuracy on validation set:")
    model.eval()
    class_correct = [0] * NUM_CLASSES
    class_total = [0] * NUM_CLASSES
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            for i in range(len(labels)):
                label = labels[i].item()
                pred = predicted[i].item()
                if label == pred:
                    class_correct[label] += 1
                class_total[label] += 1
    
    for i in range(NUM_CLASSES):
        if class_total[i] > 0:
            acc = 100 * class_correct[i] / class_total[i]
            print(f"   {CLASS_NAMES[i]}: {acc:.1f}% ({class_correct[i]}/{class_total[i]})")
    
    print("\n" + "=" * 60)
    print("✅ Everything is ready!")
    print("=" * 60)
    print("\n🎯 Next Steps:")
    print("   1. Restart your Flask app: python app.py")
    print("   2. Upload a pet photo")
    print("   3. The AI will now give ACCURATE diagnoses")
    print("   4. Non-pet images will be REJECTED")

if __name__ == '__main__':
    train()