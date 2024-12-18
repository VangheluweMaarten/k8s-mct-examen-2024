import io
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from PIL import Image
from ai_model import classify_image

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    os.makedirs("/mnt/data/uploaded_images", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def index():
    return "Visit the /docs page to view this API!"

@app.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    # Read image contents
    contents = await image.read()

    # Save image
    with open("/mnt/data/uploaded_images/" + image.filename, "wb") as buffer:
        buffer.write(contents)

    # Process image
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    index, predicted_class, confidence = classify_image(image)
    print(index, predicted_class, confidence)

    # Return result
    return {"category": predicted_class, "confidence": confidence}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
