# 🌿 Crop Disease Detection AI
### फसल रोग पहचान प्रणाली

A deep learning powered web application that detects diseases in **Potato** and **Tomato** leaf images using custom CNN models. Built with Flask, TensorFlow/Keras, and SQLite.

---

## 📸 Features

- 📷 **Camera Capture** — take leaf photos directly from your device
- 🤖 **AI Prediction** — custom CNN models with confidence scores
- 📊 **Live Dashboard** — 3 tabs (Overall / Potato / Tomato), auto-refreshed every 4 seconds
- 🕐 **Test History** — searchable and filterable card grid of all predictions
- 📋 **PDF Report** — downloadable diagnosis report per test
- 💊 **Treatment Info** — bilingual (English + Hindi) disease description and treatment
- 🗄️ **SQLite Database** — all tests stored with crop type, confidence, and timestamp

---

## 🧠 AI Models

| Model | Crop | Architecture | Input Size | Classes |
|-------|------|-------------|------------|---------|
| `potato_disease_model.keras` | Potato | Custom CNN | 256×256 | 3 |
| `tomato_disease_model_V2.keras` | Tomato | Custom CNN | 256×256 | 10 |

### ⚠️ Important — Baked Preprocessing
Both models were trained with a baked-in `Rescaling(1/255)` layer:
```python
resize_and_rescale = tf.keras.Sequential([
    layers.Resizing(IMAGE_SIZE, IMAGE_SIZE),
    layers.Rescaling(1.0/255)
])
```
The prediction code passes **raw pixel values (0–255)** — do NOT divide by 255 manually or the model will receive near-zero inputs and always predict the same class.

---

## 🦠 Supported Disease Classes

### 🥔 Potato (3 classes)
- Early Blight
- Late Blight
- Healthy

### 🍅 Tomato (10 classes)
- Bacterial Spot
- Early Blight
- Late Blight
- Leaf Mold
- Septoria Leaf Spot
- Spider Mites
- Target Spot
- Yellow Leaf Curl Virus
- Tomato Mosaic Virus
- Healthy

---

## 📁 Project Structure

```
crop-disease-detection/
│
├── app.py                        # Flask application & routes
│
├── utils/
│   ├── predict.py                # Model loading & prediction logic
│   ├── db.py                     # SQLite database functions
│   └── disease_info.py           # Disease descriptions & class names
│
├── saved_model/
│   ├── potato_disease_model.keras
│   └── tomato_disease_model_V2.keras
│
├── templates/
│   ├── base.html                 # Base layout (navbar + footer)
│   ├── index.html                # Home page (standalone, no extends)
│   ├── result.html               # Prediction result page
│   ├── dashboard.html            # Live stats dashboard (3 tabs)
│   ├── history.html              # Test history card grid
│   ├── test_detail.html          # Single test detail page
│   └── about.html                # About page
│
├── static/
│   ├── uploads/                  # Uploaded/captured leaf images
│   └── css/
│       └── style.css
│
├── data/
│   └── app.db                    # SQLite database (auto-created)
│
├── fonts/
│   └── NotoSansDevanagari-Regular.ttf   # Hindi font for PDF reports
│
├── training/
│   ├── tomato_model.ipynb        # Tomato model training notebook
│   └── training.ipynb            # Potato model training notebook
│
├── tomato_dataset_500_images/    # Training dataset
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/SunnyKushwaha272/Crop-Disease-Detection-
cd crop-disease-detection
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your trained models
Place your `.keras` model files in the `saved_model/` folder:
```
saved_model/
├── potato_disease_model.keras
└── tomato_disease_model_V2.keras
```

### 5. Run the app
```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

---

## 📦 Requirements

```
flask
tensorflow
pillow
numpy
reportlab
werkzeug
```

Install all at once:
```bash
pip install flask tensorflow pillow numpy reportlab werkzeug
```

---

## 🗄️ Database

SQLite database is auto-created at `data/app.db` on first run. Schema:

```sql
CREATE TABLE tests (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT,
    predicted   TEXT,
    confidence  REAL,
    crop_type   TEXT,
    actual      TEXT,
    correct     INTEGER,
    timestamp   TEXT
);
```

To reset the database (clear all history):
```bash
del data\app.db        # Windows
rm data/app.db         # macOS / Linux
```

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page |
| POST | `/predict` | Run prediction on uploaded image |
| GET | `/dashboard` | Dashboard page |
| GET | `/api/dashboard-stats` | Live JSON stats for dashboard |
| GET | `/history` | Test history page |
| GET | `/test/<id>` | Single test detail |
| GET | `/about` | About page |
| GET | `/download-report/<id>` | Download PDF report |

---

## ⚙️ How It Works

1. User selects crop type (Potato / Tomato)
2. User uploads or captures a leaf image
3. Flask saves the image and calls `predict_disease()`
4. Image is resized to 256×256 and passed as raw pixels to the model
5. Model's baked `Rescaling(1/255)` normalises internally
6. `argmax` of softmax output gives the predicted class
7. Result, confidence, description, and treatment shown to user
8. Test saved to SQLite DB — reflected on dashboard and history instantly

---

## 🚀 Future Improvements

1. Add more crops — Corn, Pepper, Rice, Wheat
2. Grad-CAM heatmaps to highlight the diseased leaf area
3. Mobile app for offline field use by farmers
4. Auto crop detection — no manual selection needed
5. Real-time monitoring via drone or IoT field cameras
6. Weather-based disease risk forecasting

---

## 👨‍💻 Built With

- **Flask** — web framework
- **TensorFlow / Keras** — deep learning models
- **SQLite** — lightweight database
- **ReportLab** — PDF report generation
- **Bootstrap 5** — UI framework
- **Chart.js** — dashboard charts
- **PlantVillage Dataset** — training data

---

## 📄 License

This project is for educational and research purposes.
