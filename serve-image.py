from io import BytesIO
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import torch
import io
from diffusers import DiffusionPipeline

app = FastAPI()

pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/imagine", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def generate(prompt: str):
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt parameter cannot be empty")

    try:
        images = pipe(prompt=prompt).images[0]
        memory_stream = io.BytesIO()
        images.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        image_data = memory_stream.getvalue()
        return Response(content=image_data, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))