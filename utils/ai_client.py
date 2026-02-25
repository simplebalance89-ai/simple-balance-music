"""Azure OpenAI client wrapper for Simple Balance Music."""

import streamlit as st
from openai import AzureOpenAI
import time
from utils.secrets_helper import get_secret


def get_client():
    """Get configured Azure OpenAI client."""
    return AzureOpenAI(
        azure_endpoint=get_secret("AZURE_OPENAI_ENDPOINT"),
        api_key=get_secret("AZURE_OPENAI_KEY"),
        api_version="2024-12-01-preview",
    )


def chat(system_prompt: str, messages: list, temperature: float = 0.3) -> str:
    """Send chat completion and return response text."""
    client = get_client()
    model = get_secret("AZURE_OPENAI_MODEL", "gpt-4o")

    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    t0 = time.time()
    response = client.chat.completions.create(
        model=model, messages=api_messages, temperature=temperature
    )
    elapsed = time.time() - t0

    # Track usage
    if "stats" in st.session_state:
        usage = response.usage
        s = st.session_state.stats
        s["total_queries"] += 1
        s["total_tokens_in"] += usage.prompt_tokens
        s["total_tokens_out"] += usage.completion_tokens

    return response.choices[0].message.content
