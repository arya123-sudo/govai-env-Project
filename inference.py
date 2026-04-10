import os
from openai import OpenAI
from environment import GovEnv
import json

def decide(client, state):
    try:
        prompt = f"""
You are a government policy agent.

State:
{state}

Return JSON:
{{
 "allocate": [],
 "investigate": [],
 "reallocate": []
}}
"""

        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )

        text = response.choices[0].message.content

        return json.loads(text)

    except:
        # fallback safe policy
        return {"allocate": [0,1], "investigate": [0], "reallocate": [1]}


def main():
    try:
        client = OpenAI(
            base_url=os.environ.get("API_BASE_URL"),
            api_key=os.environ.get("API_KEY")
        )

        env = GovEnv()
        tasks = ["easy", "medium", "hard"]

        for task in tasks:
            print(f"[START] task={task}", flush=True)

            state = env.reset(task)

            done = False
            step_num = 1
            total_reward = 0

            while not done:
                action = decide(client, state)

                result = env.step(action)

                reward = result["reward"]
                total_reward += reward

                print(f"[STEP] step={step_num} reward={reward}", flush=True)

                state = result["state"]
                done = result["done"]
                step_num += 1

            score = max(0, min(1, total_reward / 3))

            print(f"[END] task={task} score={score} steps={step_num-1}", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)
        exit(1)


if __name__ == "__main__":
    main()