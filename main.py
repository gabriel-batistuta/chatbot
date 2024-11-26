from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io
import ollama
import uvicorn
import json
from fastapi.responses import StreamingResponse
import asyncio  # Necessário para enviar respostas em partes

# Inicializa o app
app = FastAPI()

# Configura o cliente do Ollama
client = ollama.Client()

# Adiciona o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens. Substitua por uma lista específica para maior segurança.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Modelo de entrada de texto
class TextInput(BaseModel):
    text: str

@app.post("/chatbot/text/")
async def process_text_stream(text: str = Form(...)):
    """
    Processa entrada de texto e retorna a resposta gerada pelo LLaMA como um stream.
    """
    try:
        print(f"Texto recebido: {text}")

        async def stream_response():
            response = client.chat(
                model="llama3",
                messages=[{"role": "user", "content": text}],
                stream=True,
            )
            
            print(dir(response))  # Para depuração, imprime métodos disponíveis
            print(response)       # Confirma o objeto retornado
            print(type(response)) # Exibe o tipo do objeto retornado

            for chunk in response:
                print(f"Chunk recebido: {chunk}")  # Loga o chunk recebido
                if "message" in chunk and "content" in chunk["message"]:  # Verifica a estrutura
                    yield chunk["message"]["content"]  # Envia o conteúdo do chunk
                    await asyncio.sleep(0)  # Libera o loop para continuar
                else:
                    print(f"Chunk sem conteúdo relevante: {chunk}")  # Log para chunks inesperados


        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        print(f"Erro ao processar texto: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar texto: {e}")


# @app.post("/chatbot/text/")
# async def process_text(text: str = Form(...)):
#     """
#     Processa entrada de texto e retorna a resposta gerada pelo modelo.
#     """
#     try:
#         print(f"Texto recebido: {text}")  # Loga o texto recebido
#         # Realiza a consulta ao modelo LLaMA
#         response = client.chat(
#             model="llama3",
#             messages=[{"role": "user", "content": text}],
#         )
#         print(f"Resposta do modelo: {response['message']['content']}")  # Loga a resposta do modelo
#         # print(type(response))
#         # print(dir(response))
#         return response['message']['content']

#     except ValueError as ve:
#         print(f"Erro de validação: {ve}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         print(f"Erro no servidor: {e}")
#         raise HTTPException(status_code=500, detail=f"Erro ao processar texto: {e}")

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
