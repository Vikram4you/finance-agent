import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

load_dotenv()
# Do not send third-party provider conversations to the OpenAI tracing backend.
set_tracing_disabled(True)


def build_model():
    """Build an OpenAI-compatible Agents SDK model for Hugging Face or xAI."""
    provider = os.getenv("LLM_PROVIDER", "huggingface").strip().lower()

    if provider == "grok":
        api_key = os.getenv("XAI_API_KEY")
        model_name = os.getenv("XAI_MODEL", "grok-3-mini")
        base_url = "https://api.x.ai/v1"
    elif provider == "huggingface":
        api_key = os.getenv("HF_TOKEN")
        model_name = os.getenv("HF_MODEL", "openai/gpt-oss-120b:fastest")
        base_url = "https://router.huggingface.co/v1"
    else:
        raise ValueError("LLM_PROVIDER must be 'huggingface' or 'grok'.")

    if not api_key:
        key_name = "XAI_API_KEY" if provider == "grok" else "HF_TOKEN"
        raise ValueError(f"Missing {key_name}. Configure it in your local .env file.")

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=client,
    )
