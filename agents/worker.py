from services.openai_client import ask_gpt

def execute_task(task, context):
    """
    Worker Agent:
    Executes individual task using LLM.
    """

    system_prompt = "You are an AI operations assistant executing a task."

    user_prompt = f"""
    Task: {task}

    Context:
    {context}

    Produce the best possible output.
    """

    return ask_gpt(system_prompt, user_prompt)