from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from transcriber import transcribe_audio

# Initialize FastAPI
app = FastAPI()

# Configure Cloudinary
cloudinary.config(
    cloud_name="dae0vc8li",
    api_key="739829642419489",
    api_secret="-I_jaD8hybbn16nwPBllidAEs7o"
)


LOCAL_DOWNLOAD_DIR = "downloaded_files"
os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)

def download_file_from_url(url, local_path):
    response = requests.get(url)
    with open(local_path, "wb") as file:
        file.write(response.content)

def transcribe_file_from_cloudinary(file_id: str):
    result = cloudinary.api.resource(file_id, resource_type="video")
    file_url = result['url']
    
    # Download the file from Cloudinary
    local_file_path = os.path.join(LOCAL_DOWNLOAD_DIR, f"{file_id}.mp3")
    download_file_from_url(file_url, local_file_path)

    
    # Perform transcription
    transcription = transcribe_audio(local_file_path)
    
    # Save the transcription to a file or database for retrieval
    # transcription_path = f"/tmp/{file_id}.txt"
    # with open(transcription_path, "w") as f:
    #     f.write(transcription)
    
    return transcription

@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    # Generate a unique file ID
    file_id = str(uuid.uuid4())

    # Upload the file to Cloudinary directly
    try:
        result = cloudinary.uploader.upload(file.file, public_id=file_id, resource_type="video")
        cloudinary_url = result['url']
        
        response = {
            "file_id": file_id,
            "cloudinary_url": cloudinary_url,
            "status": "File Uploaded"
        }
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/transcription/{file_id}")
async def get_transcription(file_id: str):
    text = transcribe_file_from_cloudinary(file_id)
    try:
        response = {
            "file_id": file_id,
            "transcription": text
        }
        return JSONResponse(content=response)
    except:
        return JSONResponse(content={"error": "Transcription in progress or file not found"}, status_code=404)
