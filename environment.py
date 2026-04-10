import random

class GovEnv:
    def __init__(self):
        self.budget = 100000
        self.time_step = 0
        self.citizens = []
        self.task = "easy"

    def reset(self, task="easy"):
        self.task = task
        self.time_step = 0
        self.budget = 100000

        self.citizens = [
            {
                "id": i,
                "income": random.randint(5000, 50000),
                "health_risk": random.randint(1, 10),
                "fraud_risk": round(random.uniform(0, 1), 2)
            }
            for i in range(6)
        ]

        return self.state()

    def step(self, action):
        reward = 0

        # -------- STEP 1: Allocation --------
        if self.time_step == 0:
            for c in self.citizens:
                if c["id"] in action.get("allocate", []):
                    if c["income"] < 20000:
                        reward += 1
                    else:
                        reward -= 0.5

            self.budget -= len(action.get("allocate", [])) * 5000

        # -------- STEP 2: Audit --------
        elif self.time_step == 1:
            for c in self.citizens:
                if c["id"] in action.get("investigate", []):
                    if c["fraud_risk"] > 0.6:
                        reward += 1
                    else:
                        reward -= 0.5

        # -------- STEP 3: Correction --------
        elif self.time_step == 2:
            for c in self.citizens:
                if c["id"] in action.get("reallocate", []):
                    if c["income"] < 20000 and c["fraud_risk"] < 0.5:
                        reward += 1

        # Budget penalty
        if self.budget < 0:
            reward -= 2

        # Normalize reward
        reward = max(0, min(1, reward / 5))

        self.time_step += 1
        done = self.time_step >= 3

        return {
            "state": self.state(),
            "reward": reward,
            "done": done
        }

    def state(self):
        return {
            "citizens": self.citizens,
            "budget": self.budget,
            "step": self.time_step,
            "task": self.task
        }