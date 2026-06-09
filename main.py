from fastapi import FastAPI
from pydantic import BaseModel
from app.scraper import scrape_product
from app.video_engine import trigger_colab_gpu

app = FastAPI(title="Video Agent Backend")

class RequestBody(BaseModel):
    amazon_url: str
    pinggy_url: str

@app.post("/api/generate")
async def generate_pipeline(payload: RequestBody):
    s = await scrape_product(payload.amazon_url)
    t = s['title'][:35].strip()
    
    l = [
        f"extreme close up macro shot of {t} shoe fabric and laces, 8k resolution, cinematic lighting",
        f"low angle shot of {t} shoe sole hitting the ground, slow motion, 8k",
        f"close up of the logo on the {t} shoe, neon lighting, highly detailed",
        "close up portrait of athletic runner's highly detailed face, sweating, determination, 8k",
        f"wide cinematic shot of runner wearing {t} sprinting through neon city at night, 8k"
    ]
    n = "blurry, distorted, bad quality, person, human, face, text, watermark"
    
    r = []
    for i, p in enumerate(l):
        c = await trigger_colab_gpu(p, n, payload.pinggy_url)
        r.append(c)
        
    return {
        "status": "Storyboard completely rendered",
        "product": s['title'],
        "jobs": r
    }