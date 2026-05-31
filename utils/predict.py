import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from PIL import Image as PILImage

BASE_DIR = os.path.dirname(__file__)

POTATO_MODEL_PATH = os.path.join(BASE_DIR, "..", "saved_model", "potato_disease_model_v2.keras")
TOMATO_MODEL_PATH = os.path.join(BASE_DIR, "..", "saved_model", "tomato_disease_model_V2.keras")

potato_model = load_model(POTATO_MODEL_PATH, compile=False)
tomato_model = load_model(TOMATO_MODEL_PATH, compile=False)

print("⏳ Loading MobileNetV2 plant detector...")
mobilenet = MobileNetV2(weights="imagenet", include_top=True)
print("✅ MobileNetV2 loaded")
print("✅ Potato model loaded")
print("✅ Tomato model loaded")

# ── Image sizes ───────────────────────────────────────────────────────────
# ✅ FIX: EfficientNetB4 was trained on 380×380 — must match exactly
IMG_SIZE       = (380, 380)
MOBILENET_SIZE = (224, 224)

# ── Thresholds ────────────────────────────────────────────────────────────
WRONG_CROP_THRESHOLD  = 0.55   # below this → warn about wrong crop
# ✅ NEW: confidence threshold — below this → treat as Unknown
CONFIDENCE_THRESHOLD  = 0.75

# ── ImageNet labels that confirm image is NOT a plant at all ──────────────
NOT_PLANT_LABELS = {
    "person", "people", "man", "woman", "boy", "girl", "face", "hand",
    "dog", "cat", "bird", "car", "truck", "phone", "laptop", "keyboard",
    "book", "pen", "pencil", "paper", "wall", "floor", "desk", "chair",
    "table", "bottle", "cup", "food", "bread", "pizza", "burger",
    "building", "sky", "road", "stone", "rock", "sand", "water", "ocean"
}

# ── ImageNet labels that suggest potato/tomato plant ─────────────────────
POTATO_TOMATO_KEYWORDS = {
    "potato", "tomato",
    "bell pepper", "eggplant", "artichoke", "cardoon",
    "corn", "rapeseed", "cauliflower", "broccoli", "cabbage",
    "gyromitra", "bolete", "agaric",
    "leaf", "plant", "herb", "weed", "vine",
    "strawberry", "raspberry", "blackberry",
}

# ── Class lists ───────────────────────────────────────────────────────────
# ✅ FIX: Added 'Unknown' as the 4th potato class
potato_classes = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Unknown"
]

# ✅ FIX: Added 'Unknown' as the 11th tomato class
tomato_classes = [
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy",
    "Unknown"
]

# ── Human readable labels ─────────────────────────────────────────────────
human_labels = {
    "Potato___Early_blight":                        "Early Blight",
    "Potato___Late_blight":                         "Late Blight",
    "Potato___healthy":                             "Healthy",
    "Tomato_Bacterial_spot":                        "Bacterial Spot",
    "Tomato_Early_blight":                          "Early Blight",
    "Tomato_Late_blight":                           "Late Blight",
    "Tomato_Leaf_Mold":                             "Leaf Mold",
    "Tomato_Septoria_leaf_spot":                    "Septoria Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite":  "Spider Mites",
    "Tomato__Target_Spot":                          "Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus":        "Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus":                  "Tomato Mosaic Virus",
    "Tomato_healthy":                               "Healthy",
    # ✅ NEW: Unknown human label for both models
    "Unknown":                                      "Unknown Leaf"
}


def _load_image(img_path, size=IMG_SIZE):
    """
    Load and resize image to the correct size for EfficientNetB4.
    ✅ No manual rescaling — EfficientNetB4 has built-in preprocessing.
    """
    img = PILImage.open(img_path).convert("RGB")
    img = img.resize(size, PILImage.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)   # (1, 380, 380, 3)
    return arr


def _check_image_with_mobilenet(img_path):
    """
    Use MobileNetV2 as a gateway to check if image is a valid crop leaf.

    Returns: (is_valid_crop_leaf, top_label, top_confidence, all_labels)
    - If top labels clearly NOT a plant  → reject immediately
    - If top labels are plant/leaf related → allow through
    - If completely different plant (rose, oak etc.) → reject with warning
    """
    img = PILImage.open(img_path).convert("RGB").resize(MOBILENET_SIZE, PILImage.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    arr = preprocess_input(arr)

    preds   = mobilenet.predict(arr, verbose=0)
    decoded = decode_predictions(preds, top=10)[0]

    print("\n── MobileNetV2 top 10 predictions ──")
    all_labels = []
    for _, label, conf in decoded:
        print(f"  {label:<40s} {round(conf * 100, 2)}%")
        all_labels.append(label.lower().replace("_", " "))

    top_label = decoded[0][1].lower().replace("_", " ")
    top_conf  = float(decoded[0][2])

    # Check if clearly NOT a plant (top 3 labels)
    for label in all_labels[:3]:
        for not_plant in NOT_PLANT_LABELS:
            if not_plant in label:
                print(f"  ❌ Not a plant: '{label}'")
                return False, decoded[0][1], top_conf, all_labels

    # Check if any top 10 label matches potato/tomato keywords
    for label in all_labels:
        for keyword in POTATO_TOMATO_KEYWORDS:
            if keyword in label:
                print(f"  ✅ Matches crop keyword: '{label}' contains '{keyword}'")
                return True, decoded[0][1], top_conf, all_labels

    # It's some kind of plant but doesn't match potato/tomato keywords
    print(f"  ⚠️ Plant detected but not potato/tomato related: '{top_label}'")
    return False, decoded[0][1], top_conf, all_labels


def predict_disease(img_path, crop_type):
    """
    Full prediction pipeline for potato or tomato leaf disease.

    Stage 1 — MobileNetV2 gateway:
        Rejects non-plant images (walls, people, food etc.)

    Stage 2 — EfficientNetB4 primary model:
        Classifies the leaf into disease classes.
        Now includes 'Unknown' class for non-matching leaves.

    Stage 3 — Confidence threshold check:
        If confidence < 0.75 → treated as Unknown even if model
        predicted a disease class.

    Stage 4 — Wrong crop detection:
        Runs other crop model to warn if image looks like wrong plant.

    Returns:
        predicted_class  (str)   — raw class name e.g. 'Potato___Early_blight' or 'Unknown'
        predicted_human  (str)   — readable name e.g. 'Early Blight' or 'Unknown Leaf'
        confidence       (float) — 0.0 to 1.0
        wrong_crop_warning (str | None) — warning message or None

    Raises:
        ValueError — if image fails MobileNetV2 gate or is Unknown leaf
    """
    crop_type = crop_type.lower()

    if crop_type == "potato":
        model       = potato_model
        classes     = potato_classes
        other_model = tomato_model
        other_crop  = "Tomato"
        crop_label  = "Potato 🥔"
    elif crop_type == "tomato":
        model       = tomato_model
        classes     = tomato_classes
        other_model = potato_model
        other_crop  = "Potato"
        crop_label  = "Tomato 🍅"
    else:
        raise ValueError(f"Invalid crop type: {crop_type!r}. Must be 'potato' or 'tomato'.")

    # ── STAGE 1: MobileNetV2 gateway ──────────────────────────────────────
    # Rejects non-plant images before wasting time on EfficientNetB4
    is_valid, top_label, top_conf, all_labels = _check_image_with_mobilenet(img_path)

    if not is_valid:
        raise ValueError(
            f"❌ This image does not appear to be a plant leaf. "
            f"Please upload a clear photo of a {crop_label} leaf only."
        )

    # ── STAGE 2: EfficientNetB4 primary model ────────────────────────────
    arr             = _load_image(img_path)          # (1, 380, 380, 3)
    preds           = model.predict(arr, verbose=0)[0]
    idx             = int(np.argmax(preds))
    predicted_class = classes[idx]
    confidence      = float(preds[idx])

    print(f"\n===== Prediction =====")
    print(f"Crop      : {crop_type}")
    print(f"Predicted : {predicted_class}  ({round(confidence * 100, 2)}%)")

    # ── STAGE 3: Confidence threshold + Unknown class check ───────────────
    # ✅ NEW: two-layer Unknown detection
    # Layer 1 — model itself predicted Unknown class
    # Layer 2 — model predicted a disease but with low confidence
    if predicted_class == "Unknown" or confidence < CONFIDENCE_THRESHOLD:
        predicted_class = "Unknown"
        predicted_human = "Unknown Leaf"
        print(f"  ⚠️ Unknown leaf detected "
              f"(class={classes[idx]}, confidence={round(confidence*100,2)}%)")
        print("======================\n")
        raise ValueError(
            f"⚠️ This leaf does not appear to be a {crop_label} leaf. "
            f"Our model could not identify it as a known {crop_type} disease or healthy leaf. "
            f"Please upload a clear, close-up photo of a {crop_label} leaf."
        )

    predicted_human = human_labels.get(predicted_class, predicted_class)

    # ── STAGE 4: Wrong crop detection ────────────────────────────────────
    # Run the OTHER crop model — if it's more confident → likely wrong crop
    other_preds      = other_model.predict(arr, verbose=0)[0]
    other_confidence = float(np.max(other_preds))
    other_idx        = int(np.argmax(other_preds))
    other_classes    = tomato_classes if crop_type == "potato" else potato_classes
    other_predicted  = other_classes[other_idx]

    print(f"Other crop: {other_crop} → {other_predicted} ({round(other_confidence * 100, 2)}%)")

    # Print all class probabilities
    print("All probs :")
    for c, p in zip(classes, preds):
        bar = "█" * int(p * 40)
        print(f"  {c:<55s} {p:.4f}  {bar}")
    print("======================\n")

    wrong_crop_warning = None

    # ✅ FIX: Only warn about wrong crop if other model's prediction
    # is NOT Unknown — no point warning "looks like tomato" if tomato
    # model also says Unknown
    if (confidence < WRONG_CROP_THRESHOLD
            and other_confidence > confidence
            and other_predicted != "Unknown"):
        wrong_crop_warning = (
            f"⚠️ Low confidence ({round(confidence * 100, 1)}%). "
            f"This image looks more like a {other_crop} leaf "
            f"({round(other_confidence * 100, 1)}% confidence). "
            f"Please re-upload and select the correct crop type."
        )

    return predicted_class, predicted_human, confidence, wrong_crop_warning