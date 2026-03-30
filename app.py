from fastapi import FastAPI
from environment import GovEnv

app = FastAPI()
env = GovEnv()

@app.get("/")
def root():
    return {"message": "GovAI running"}

# ✅ SUPPORT BOTH (VERY IMPORTANT)
@app.get("/reset")
@app.post("/reset")
def reset():
    return env.reset()

@app.get("/health")
def health():
    return {"status": "ok"}