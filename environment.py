import random

TASK_CONFIG = {
    "easy": {
        "budget": 100000,
        "citizen_count": 6,
        "income_range": (3000, 60000),
        "health_range": (1, 10),
        "fraud_range": (0.0, 1.0),
        "cost_per_allocation": 5000,
        "fraud_threshold": 0.6,
        "income_threshold": 20000,
        "noise": False,
    },
    "medium": {
        "budget": 60000,
        "citizen_count": 8,
        "income_range": (10000, 50000),
        "health_range": (3, 9),
        "fraud_range": (0.3, 0.8),
        "cost_per_allocation": 7000,
        "fraud_threshold": 0.65,
        "income_threshold": 25000,
        "noise": True,
    },
    "hard": {
        "budget": 35000,
        "citizen_count": 10,
        "income_range": (15000, 45000),
        "health_range": (4, 8),
        "fraud_range": (0.4, 0.75),
        "cost_per_allocation": 9000,
        "fraud_threshold": 0.7,
        "income_threshold": 28000,
        "noise": True,
    },
}


class GovEnv:
    """
    Multi-step government policy simulation environment.

    Episode structure (3 steps):
      Step 0 — Welfare Allocation: choose which citizens to fund
      Step 1 — Fraud Audit: choose which citizens to investigate
      Step 2 — Reallocation: based on audit, choose final beneficiaries

    Scoring:
      Each correct action adds +1 reward, each incorrect action -0.5.
      Budget overrun applies a penalty scaled to severity.
      Final score = total_reward / max_possible_reward, clamped [0, 1].
    """

    def __init__(self):
        self.cfg = TASK_CONFIG["easy"]
        self.task = "easy"
        self.budget = self.cfg["budget"]
        self.time_step = 0
        self.citizens = []
        self.audit_results = {}

    def reset(self, task: str = "easy") -> dict:
        if task not in TASK_CONFIG:
            raise ValueError(f"Unknown task '{task}'. Choose: easy, medium, hard.")

        self.task = task
        self.cfg = TASK_CONFIG[task]
        self.time_step = 0
        self.budget = self.cfg["budget"]
        self.audit_results = {}

        rng_income = self.cfg["income_range"]
        rng_health = self.cfg["health_range"]
        rng_fraud = self.cfg["fraud_range"]
        noise = self.cfg["noise"]

        self.citizens = []
        for i in range(self.cfg["citizen_count"]):
            real_fraud = round(random.uniform(*rng_fraud), 2)
            # In medium/hard, reported fraud score has noise (to make it harder)
            reported_fraud = (
                round(min(1.0, max(0.0, real_fraud + random.uniform(-0.2, 0.2))), 2)
                if noise
                else real_fraud
            )
            self.citizens.append({
                "id": i,
                "income": random.randint(*rng_income),
                "health_risk": random.randint(*rng_health),
                "fraud_risk": reported_fraud,       # what the AI sees
                "_real_fraud": real_fraud,          # ground truth (hidden from prompt)
            })

        return self._public_state()

    def step(self, action: dict) -> dict:
        cfg = self.cfg
        reward = 0.0
        info = {}

        if self.time_step == 0:
            # --- Welfare Allocation ---
            allocated = action.get("allocate", [])
            cost = len(allocated) * cfg["cost_per_allocation"]
            self.budget -= cost

            correct, wrong = 0, 0
            for c in self.citizens:
                if c["id"] in allocated:
                    if c["income"] < cfg["income_threshold"]:
                        reward += 1
                        correct += 1
                    else:
                        reward -= 0.5
                        wrong += 1

            if self.budget < 0:
                overage_penalty = abs(self.budget) / cfg["budget"]
                reward -= overage_penalty * 3

            info = {"allocated": allocated, "budget_remaining": self.budget,
                    "correct": correct, "wrong": wrong}

        elif self.time_step == 1:
            # --- Fraud Audit ---
            investigated = action.get("investigate", [])
            correct, wrong = 0, 0
            self.audit_results = {}

            for c in self.citizens:
                if c["id"] in investigated:
                    if c["_real_fraud"] > cfg["fraud_threshold"]:
                        reward += 1
                        self.audit_results[c["id"]] = "fraudulent"
                        correct += 1
                    else:
                        reward -= 0.5
                        self.audit_results[c["id"]] = "clean"
                        wrong += 1

            info = {"investigated": investigated, "audit_results": self.audit_results,
                    "correct": correct, "wrong": wrong}

        elif self.time_step == 2:
            # --- Final Reallocation ---
            reallocated = action.get("reallocate", [])
            correct, wrong = 0, 0

            for c in self.citizens:
                if c["id"] in reallocated:
                    is_needy = c["income"] < cfg["income_threshold"]
                    is_clean = self.audit_results.get(c["id"], "unknown") != "fraudulent"
                    if is_needy and is_clean:
                        reward += 1
                        correct += 1
                    else:
                        reward -= 0.5
                        wrong += 1

            info = {"reallocated": reallocated, "correct": correct, "wrong": wrong}

        # Normalize reward to [0, 1]
        max_possible = self.cfg["citizen_count"]
        normalized = max(0.01, min(0.99, reward / max_possible))

        self.time_step += 1
        done = self.time_step >= 3

        return {
            "state": self._public_state(),
            "reward": round(normalized, 4),
            "done": done,
            "info": info,
        }

    def _public_state(self) -> dict:
        """Return state with real_fraud hidden — only reported fraud_risk exposed."""
        public_citizens = [
            {k: v for k, v in c.items() if not k.startswith("_")}
            for c in self.citizens
        ]
        return {
            "citizens": public_citizens,
            "budget": self.budget,
            "step": self.time_step,
            "task": self.task,
            "audit_results": self.audit_results,
            "config": {
                "income_threshold": self.cfg["income_threshold"],
                "fraud_threshold": self.cfg["fraud_threshold"],
                "cost_per_allocation": self.cfg["cost_per_allocation"],
            },
        }
