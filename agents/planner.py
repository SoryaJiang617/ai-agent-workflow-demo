import json

from services.openai_client import ask_gpt


def plan_task(user_input: str) -> list:
    prompt = (
        "Plan the requested deliverable using the fewest useful writing steps. "
        "Use one step for a straightforward draft. Use up to three only when "
        "a later step needs the earlier result. The last step must produce the "
        "requested deliverable. A separate reviewer will check it afterwards. "
        "Return only a JSON array of actionable, nonempty strings in execution order."
    )
    raw_plan = ask_gpt(prompt, user_input)
    try:
        steps = json.loads(raw_plan)
    except json.JSONDecodeError as exc:
        raise ValueError("The planner returned invalid JSON.") from exc
    if not isinstance(steps, list) or not 1 <= len(steps) <= 3:
        raise ValueError("Expected a plan with one to three steps.")
    if any(not isinstance(step, str) or not step.strip() for step in steps):
        raise ValueError("Each planned step must contain text.")
    return [step.strip() for step in steps]
