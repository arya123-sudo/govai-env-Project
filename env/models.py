from pydantic import BaseModel
from typing import List

class Citizen(BaseModel):
    id: int
    income: float
    family_size: int
    health_risk: int
    region: str
    fraud_risk: float

class Observation(BaseModel):
    citizens: List[Citizen]
    remaining_budget: float
    time_step: int

class Action(BaseModel):
    citizen_id: int
    scheme: str

class Reward(BaseModel):
    value: float
