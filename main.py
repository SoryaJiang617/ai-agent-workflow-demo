from agents.planner import plan_task
from agents.worker import execute_task
from agents.reviewer import review_output
print("PROGRAM STARTED")
def run_agent_workflow(user_input):

    print("\n--- Planning Phase ---")
    tasks = plan_task(user_input)

    context = user_input

    print("\n--- Execution Phase ---")
    for t in tasks:
        print(f"Running task: {t}")
        context = execute_task(t, context)

    print("\n--- Review Phase ---")
    final_output = review_output(context)

    return final_output


if __name__ == "__main__":
    user_input = input("Enter a business request:\n")

    result = run_agent_workflow(user_input)

    print("\n===== FINAL OUTPUT =====\n")
    print(result)