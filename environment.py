import random

class GovEnv:
    def __init__(self):
        random.seed(42)
        self.history = []

    def reset(self, task="easy"):
        self.task = task
        self.time_step = 0
        self.done = False

        self.budget = {"easy": 100000, "medium": 70000, "hard": 50000}[task]
        if task == "hard":
            self.budget -= 10000  # make it harder
        self.citizens = self.generate_citizens(task)
        self.history = []

        return self.state()

    def generate_citizens(self, task):
        n = {"easy": 5, "medium": 10, "hard": 20}[task]

        citizens = []
        for i in range(n):
            citizens.append({
                "id": i,
                "income": random.randint(5000, 50000),
                "family_size": random.randint(1, 6),
                "health_risk": random.randint(1, 10),
                "region": random.choice(["rural", "urban"]),
                "fraud_risk": round(random.random(), 2)
            })
        return citizens

    def step(self, action):
        if self.done:
            return self.state(), 0, True, {}

        reward = 0
        citizen = next((c for c in self.citizens if c["id"] == action["citizen_id"]), None)

        if not citizen:
            return self.state(), -1, self.done, {}

        scheme_cost = {"health":20000,"food":10000,"education":15000,"reject":0}
        cost = scheme_cost.get(action["scheme"], 0)

        if cost > self.budget:
            reward -= 5
        else:
            self.budget -= cost

            if citizen["income"] < 20000:
                reward += 3
            else:
                reward -= 1

            if citizen["health_risk"] > 7 and action["scheme"] == "health":
                reward += 3

            if citizen["fraud_risk"] > 0.7:
                reward -= 4

            if citizen["income"] < 15000:
                reward += 5

            if citizen["fraud_risk"] > 0.7 and action["scheme"] != "reject":
                reward -= 6

            if action["scheme"] == "reject" and citizen["fraud_risk"] > 0.7:
                reward += 3

        self.history.append((citizen, action, reward))

        self.time_step += 1
        if self.time_step >= len(self.citizens):
            self.done = True

        return self.state(), reward, self.done, {}

    def state(self):
        return {
            "citizens": self.citizens,
            "remaining_budget": self.budget,
            "time_step": self.time_step
        }
