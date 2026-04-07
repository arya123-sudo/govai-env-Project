from environment import GovEnv

def main():
    env = GovEnv()
    state = env.reset()

    print("Environment reset successful")
    print(state)

if __name__ == "__main__":
    main()
