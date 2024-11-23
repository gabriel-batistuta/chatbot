from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io
import ollama

# Inicializa o app
app = FastAPI()

# Configura o cliente do Ollama
client = ollama.Client()

# Modelo de entrada de texto
class TextInput(BaseModel):
    text: str

@app.post("/chatbot/text/")
async def process_text(text: str = Form(...)):
    """
    Processa entrada de texto e retorna a resposta gerada pelo modelo.
    """
    try:
        # Realiza a consulta ao modelo LLaMA
        response = client.chat(
            model="llama",
            messages=[{"role": "user", "content": text}],
        )
        return {"response": response.get("content", "Erro ao gerar resposta.")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar texto: {e}")

@app.post("/chatbot/image/")
async def process_image(file: UploadFile = File(...)):
    """
    Processa entrada de imagem e retorna informações sobre ela.
    """
    try:
        # Leia a imagem enviada pelo usuário
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Realize algum processamento básico com Pillow
        image_info = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
        }
        return {"image_info": image_info, "message": "Imagem processada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")
