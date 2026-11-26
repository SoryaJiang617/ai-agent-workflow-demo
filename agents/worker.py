from services.openai_client import ask_gpt


def execute_task(task: str, user_input: str, previous_output: str = "") -> str:
    prompt = (
        "Carry out the current step toward the user's requested deliverable. "
        "Preserve the supplied facts and constraints. Build on any previous work. "
        "Return the result of this step."
    )
    context = f"Original request:\n{user_input}\n\nCurrent step:\n{task}"
    if previous_output:
        context += f"\n\nPrevious step's result:\n{previous_output}"
    return ask_gpt(prompt, context)
