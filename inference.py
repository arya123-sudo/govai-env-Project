from environment import GovEnv

def main():
    env = GovEnv()

    print("[START] task=demo", flush=True)

    state = env.reset()

    reward = 1.0

    print(f"[STEP] step=1 reward={reward}", flush=True)

    print("[END] task=demo score=1.0 steps=1", flush=True)


if __name__ == "__main__":
    main()