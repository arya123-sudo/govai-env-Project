import os
import json
import re
from openai import OpenAI
from environment import GovEnv


def build_prompt(state: dict) -> str:
    step = state["step"]
    citizens = state["citizens"]
    budget = state["budget"]
    cfg = state["config"]
    audit = state.get("audit_results", {})

    citizen_lines = "\n".join(
        f"  id={c['id']} income={c['income']} health_risk={c['health_risk']} fraud_risk={c['fraud_risk']}"
        for c in citizens
    )

    if step == 0:
        return f"""You are a government policy AI making welfare decisions.

TASK: Welfare Allocation
Budget available: {budget}
Cost per allocation: {cfg['cost_per_allocation']}
Income threshold for eligibility: {cfg['income_threshold']}

Citizens:
{citizen_lines}

Select citizen IDs to allocate welfare to. Prioritize low-income citizens. Do NOT overspend the budget.

Respond ONLY with valid JSON, no explanation:
{{"allocate": [list of citizen ids]}}"""

    elif step == 1:
        return f"""You are a government policy AI conducting fraud audits.

TASK: Fraud Investigation
Fraud risk threshold: {cfg['fraud_threshold']} (higher = more suspicious)

Citizens:
{citizen_lines}

Select citizen IDs with fraud_risk above {cfg['fraud_threshold']} to investigate.

Respond ONLY with valid JSON, no explanation:
{{"investigate": [list of citizen ids]}}"""

    elif step == 2:
        audit_lines = "\n".join(
            f"  id={cid}: {result}" for cid, result in audit.items()
        ) or "  (no audits conducted)"

        return f"""You are a government policy AI making final reallocation decisions.

TASK: Final Reallocation
Income threshold: {cfg['income_threshold']}
Audit results from previous step:
{audit_lines}

Citizens:
{citizen_lines}

Select citizen IDs to receive final welfare: they must be low-income AND not flagged as fraudulent.

Respond ONLY with valid JSON, no explanation:
{{"reallocate": [list of citizen ids]}}"""

    return "{}"


def parse_action(text: str, step: int) -> dict:
    """Extract JSON from model response robustly."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block from response
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Fallback safe actions per step
    fallbacks = [
        {"allocate": []},
        {"investigate": []},
        {"reallocate": []},
    ]
    print(f"[WARN] Could not parse response at step {step}. Using fallback. Raw: {text[:200]}", flush=True)
    return fallbacks[step]


def decide(client, state: dict) -> dict:
    prompt = build_prompt(state)
    step = state["step"]

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise government policy AI. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.0,
        )
        text = response.choices[0].message.content or ""
        return parse_action(text, step)

    except Exception as e:
        print(f"[ERROR] API call failed at step {step}: {e}", flush=True)
        return [{"allocate": []}, {"investigate": []}, {"reallocate": []}][step]


def run_task(client, env: GovEnv, task: str) -> dict:
    print(f"\n{'='*50}", flush=True)
    print(f"[START] task={task}", flush=True)

    state = env.reset(task)
    total_reward = 0.0
    step_num = 0
    step_rewards = []

    while True:
        action = decide(client, state)
        print(f"[ACTION] step={step_num} action={action}", flush=True)

        result = env.step(action)
        reward = result["reward"]
        total_reward += reward
        step_rewards.append(round(reward, 4))

        print(f"[STEP] step={step_num} reward={reward} info={result['info']}", flush=True)

        state = result["state"]
        step_num += 1

        if result["done"]:
            break

    score = round(total_reward / 3, 4)
    print(f"[END] task={task} score={score} step_rewards={step_rewards}", flush=True)
    return {"task": task, "score": score, "step_rewards": step_rewards}


def main():
    api_base = os.environ.get("API_BASE_URL")
    api_key = os.environ.get("API_KEY")

    if not api_key:
        print("[ERROR] API_KEY environment variable not set.", flush=True)
        exit(1)

    client = OpenAI(base_url=api_base, api_key=api_key)
    env = GovEnv()

    results = []
    for task in ["easy", "medium", "hard"]:
        result = run_task(client, env, task)
        results.append(result)

    print("\n" + "="*50, flush=True)
    print("[SUMMARY]", flush=True)
    for r in results:
        print(f"  task={r['task']} score={r['score']} steps={r['step_rewards']}", flush=True)

    avg = round(sum(r["score"] for r in results) / len(results), 4)
    print(f"  average_score={avg}", flush=True)


if __name__ == "__main__":
    main()
