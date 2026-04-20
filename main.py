from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import io
from PIL import Image

# This imports your prediction brain
from model.inference import predict_image

# 1. Initialize FastAPI (This is the "app" uvicorn is looking for!)
app = FastAPI()

# 2. Link your CSS/JS files
# This assumes you have a folder named 'static' with your UI files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serves your frontend website."""
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Receives an image and returns the 99.3% accurate diagnosis."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    try:
        # Read the uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Run the 99% accurate model
        result = predict_image(image)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)