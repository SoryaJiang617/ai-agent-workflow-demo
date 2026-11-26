from services.openai_client import ask_gpt


def review_output(user_input: str, result: str) -> str:
    prompt = (
        "Review the draft against the original request. Correct missing facts, "
        "unsupported claims, tone, language and format. Check every explicit "
        "length constraint using the requested unit. For a word limit on the "
        "whole answer, count headings and sign-offs too. Revise to fit before "
        "returning only the finished deliverable."
    )
    context = (
        f"Original request:\n{user_input}\n\nDraft:\n{result}\n\n"
        f"Draft length (whitespace-separated words): {len(result.split())}"
    )
    return ask_gpt(prompt, context)
