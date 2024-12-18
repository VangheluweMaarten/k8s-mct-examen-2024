import json
import uvicorn
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os
import io
# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

BACKEND_URL = os.getenv("BACKEND_URL", "http://api:8000")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

connected_clients = []

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """Unified WebSocket endpoint for CLEAR and LOG messages."""
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.post("/send-clear/")
async def send_clear():
    """Send 'CLEAR' signal to connected WebSocket clients."""
    for client in connected_clients:
        json_log = {"type": "CLEAR"}
        await client.send_text(json.dumps(json_log))
    return {"status": "CLEAR signal sent"}


@app.post("/send-log/")
async def send_log(message: str):
    """Send 'LOGS' to connected WebSocket clients."""
    for client in connected_clients:
        json_log = {"message": message, "type": "LOG"}
        await client.send_text(json.dumps(json_log))
    return {"status": "LOG message sent"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Retrieve the score from an environment variable
    score = os.getenv("SCORE", "0")
    name = os.getenv("NAME", "VUL MIJ IN")
    
    # Render the template with the score
    return templates.TemplateResponse("index.html", {"request": request, "score": score, "name": name})


@app.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    # Send request to backend
    try:
        contents = await image.read()
        # Save image
        with open("/app/static/uploaded_images/" + image.filename, "wb") as buffer:
            buffer.write(contents)
        response = requests.post(f"{BACKEND_URL}/upload/", files={"image": (image.filename, io.BytesIO(contents))})
        response_data = response.json()
        predicted_class = response_data["category"]
        confidence = response_data["confidence"]
        # Receive response from backend
        return {"category": predicted_class, "confidence": confidence}
    except Exception as e:
        return {"error": f"Something went wrong, is the API on? Is it accessible on {BACKEND_URL}?\n\nError: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
