"""
Replicate API client for Simple Balance Music.
Handles MusicGen generation and Demucs stem separation.
"""

import time

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import replicate as replicate_lib
    HAS_REPLICATE = True
except ImportError:
    replicate_lib = None
    HAS_REPLICATE = False


def _get_token() -> str:
    """Get Replicate API token from Streamlit secrets."""
    if st is not None:
        return st.secrets.get("REPLICATE_API_TOKEN", "")
    return ""


def _is_connected() -> bool:
    """Check if Replicate API is configured."""
    return HAS_REPLICATE and bool(_get_token())


def generate_music(
    prompt: str,
    duration: int = 30,
    model: str = "meta/musicgen:large",
    temperature: float = 1.0,
    top_k: int = 250,
    top_p: float = 0.0,
    classifier_free_guidance: int = 3,
) -> dict:
    """
    Generate music using MusicGen on Replicate.

    Args:
        prompt: Text description of the music to generate
        duration: Length in seconds (max 30 for large model)
        model: Replicate model identifier
        temperature: Sampling temperature
        top_k: Top-k sampling
        top_p: Nucleus sampling (0 = disabled)
        classifier_free_guidance: CFG scale (higher = more prompt adherence)

    Returns:
        dict with keys: url (str), duration (int), model (str), status (str)
        On failure or mock mode: status="mock" with placeholder data
    """
    if not _is_connected():
        return _mock_generate(prompt, duration)

    try:
        client = replicate_lib.Client(api_token=_get_token())

        output = client.run(
            model,
            input={
                "prompt": prompt,
                "duration": min(duration, 30),
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "classifier_free_guidance": classifier_free_guidance,
                "output_format": "wav",
                "normalization_strategy": "peak",
            },
        )

        audio_url = str(output) if not isinstance(output, list) else str(output[0])

        return {
            "url": audio_url,
            "duration": duration,
            "model": model,
            "prompt": prompt,
            "status": "complete",
        }

    except Exception as e:
        return {
            "url": None,
            "duration": duration,
            "model": model,
            "prompt": prompt,
            "status": "error",
            "error": str(e),
        }


def separate_stems(
    audio_url: str,
    model: str = "cjwbw/demucs:latest",
    stems: int = 4,
) -> dict:
    """
    Separate audio into stems using Demucs on Replicate.

    Args:
        audio_url: URL of the audio file to separate
        model: Replicate model identifier for Demucs
        stems: Number of stems (2 or 4)

    Returns:
        dict with keys: vocals, drums, bass, other (each a URL string)
        On failure or mock mode: status="mock" with None URLs
    """
    if not _is_connected():
        return _mock_separate()

    try:
        client = replicate_lib.Client(api_token=_get_token())

        output = client.run(
            model,
            input={
                "audio": audio_url,
                "stems": stems,
            },
        )

        if isinstance(output, dict):
            return {
                "vocals": str(output.get("vocals", "")),
                "drums": str(output.get("drums", "")),
                "bass": str(output.get("bass", "")),
                "other": str(output.get("other", "")),
                "status": "complete",
            }
        else:
            return {
                "vocals": str(output[0]) if len(output) > 0 else None,
                "drums": str(output[1]) if len(output) > 1 else None,
                "bass": str(output[2]) if len(output) > 2 else None,
                "other": str(output[3]) if len(output) > 3 else None,
                "status": "complete",
            }

    except Exception as e:
        return {
            "vocals": None,
            "drums": None,
            "bass": None,
            "other": None,
            "status": "error",
            "error": str(e),
        }


def run_async(model: str, input_data: dict, poll_interval: float = 2.0, timeout: float = 300.0) -> dict:
    """
    Run a Replicate prediction with polling for completion.

    Args:
        model: Replicate model identifier
        input_data: Input parameters dict
        poll_interval: Seconds between status checks
        timeout: Maximum wait time in seconds

    Returns:
        dict with output data and status
    """
    if not _is_connected():
        return {"status": "mock", "output": None}

    try:
        client = replicate_lib.Client(api_token=_get_token())
        prediction = client.predictions.create(
            model=model,
            input=input_data,
        )

        elapsed = 0.0
        while prediction.status not in ("succeeded", "failed", "canceled"):
            if elapsed >= timeout:
                return {"status": "timeout", "output": None, "id": prediction.id}
            time.sleep(poll_interval)
            elapsed += poll_interval
            prediction.reload()

        if prediction.status == "succeeded":
            return {
                "status": "complete",
                "output": prediction.output,
                "id": prediction.id,
                "metrics": prediction.metrics,
            }
        else:
            return {
                "status": prediction.status,
                "output": None,
                "error": prediction.error,
                "id": prediction.id,
            }

    except Exception as e:
        return {"status": "error", "output": None, "error": str(e)}


# --- Mock/Fallback Functions ---

def _mock_generate(prompt: str, duration: int) -> dict:
    """Return mock data when Replicate is not configured."""
    return {
        "url": None,
        "duration": duration,
        "model": "mock",
        "prompt": prompt,
        "status": "mock",
        "message": "Replicate API not configured. Set REPLICATE_API_TOKEN in .streamlit/secrets.toml",
    }


def _mock_separate() -> dict:
    """Return mock stem data when Replicate is not configured."""
    return {
        "vocals": None,
        "drums": None,
        "bass": None,
        "other": None,
        "status": "mock",
        "message": "Replicate API not configured. Set REPLICATE_API_TOKEN in .streamlit/secrets.toml",
    }
