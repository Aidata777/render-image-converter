from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from github import Github
from PIL import Image
from datetime import datetime
import io
import os

app = FastAPI()

# Configuración
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "Aidata777/render-image-converter"
BRANCH = "main"
FOLDER = "images"
USER = "Aidata777"

@app.get("/")
def home():
    return {"message": "Servicio activo"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Leer y convertir la imagen a JPEG
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        # Crear nombre único
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.jpg"

        # Conectar con GitHub y subir imagen
        github = Github(GITHUB_TOKEN)
        repo = github.get_repo(REPO_NAME)
        content = buffer.read()

        path = f"{FOLDER}/{filename}"
        repo.create_file(path, "add converted image", content, branch=BRANCH)

        # Generar URL pública
        public_url = f"https://{USER}.github.io/{REPO_NAME.split('/')[-1]}/{path}"

        return {"url": public_url}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

