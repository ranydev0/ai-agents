from agent import agent


def main():
    print("Alfred is at your service, Sir.\n")

    while True:
        task = input("You: ").strip()
        if not task:
            continue
        if task.lower() in ("exit", "quit", "goodbye"):
            print("Alfred: Very good, Sir. Goodnight.")
            break
        response = agent.run(task)
        print(f"\nAlfred: {response}\n")


if __name__ == "__main__":
    main()
