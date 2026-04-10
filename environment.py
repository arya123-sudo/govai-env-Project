import random

class GovEnv:
    def __init__(self):
        self.budget = 100000
        self.time_step = 0
        self.citizens = []

    def reset(self):
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

        for citizen in self.citizens:
            cid = citizen["id"]

            if cid in action.get("allocate", []):
                if citizen["income"] < 15000:
                    reward += 1
                if citizen["fraud_risk"] > 0.7:
                    reward -= 2

        reward = max(0, min(1, reward / 5))

        self.time_step += 1

        done = self.time_step >= 1

        return {
            "state": self.citizens,
            "reward": reward,
            "done": done
        }

    def state(self):
        return {"citizens": self.citizens, "budget": self.budget}