# backend/app.py  — CLEAN VERSION (no mango model)
import io
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import tensorflow as tf  # type: ignore

# ---------------------------
# FastAPI Setup
# ---------------------------
app = FastAPI(title="Plant Disease Detection API")

# Allow all CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Model paths (ONLY YOUR MODEL)
# ---------------------------
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

MODEL_PATH = MODELS_DIR / "plant_model_best.h5"    # primary recommended model
FALLBACK_MODEL_PATH = MODELS_DIR / "plant_model.keras"  # used only if h5 fails
CLASS_INDEX_FILE = MODELS_DIR / "class_indices.json"

IMG_SIZE = 224  # model input size

model = None
index_to_class = {}

# ---------------------------
# Load model + classes
# ---------------------------
def load_model_files():
    global model, index_to_class

    # Load model
    if MODEL_PATH.exists():
        model_to_load = MODEL_PATH
    elif FALLBACK_MODEL_PATH.exists():
        model_to_load = FALLBACK_MODEL_PATH
    else:
        raise RuntimeError("No model file found in models/ directory.")

    print(f"Loading model from: {model_to_load}")
    try:
        model = tf.keras.models.load_model(str(model_to_load))
        print("Model loaded!")
    except Exception as e:
        print("ERROR loading model:", e)
        raise e

    # Load class index mapping
    if not CLASS_INDEX_FILE.exists():
        raise RuntimeError("class_indices.json not found in models/ directory.")

    with open(CLASS_INDEX_FILE, "r") as f:
        class_indices = json.load(f)

    # Convert {class_name: index} → {index: class_name}
    global index_to_class
    index_to_class = {int(v): k for k, v in class_indices.items()}

    print(f"Loaded {len(index_to_class)} classes.")

# Run at startup
@app.on_event("startup")
def startup_event():
    load_model_files()

# ---------------------------
# Preprocessing
# ---------------------------
def preprocess_image_bytes(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img).astype(np.float32)
    arr = tf.keras.applications.efficientnet.preprocess_input(arr)  # MATCH TRAINING
    arr = np.expand_dims(arr, axis=0)
    return arr

# ---------------------------
# Predict endpoint
# ---------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...), top_k: int = Query(3, ge=1, le=10)):
    if model is None:
        raise HTTPException(500, "Model not loaded")

    image_bytes = await file.read()
    arr = preprocess_image_bytes(image_bytes)

    preds = model.predict(arr)[0]
    preds = preds.ravel()

    # Take top-k predictions
    k = min(top_k, len(preds))
    idxs = preds.argsort()[-k:][::-1]

    results = []
    for i in idxs:
        results.append({
            "label": index_to_class.get(int(i), f"class_{i}"),
            "confidence": float(preds[int(i)]),
            "index": int(i)
        })

    return {"predictions": results}

# ---------------------------
# Run server manually
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)