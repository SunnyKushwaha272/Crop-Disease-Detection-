import numpy as np
import os
from tensorflow.keras.models import load_model
from PIL import Image as PILImage

BASE_DIR = os.path.dirname(__file__)

POTATO_MODEL_PATH = os.path.join(BASE_DIR, "..", "saved_model", "potato_disease_model.keras")
TOMATO_MODEL_PATH = os.path.join(BASE_DIR, "..", "saved_model", "tomato_disease_model_V2.keras")

potato_model = load_model(POTATO_MODEL_PATH, compile=False)
tomato_model = load_model(TOMATO_MODEL_PATH, compile=False)

print("✅ Potato model loaded")
print("✅ Tomato model loaded")

# ─────────────────────────────────────────────────────────────────────────────
# IMAGE SIZE — must match IMAGE_SIZE used in training
# ─────────────────────────────────────────────────────────────────────────────
IMG_SIZE = (256, 256)

# ─────────────────────────────────────────────────────────────────────────────
# WHY WE DO NOT divide by 255 here:
#
# Both models were trained with this baked-in preprocessing:
#   resize_and_rescale = tf.keras.Sequential([
#       layers.Resizing(IMAGE_SIZE, IMAGE_SIZE),
#       layers.Rescaling(1.0/255)          ← model does /255 internally
#   ])
#
# So we must pass RAW pixel values (0–255) and let the model rescale itself.
# Dividing by 255 manually AND having the model do it again = double division:
#   raw pixel 200  →  /255  →  0.784  →  /255 again  →  0.003  ≈ black image
# A near-black image makes the model always predict the same class (Early Blight).
# ─────────────────────────────────────────────────────────────────────────────

potato_classes = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy"
]

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
    "Tomato_healthy"
]

human_labels = {
    "Potato___Early_blight":                       "Early Blight",
    "Potato___Late_blight":                        "Late Blight",
    "Potato___healthy":                            "Healthy",
    "Tomato_Bacterial_spot":                       "Bacterial Spot",
    "Tomato_Early_blight":                         "Early Blight",
    "Tomato_Late_blight":                          "Late Blight",
    "Tomato_Leaf_Mold":                            "Leaf Mold",
    "Tomato_Septoria_leaf_spot":                   "Septoria Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Spider Mites",
    "Tomato__Target_Spot":                         "Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus":       "Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus":                 "Tomato Mosaic Virus",
    "Tomato_healthy":                              "Healthy"
}


def predict_disease(img_path, crop_type):

    crop_type = crop_type.lower()

    if crop_type == "potato":
        model   = potato_model
        classes = potato_classes
    elif crop_type == "tomato":
        model   = tomato_model
        classes = tomato_classes
    else:
        raise ValueError(f"Invalid crop type: {crop_type!r}")

    # ── Load image — pass RAW pixels (0–255), model rescales internally ───
    img = PILImage.open(img_path).convert("RGB")
    img = img.resize(IMG_SIZE, PILImage.LANCZOS)
    arr = np.array(img, dtype=np.float32)       # ← NO /255 here
    arr = np.expand_dims(arr, axis=0)            # shape: (1, 256, 256, 3)

    # ── Predict ───────────────────────────────────────────────────────────
    preds           = model.predict(arr, verbose=0)[0]
    idx             = int(np.argmax(preds))
    predicted_class = classes[idx]
    predicted_human = human_labels.get(predicted_class, predicted_class)
    confidence      = float(preds[idx])

    # ── Debug output ──────────────────────────────────────────────────────
    print("\n===== Prediction =====")
    print(f"Crop      : {crop_type}")
    print(f"Predicted : {predicted_class}  ({round(confidence * 100, 2)}%)")
    print("All probs :")
    for c, p in zip(classes, preds):
        bar = "█" * int(p * 40)
        print(f"  {c:<52s} {p:.4f}  {bar}")
    print("======================\n")

    return predicted_class, predicted_human, confidence