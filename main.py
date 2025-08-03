from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io, os
from github import Github
from datetime import datetime

app = FastAPI()

# Variables de entorno
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "TU_USUARIO/TU_REPOSITORIO"
BRANCH = "main"
FOLDER = "images"

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=95)
    output.seek(0)

    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    content = output.read()
    repo.create_file(f"{FOLDER}/{filename}", "add converted image", content, branch=BRANCH)

    url = f"https://TU_USUARIO.github.io/TU_REPOSITORIO/{FOLDER}/{filename}"
    return {"url": url}"
