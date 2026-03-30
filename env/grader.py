def grade(history):
    if not history:
        return 0.0
    positive = sum(1 for _, _, r in history if r > 0)
    return max(0.0, min(positive/len(history), 1.0))
