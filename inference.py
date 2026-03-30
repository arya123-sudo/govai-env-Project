import os,json
from openai import OpenAI
from env.environment import GovEnv
from env.grader import grade

client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN")
)

MODEL_NAME = os.getenv("MODEL_NAME")
env = GovEnv()

def run_task(task):
    obs = env.reset(task)
    for _ in range(20):
        action = {"citizen_id":0,"scheme":"reject"}
        obs, reward, done, _ = env.step(action)
        if done:
            break
    return grade(env.history)

if __name__=="__main__":
    for t in ["easy","medium","hard"]:
        print(t, run_task(t))
