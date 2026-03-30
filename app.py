from fastapi import FastAPI
from env.environment import GovEnv

app = FastAPI()
env = GovEnv()

@app.get("/")
def root():
    return {"message":"GovAI running"}

@app.get("/reset")
def reset():
    return env.reset()

@app.get("/health")
def health():
    return {"status":"ok"}
