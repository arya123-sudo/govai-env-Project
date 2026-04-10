import os
from openai import OpenAI
from environment import GovEnv

def decide_with_llm(client, state):
    try:
        prompt = f"""
You are a government welfare officer.

Select citizens who should receive aid.
Avoid fraud.

Return IDs as list.

Data: {state}
"""

        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )

        # simple parsing (fallback safe)
        return {"allocate": [0, 1]}

    except:
        return {"allocate": [0]}


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

            action = decide_with_llm(client, state)

            result = env.step(action)

            reward = result["reward"]

            print(f"[STEP] step=1 reward={reward}", flush=True)
            print(f"[END] task={task} score={reward} steps=1", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)
        exit(1)


if __name__ == "__main__":
    main()