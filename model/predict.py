"""
PetCheck AI Prediction - SCREENSHOTS ALLOWED, OTHERS REJECTED
- Accepts: Pets + Screenshots
- Rejects: People, Cars, Landscapes, Solid colors
"""

import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
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
                _model = models.resnet18(weights=None)
                _model.fc = nn.Linear(_model.fc.in_features, len(DISEASE_CLASSES))
                _model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
                _model.eval()
                print("✅ Trained AI model loaded!")
            else:
                print("⚠️ Model not found")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    return _model

def is_valid_pet_image(image_path):
    """
    ACCEPTS: Pets + Screenshots
    REJECTS: People, Cars, Landscapes, Solid colors
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        
        # REJECT 1: Too small
        if height < 30 or width < 30:
            return False, "Image is too small. Please upload a larger photo."
        
        # REJECT 2: Solid color
        if len(img_array.shape) == 3:
            r_std = np.std(img_array[:,:,0])
            g_std = np.std(img_array[:,:,1])
            b_std = np.std(img_array[:,:,2])
            if (r_std + g_std + b_std) / 3 < 5:
                return False, "This appears to be a solid color image. Please upload a photo of your pet."
        
        # REJECT 3: People (high skin percentage)
        skin_pixels = 0
        total_samples = 0
        step = max(1, min(height, width) // 40)
        
        for y in range(0, height, step):
            for x in range(0, width, step):
                r, g, b = img_array[y, x]
                if (r > 100 and r < 230 and 
                    g > 50 and g < 180 and 
                    b > 40 and b < 160 and
                    r > g and r > b):
                    skin_pixels += 1
                total_samples += 1
        
        skin_percent = (skin_pixels / total_samples) * 100 if total_samples > 0 else 0
        
        if skin_percent > 55:
            return False, f"This appears to be a person ({skin_percent:.0f}% skin). Please upload a photo of your pet or a screenshot."
        
        # REJECT 4: Cars/Vehicles (low color variance + strong horizontal lines)
        r_mean = np.mean(img_array[:,:,0])
        g_mean = np.mean(img_array[:,:,1])
        b_mean = np.mean(img_array[:,:,2])
        color_var = abs(r_mean - g_mean) + abs(g_mean - b_mean) + abs(b_mean - r_mean)
        
        if color_var < 45:
            try:
                from scipy import ndimage
                gray = np.mean(img_array, axis=2)
                sobel_x = ndimage.sobel(gray, axis=0)
                h_edges = np.mean(np.abs(sobel_x))
                if h_edges > 28:
                    return False, "This appears to be a vehicle. Please upload a photo of your pet or a screenshot."
            except:
                pass
        
        # REJECT 5: Landscapes (blue sky + green ground)
        if height > 200:
            top_portion = img_array[:height//5, :, :]
            top_blue = np.mean(top_portion[:,:,2])
            bottom_portion = img_array[4*height//5:, :, :]
            bottom_green = np.mean(bottom_portion[:,:,1])
            
            if top_blue > 130 and bottom_green > 90:
                return False, "This appears to be a landscape photo. Please upload a photo of your pet or a screenshot."
        
        # ACCEPT: Everything else (Pets, Screenshots, etc.)
        return True, None
        
    except Exception as e:
        print(f"Detection warning: {e}")
        return True, None

def predict_disease(image_path):
    """Main prediction function"""
    
    try:
        # Check if valid image
        is_valid, reject_reason = is_valid_pet_image(image_path)
        
        if not is_valid:
            return {
                'success': False,
                'error': 'not_a_pet',
                'message': f'❌ {reject_reason}',
                'disease': 'Not a Pet',
                'confidence': 0,
                'advice': 'Please upload a photo of your dog/cat or a screenshot.',
                'all_predictions': []
            }
        
        # Load trained model
        model = load_model()
        
        if model is None:
            return {
                'success': False,
                'error': 'no_model',
                'message': 'AI model not loaded. Please run training first.',
                'disease': 'Error',
                'confidence': 0,
                'advice': 'Run: python model/train.py',
                'all_predictions': []
            }
        
        # Prepare image
        image = Image.open(image_path).convert('RGB')
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0)
        
        # Predict
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
        
        confidence, idx = torch.max(probabilities, 0)
        disease = DISEASE_CLASSES[idx.item()]
        confidence_pct = round(confidence.item() * 100, 2)
        
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
            'error': 'processing_error',
            'message': str(e),
            'disease': 'Error',
            'confidence': 0,
            'advice': 'Please try again',
            'all_predictions': []
        }