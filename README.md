# 🐾 PetCheck — AI-Powered Veterinary Web App

**UICT Group 46 | Final Year Project | Diploma in Computer Science**

---

## Project Structure

```
petcheck/
├── app.py                  ← Main Flask application
├── schema.sql              ← MySQL database setup
├── requirements.txt        ← Python dependencies
├── .env                    ← Environment variables (edit this!)
├── model/
│   ├── predict.py          ← AI prediction logic
│   ├── train.py            ← Model training script
│   └── petcheck_model.pth  ← Trained model (generated after training)
├── templates/
│   ├── base.html           ← Base layout
│   ├── index.html          ← Home page
│   ├── upload.html         ← Upload & diagnose page
│   ├── results.html        ← Diagnosis results page
│   └── vets.html           ← Vet finder page
├── static/
│   ├── css/style.css       ← All styles
│   └── js/main.js          ← Frontend JavaScript
└── uploads/                ← Uploaded pet images (auto-created)
```

---

## ⚙️ Setup Instructions

### Step 1 — Create & activate virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# OR
source venv/bin/activate          # Mac/Linux
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set up MySQL database
1. Open MySQL Workbench or phpMyAdmin
2. Run the contents of `schema.sql`
3. Edit `.env` with your MySQL password

### Step 4 — Run the app
```bash
python app.py
```
Open your browser at: **http://127.0.0.1:5000**

---

## 🤖 Training the AI Model

### Step 1 — Collect images
Create this folder structure and add pet images:
```
dataset/
  train/
    Healthy/             ← at least 50 images per class
    Skin Infection/
    Eye Infection/
    Ear Infection/
    Ringworm/
    Wounds/
    Obesity/
    Dental Disease/
  val/
    Healthy/             ← about 20% of your total images
    Skin Infection/
    ...
```

### Step 2 — Train the model
```bash
python model/train.py
```
This will train for 20 epochs and save the best model to `model/petcheck_model.pth`.

### Step 3 — Test it
Restart the Flask app and upload a pet photo to test the diagnosis.

---

## 🗂️ Disease Classes Detected
1. Healthy
2. Skin Infection / Mange
3. Eye Infection / Conjunctivitis
4. Ear Infection / Otitis
5. Ringworm / Fungal Infection
6. Wounds / Injuries
7. Obesity / Malnutrition
8. Dental Disease

---

## 📋 Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Database**: MySQL
- **AI**: PyTorch (ResNet18 CNN)

---

## 👥 Team — Group 46
- Sserwaniko Frank (GL) — 2024/DCS/DAY/0906/G
- Asuza Jedidah Esther — 2024/DCS/DAY/0240
- Kisubi Simon Peter — 2024/DCS/DAY/0994/G
- Ssemwanga Timothy — 2024/DCS/DAY/0911/G
- Mugisha Trevor — 2024/DCS/DAY/0865
- Kiyemba Sharif — 2024/DCS/DAY/0991G

**Supervisor**: Mr. Musinguzi Ivan | UICT
