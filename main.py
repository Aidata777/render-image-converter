from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image
import io
from datetime import datetime
from github import Github
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or "TU_GITHUB_TOKEN"
REPO_NAME = "Aidata777/render-image-converter"
BRANCH = "main"
FOLDER = "images"

# Reglas de Instagram
MIN_WIDTH = 320
MAX_WIDTH = 1440
MIN_RATIO = 0.8    # 4:5
MAX_RATIO = 1.91   # 1.91:1

@app.get("/")
def home():
    return {"message": "Service is running"}

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    width, height = image.size
    aspect_ratio = width / height

    # Ajustar relación de aspecto
    if aspect_ratio < MIN_RATIO:
        new_height = int(width / MIN_RATIO)
        offset = (height - new_height) // 2
        image = image.crop((0, offset, width, offset + new_height))
    elif aspect_ratio > MAX_RATIO:
        new_width = int(height * MAX_RATIO)
        offset = (width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, height))

    # Redimensionar según ancho
    width, height = image.size
    if width > MAX_WIDTH:
        new_height = int(MAX_WIDTH * height / width)
        image = image.resize((MAX_WIDTH, new_height), Image.LANCZOS)
    elif width < MIN_WIDTH:
        new_height = int(MIN_WIDTH * height / width)
        image = image.resize((MIN_WIDTH, new_height), Image.LANCZOS)

    # Guardar como JPEG
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=95)
    output.seek(0)

    # Subir a GitHub
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    content = output.read()
    repo.create_file(f"{FOLDER}/{filename}", "Upload image", content, branch=BRANCH)

    # Respuesta como texto plano (solo la URL)
    url = f"https://aidata777.github.io/render-image-converter/{FOLDER}/{filename}"
    return Response(content=url, media_type="text/plain")
