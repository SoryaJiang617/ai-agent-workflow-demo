from services.openai_client import ask_gpt

def review_output(result):
    """
    Reviewer Agent:
    Validates and improves final output.
    """

    system_prompt = "You are a senior reviewer improving AI-generated work."

    user_prompt = f"""
    Improve clarity, structure, and professionalism:

    {result}
    """

    return ask_gpt(system_prompt, user_prompt)