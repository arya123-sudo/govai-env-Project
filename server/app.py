from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from environment import GovEnv

app = FastAPI(
    title="GovAI Environment",
    description="Multi-step government policy simulation: welfare allocation, fraud auditing, reallocation.",
    version="2.0.0",
)

env = GovEnv()


class ResetRequest(BaseModel):
    task: Optional[str] = "easy"


class StepRequest(BaseModel):
    allocate: Optional[List[int]] = []
    investigate: Optional[List[int]] = []
    reallocate: Optional[List[int]] = []


@app.get("/")
def root():
    return {
        "message": "GovAI Environment is running",
        "version": "2.0.0",
        "endpoints": ["/reset", "/step", "/state", "/health"],
        "tasks": ["easy", "medium", "hard"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/state")
def get_state():
    return env._public_state()


@app.post("/reset")
def reset(body: ResetRequest = ResetRequest()):
    try:
        state = env.reset(task=body.task)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reset")
def reset_get(task: str = "easy"):
    try:
        state = env.reset(task=task)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(body: StepRequest):
    action = {
        "allocate": body.allocate,
        "investigate": body.investigate,
        "reallocate": body.reallocate,
    }
    try:
        result = env.step(action)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
