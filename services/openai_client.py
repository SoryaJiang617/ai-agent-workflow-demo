import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _get_client():
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in .env or in your environment.")
    return OpenAI(api_key=api_key, timeout=20.0, max_retries=0)


def ask_gpt(system_prompt: str, user_prompt: str) -> str:
    try:
        import openai

        client = _get_client()
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Install the project dependencies with python -m pip install -r requirements.txt."
        ) from exc

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
    except openai.AuthenticationError as exc:
        raise RuntimeError("OpenAI rejected the API key. Check OPENAI_API_KEY.") from exc
    except openai.RateLimitError as exc:
        raise RuntimeError("OpenAI rate limit reached. Check your quota or try later.") from exc
    except openai.APITimeoutError as exc:
        raise RuntimeError("OpenAI timed out. Try again.") from exc
    except openai.APIConnectionError as exc:
        raise RuntimeError("Could not reach OpenAI. Check your network connection.") from exc
    except openai.APIError as exc:
        raise RuntimeError(
            "OpenAI could not complete the request. Check model access or try again later."
        ) from exc

    content = response.choices[0].message.content if response.choices else None
    if not content or not content.strip():
        raise RuntimeError("OpenAI returned an empty response. Try again.")
    return content.strip()
