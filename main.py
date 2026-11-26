import sys

from agents.planner import plan_task
from agents.reviewer import review_output
from agents.worker import execute_task


def run_agent_workflow(user_input: str) -> str:
    if not user_input.strip():
        raise ValueError("Enter a business request before starting.")

    stage = "Planning"
    try:
        print("\n--- Planning ---")
        steps = plan_task(user_input)
        for number, step in enumerate(steps, start=1):
            print(f"{number}. {step}")

        print("\n--- Execution ---")
        draft = ""
        for number, step in enumerate(steps, start=1):
            stage = f"Execution step {number}"
            print(f"Running step {number} of {len(steps)}...")
            draft = execute_task(step, user_input, draft)

        stage = "Review"
        print("\n--- Review ---")
        return review_output(user_input, draft)
    except (ValueError, RuntimeError) as exc:
        raise RuntimeError(f"{stage} failed: {exc}") from exc


def main() -> int:
    try:
        request = input("Enter a business request:\n")
        result = run_agent_workflow(request)
    except EOFError:
        print("No request received.", file=sys.stderr)
        return 1
    except (ValueError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print("\n===== FINAL OUTPUT =====\n")
    print(result)
    print(f"\nWord count (whitespace-separated): {len(result.split())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
