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
    "Healthy": "✅ Your pet appears healthy! Keep up regular vet checkups, a balanced diet, and daily exercise.",
    "Skin Infection": "⚠️ Clean the affected area with mild soap. Prevent scratching. Visit a vet for proper medication.",
    "Eye Infection": "⚠️ Gently wipe discharge with a clean, damp cloth. Do NOT use human eye drops. See a vet for antibiotics.",
    "Ear Infection": "⚠️ Do NOT insert anything into the ear. Visit a vet for proper cleaning and medication.",
    "Ringworm": "⚠️ Isolate your pet from other animals. Wash bedding daily. Antifungal treatment from a vet is needed.",
    "Wounds/Injuries": "🚨 Clean with saline solution. Apply gentle pressure if bleeding. See a vet for deep wounds.",
    "Obesity": "⚠️ Reduce food portions. Increase daily exercise. Consult a vet for a proper diet plan.",
    "Dental Disease": "⚠️ Brush your pet's teeth with pet-safe toothpaste. Provide dental chews. Schedule a vet dental checkup."
}

_model = None

def load_model():
    global _model
    if _model is None:
        try:
            if os.path.exists(MODEL_PATH):
                print(f"Loading model from {MODEL_PATH}")
                _model = models.resnet18(weights=None)
                _model.fc = nn.Linear(_model.fc.in_features, len(DISEASE_CLASSES))
                _model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
                _model.eval()
                print("✅ Trained AI model loaded successfully!")
            else:
                print("⚠️ Model file not found.")
                return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return _model

def predict_disease(image_path):
    """Predict disease using your trained model"""
    
    model = load_model()
    
    if model is None:
        return {
            'success': False,
            'error': 'model_not_found',
            'disease': 'Model Not Ready',
            'confidence': 0,
            'advice': 'AI model is not loaded. Please check the server logs.',
            'all_predictions': []
        }
    
    try:
        # Load and prepare image
        image = Image.open(image_path).convert('RGB')
        
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
        return {
            'success': False,
            'error': str(e),
            'disease': 'Error',
            'confidence': 0,
            'advice': f'Error analyzing image: {str(e)}. Please try again.',
            'all_predictions': []
        }