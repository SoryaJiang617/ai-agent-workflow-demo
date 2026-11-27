import json
import re
from typing import Optional

from services.openai_client import ask_gpt


# Apply email formatting to writing requests, not to analyses of existing emails.
_EMAIL_REQUEST = re.compile(
    r"\b(?:write|draft|compose|prepare|rewrite|revise)\s+"
    r"(?:(?!(?:of|about|on|for|from|to)\b)[\w-]+\s+)*e-?mail\b", re.I
)
_WORD_LIMIT = re.compile(
    r"\b(under|fewer than|less than|at most|no more than)\s+(\d+)\s+words?\b", re.I
)
_EDITORIAL_TEXT = re.compile(
    r"^\s*(?:\*{0,2}(?:subject|(?:original|revised|final) (?:draft|email)|draft|"
    r"(?:editor.?s? )?notes?)\s*:"
    r"|please (?:ensure (?:to |you )?)?fill in the placeholders)"
    r"|\bword count\s*[:=]\s*\d+|\bthis email is \d+ words\b", re.I | re.M
)


def _render_email(reply: str, max_words: Optional[int]) -> str:
    try:
        fields = json.loads(reply)
    except json.JSONDecodeError as exc:
        raise ValueError("Return a single JSON object containing the final email.") from exc

    if not isinstance(fields, dict) or fields.keys() != {"subject", "body"}:
        raise ValueError("Return exactly the subject and body of one email.")
    if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
        raise ValueError("Both the subject and body must contain text.")

    subject, body = fields["subject"].strip(), fields["body"].strip()
    if len(subject.splitlines()) != 1 or _EDITORIAL_TEXT.search(subject + "\n" + body):
        raise ValueError("Remove extra drafts, headers, editor notes and word counts.")
    email = f"Subject: {subject}\n\n{body}"
    count = len(email.split())
    if max_words is not None and count > max_words:
        raise ValueError(f"The complete email has {count} words. The maximum is {max_words}.")
    return email


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
    if not _EMAIL_REQUEST.search(user_input):
        return ask_gpt(prompt, context)

    prompt += (
        ' Return one JSON object with exactly two strings: "subject" (one line, '
        'without the Subject: prefix) and "body" (from greeting through sign-off). '
        "Write only what the recipient should read. Omit earlier drafts, editorial "
        "instructions, word counts and Markdown fences. Use only supplied facts."
    )
    max_words = None
    match = _WORD_LIMIT.search(user_input)
    if match:
        max_words = int(match[2])
        if match[1].lower() in ("under", "fewer than", "less than"):
            max_words -= 1
        context += f"\nMaximum {max_words} whitespace-separated words including the Subject: label."

    reply = ask_gpt(prompt, context)
    try:
        return _render_email(reply, max_words)
    except ValueError as exc:
        context += f"\nYour last response failed validation: {exc} Rewrite the final email."
    return _render_email(ask_gpt(prompt, context), max_words)
