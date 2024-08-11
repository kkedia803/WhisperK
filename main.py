# main.py

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import uuid
from transcriber import transcribe_audio

# Create an instance of FastAPI
app = FastAPI()

# Define the upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    # Generate a unique file ID
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.mp3")

    # Save the uploaded file to the upload directory
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Transcribe the saved audio file
    transcription = transcribe_audio(file_path)
    response = {
        "file_id": file_id,
        "transcription": transcription
    }

    return JSONResponse(content=response)

@app.get("/transcription/{file_id}")
async def get_transcription(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.mp3")
    if os.path.exists(file_path):
        transcription = transcribe_audio(file_path)
        response = {
            "file_id": file_id,
            "transcription": transcription
        }
        return JSONResponse(content=response)
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)
