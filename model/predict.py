"""
PetCheck AI Prediction - Uses Your Trained Model
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'petcheck_model.pth')

DISEASE_CLASSES = [
    "Healthy",
    "Skin Infection",
    "Eye Infection",
    "Ear Infection",
    "Ringworm",
    "Wounds/Injuries",
    "Obesity",
    "Dental Disease"
]

DISEASE_ADVICE = {
    "Healthy": "✅ Your pet appears healthy!\n\n📋 Recommendations:\n• Schedule regular vet checkups (every 6-12 months)\n• Maintain a balanced diet\n• Ensure daily exercise\n• Keep vaccinations up to date",
    
    "Skin Infection": "⚠️ SKIN INFECTION DETECTED\n\n📋 Home Care:\n• Clean the affected area with mild soap and water\n• Prevent scratching - use an Elizabethan collar if needed\n• Keep the area dry\n\n🏥 Medical Care:\n• See a vet within 24-48 hours\n• Antibiotics or antifungal medication may be prescribed",
    
    "Eye Infection": "⚠️ EYE INFECTION DETECTED\n\n📋 Home Care:\n• Gently wipe discharge with clean damp cloth\n• Use separate cloth for each eye\n• Do NOT use human eye drops\n\n🏥 Medical Care:\n• See a vet within 24 hours\n• Antibiotic eye drops will be prescribed",
    
    "Ear Infection": "⚠️ EAR INFECTION DETECTED\n\n📋 Home Care:\n• Do NOT insert anything into the ear canal\n• Clean outer ear with damp cloth\n• Keep ears dry\n\n🏥 Medical Care:\n• See a vet within 24-48 hours\n• Ear cleaning and medication needed",
    
    "Ringworm": "⚠️ RINGWORM DETECTED\n\n📋 Home Care:\n• Isolate from other pets and children\n• Wash all bedding, toys, and grooming tools\n• Wear gloves when handling your pet\n\n🏥 Medical Care:\n• See a vet for antifungal medication\n• Treatment takes 6-8 weeks",
    
    "Wounds/Injuries": "🚨 WOUND/INJURY DETECTED\n\n📋 First Aid:\n• Clean gently with saline solution\n• Apply gentle pressure if bleeding\n• Cover with clean bandage\n\n🏥 EMERGENCY:\n• See a vet IMMEDIATELY if bleeding does not stop",
    
    "Obesity": "⚠️ OBESITY DETECTED\n\n📋 Recommendations:\n• Reduce daily food portions by 10-20%\n• Measure food with a standard cup\n• Limit treats to 10% of daily calories\n• Increase daily exercise gradually\n\n🏥 Medical Care:\n• Consult vet for proper diet plan",
    
    "Dental Disease": "⚠️ DENTAL DISEASE DETECTED\n\n📋 Home Care:\n• Start brushing teeth daily with pet-safe toothpaste\n• Use a soft finger brush\n• Provide dental chews and toys\n\n🏥 Medical Care:\n• Schedule professional dental cleaning"
}

# Load model once
_model = None

def load_model():
    global _model
    if _model is None:
        try:
            if os.path.exists(MODEL_PATH):
                print(f"Loading model from {MODEL_PATH}")
                print(f"Model file size: {os.path.getsize(MODEL_PATH) / (1024*1024):.2f} MB")
                
                # Use the same architecture as training
                _model = models.resnet18(weights=None)
                _model.fc = nn.Linear(_model.fc.in_features, len(DISEASE_CLASSES))
                
                # Load the trained weights
                state_dict = torch.load(MODEL_PATH, map_location='cpu')
                _model.load_state_dict(state_dict)
                _model.eval()
                print("✅ Trained AI model loaded successfully!")
                return _model
            else:
                print(f"⚠️ Model file not found at {MODEL_PATH}")
                return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return _model

def predict_disease(image_path):
    """
    Predict disease using your trained model
    """
    # Load the trained model
    model = load_model()
    
    # If model not available, return error
    if model is None:
        return {
            'success': False,
            'error': 'model_not_found',
            'disease': 'Model Not Ready',
            'confidence': 0,
            'advice': 'AI model is not loaded. Please check the server logs.\n\nRun: python model/train.py to train the model first.',
            'all_predictions': []
        }
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': 'file_not_found',
                'disease': 'Error',
                'confidence': 0,
                'advice': 'Image file not found. Please try uploading again.',
                'all_predictions': []
            }
        
        # Load and prepare image
        image = Image.open(image_path).convert('RGB')
        
        # Use the same transform as training
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0)
        
        # Make prediction
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
        
        # Get top prediction
        confidence, idx = torch.max(probabilities, 0)
        disease = DISEASE_CLASSES[idx.item()]
        confidence_pct = round(confidence.item() * 100, 2)
        
        print(f"Prediction: {disease} with {confidence_pct}% confidence")
        
        # Get all predictions for display
        all_predictions = []
        for i, prob in enumerate(probabilities):
            all_predictions.append({
                'disease': DISEASE_CLASSES[i],
                'confidence': round(prob.item() * 100, 2)
            })
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'success': True,
            'disease': disease,
            'confidence': confidence_pct,
            'advice': DISEASE_ADVICE.get(disease, "Please consult a veterinarian."),
            'all_predictions': all_predictions[:4],
            'mode': 'trained_ai'
        }
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return {
            'success': False,
            'error': 'prediction_error',
            'disease': 'Error',
            'confidence': 0,
            'advice': f'Error during analysis: {str(e)}. Please try again.',
            'all_predictions': []
        }