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
                "family_size": random.randint(1, 6),
                "health_risk": random.randint(1, 10),
                "fraud_risk": round(random.uniform(0, 1), 2)
            }
            for i in range(5)
        ]

        return {"citizens": self.citizens, "budget": self.budget}

    def step(self, action):
        reward = 0
        cost_per_person = 5000

        allocated = action.get("allocate", [])
        spent = len(allocated) * cost_per_person
        self.budget -= spent

        # ❌ penalty if overspending
        if self.budget < 0:
            reward -= 2

        for citizen in self.citizens:
            cid = citizen["id"]

            if cid in allocated:

                # EASY
                if self.task == "easy":
                    if citizen["income"] < 20000:
                        reward += 1

                # MEDIUM
                elif self.task == "medium":
                    if citizen["income"] < 20000 and citizen["health_risk"] > 5:
                        reward += 1

                # HARD
                elif self.task == "hard":
                    if citizen["income"] < 20000 and citizen["fraud_risk"] < 0.5:
                        reward += 1
                    else:
                        reward -= 1

        # 🎯 fairness bonus
        low_income_supported = sum(
            1 for c in self.citizens
            if c["income"] < 15000 and c["id"] in allocated
        )
        reward += low_income_supported * 0.2

        reward = max(0, min(1, reward / 5))

        self.time_step += 1
        done = self.time_step >= 1

        return {
            "state": self.citizens,
            "reward": reward,
            "done": done,
            "budget": self.budget
        }

    def state(self):
        return {"citizens": self.citizens, "budget": self.budget}