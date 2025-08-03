from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from github import Github
from PIL import Image
from datetime import datetime
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_NAME = "Aidata777/render-image-converter"
BRANCH = "main"
FOLDER = "images"

# Instagram limits
MAX_WIDTH = 1440
MIN_WIDTH = 320
MIN_RATIO = 0.8   # 4:5
MAX_RATIO = 1.91  # 1.91:1

def resize_for_instagram(image: Image.Image) -> Image.Image:
    width, height = image.size
    aspect_ratio = width / height

    # Ajuste de proporción si está fuera de rango
    if aspect_ratio < MIN_RATIO:
        # Demasiado alto → recortar arriba/abajo
        new_height = int(width / MIN_RATIO)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    elif aspect_ratio > MAX_RATIO:
        # Demasiado ancho → recortar lados
        new_width = int(height * MAX_RATIO)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))

    # Redimensionar a máximo ancho permitido si excede
    width, height = image.size
    if width > MAX_WIDTH:
        ratio = MAX_WIDTH / width
        image = image.resize((MAX_WIDTH, int(height * ratio)), Image.ANTIALIAS)

    # Asegura mínimo ancho
    if image.size[0] < MIN_WIDTH:
        ratio = MIN_WIDTH / image.size[0]
        image = image.resize((MIN_WIDTH, int(image.size[1] * ratio)), Image.ANTIALIAS)

    return image

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    image = resize_for_instagram(image)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=95)
    output.seek(0)

    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    content = output.read()
    repo.create_file(f"{FOLDER}/{filename}", "add converted image", content, branch=BRANCH)

    url = f"https://aidata777.github.io/render-image-converter/{FOLDER}/{filename}"
    return {"url": url}
