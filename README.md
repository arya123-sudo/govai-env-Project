---
title: govai-env
emoji: "🤖"
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "0.0.1"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🏛️ GovAI Env — Government Welfare Policy Simulation Environment

An **OpenEnv** reinforcement-learning environment that simulates government welfare policy decisions. An AI agent must allocate welfare funds to low-income citizens, audit high-risk fraud cases, and reallocate funds based on the audit results — all under a tight budget, with noisy signals.

It is designed to evaluate AI decision-making in **resource-constrained, adversarial settings**: helping everyone is impossible, fraud signals are unreliable, and every wrong decision costs reward.

## 🎮 How an Episode Works

Each episode runs for **3 steps**:

| Step | Phase | Agent's job |
|---|---|---|
| 0 | **Welfare Allocation** | Choose which citizens receive funding |
| 1 | **Fraud Audit** | Choose which citizens to investigate |
| 2 | **Reallocation** | Based on audit results, choose the final beneficiaries |

## 📋 Tasks

| Task | Citizens | Budget | Income threshold | Fraud threshold | Signal noise |
|---|---|---|---|---|---|
| `easy` | 6 | ₹100,000 | ₹20,000 | 0.60 | None — clear signals |
| `medium` | 8 | ₹60,000 | ₹25,000 | 0.65 | ±0.2 on fraud scores |
| `hard` | 10 | ₹35,000 (very tight) | ₹28,000 | 0.70 | High noise |

## 🏆 Scoring

- `reward = correct_decisions − 0.5 × wrong_decisions` per step
- **Budget overrun** applies an extra penalty proportional to the overage
- Step rewards are normalized (`reward / citizen_count`, clamped to **[0.0, 1.0]**)
- **Final score** = mean of the 3 step rewards

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/reset` | Start a new episode — body: `{"task": "easy"}` |
| POST | `/step` | Submit actions — body: `{"allocate": [], "investigate": [], "reallocate": []}` |
| GET | `/state` | Current environment state |
| GET | `/health` | Health check |

## ▶️ Run It Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the environment server
uvicorn app:app --host 0.0.0.0 --port 8000

# Or with Docker
docker build -t govai-env .
docker run -p 8000:8000 govai-env
```

Then run an agent against it with `inference.py`, or explore the API at `http://localhost:8000/docs`.

## 📂 Project Structure

```
├── app.py            # FastAPI application entrypoint
├── environment.py    # GovEnv — the simulation environment (tasks, state, scoring)
├── inference.py      # Agent inference / evaluation script
├── openenv.yaml      # OpenEnv spec — endpoints, tasks, scoring rules
├── backend/          # Backend modules
├── server/           # Server entrypoint (server.app:main)
├── frontend/         # Frontend UI
├── Dockerfile        # Container build (also used by the HF Space)
└── requirements.txt
```

## 🛠️ Tech Stack

- **Python 3.10** · **FastAPI** · **Uvicorn**
- **OpenEnv Core** (`openenv-core >= 0.2.0`) — environment spec & API pattern
- **Docker** — deployment, including Hugging Face Spaces

## 👤 Author

**Arya Yaligar** — [GitHub](https://github.com/arya123-sudo) · [LinkedIn](https://www.linkedin.com/in/arya-yaligar-ba15a2385)
