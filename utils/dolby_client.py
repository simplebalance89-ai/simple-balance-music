"""
Dolby.io Media API client for Simple Balance Music.
Handles mastering, enhancement, and audio analysis via Dolby.io.
"""

import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

try:
    import streamlit as st
except ImportError:
    st = None


DOLBY_API_BASE = "https://api.dolby.com/media/"


def _get_api_key() -> str:
    if st is not None:
        return st.secrets.get("DOLBY_API_KEY", "")
    return ""


def _is_connected() -> bool:
    return HAS_REQUESTS and bool(_get_api_key())


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _poll_job(job_id, endpoint, poll_interval=2.0, timeout=300.0):
    elapsed = 0.0
    while elapsed < timeout:
        try:
            resp = requests.get(
                f"{DOLBY_API_BASE}{endpoint}",
                params={"job_id": job_id},
                headers=_headers(),
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "").lower()
                if status == "success":
                    return {"status": "complete", "data": data}
                elif status in ("failed", "error"):
                    return {"status": "error", "error": data.get("error", "Unknown error"), "data": data}
            time.sleep(poll_interval)
            elapsed += poll_interval
        except Exception as e:
            return {"status": "error", "error": str(e)}
    return {"status": "timeout", "error": f"Job timed out after {timeout}s"}


def get_upload_url():
    if not _is_connected():
        return {"status": "mock", "url": None, "dlb_url": None}
    try:
        resp = requests.post(
            f"{DOLBY_API_BASE}input",
            headers=_headers(),
            json={"url": "dlb://input/audio.wav"},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {"status": "complete", "url": data.get("url"), "dlb_url": "dlb://input/audio.wav"}
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def upload_file(upload_url, file_path):
    if not _is_connected():
        return {"status": "mock"}
    try:
        with open(file_path, "rb") as f:
            resp = requests.put(upload_url, data=f, headers={"Content-Type": "application/octet-stream"}, timeout=120)
        if resp.status_code in (200, 201):
            return {"status": "complete"}
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def master_track(input_url, output_url="dlb://output/mastered.wav", profile="music", loudness=None):
    if not _is_connected():
        return _mock_master(input_url)
    try:
        body = {"input": input_url, "output": output_url, "content": {"type": profile}}
        if loudness:
            body["loudness"] = loudness
        resp = requests.post(f"{DOLBY_API_BASE}master", headers=_headers(), json=body, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            job_id = data.get("job_id")
            result = _poll_job(job_id, "master")
            if result["status"] == "complete":
                dl = get_download_url(output_url)
                return {"status": "complete", "job_id": job_id, "output_url": dl.get("url"), "dlb_url": output_url}
            return result
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def enhance_audio(input_url, output_url="dlb://output/enhanced.wav", noise_reduction=True, dynamics=True):
    if not _is_connected():
        return _mock_enhance(input_url)
    try:
        body = {"input": input_url, "output": output_url, "content": {"type": "music"}}
        audio_settings = {}
        if noise_reduction:
            audio_settings["noise"] = {"reduction": {"enable": True, "amount": "auto"}}
        if dynamics:
            audio_settings["dynamics"] = {"range_control": {"enable": True}}
        if audio_settings:
            body["audio"] = audio_settings
        resp = requests.post(f"{DOLBY_API_BASE}enhance", headers=_headers(), json=body, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            job_id = data.get("job_id")
            result = _poll_job(job_id, "enhance")
            if result["status"] == "complete":
                dl = get_download_url(output_url)
                return {"status": "complete", "job_id": job_id, "output_url": dl.get("url"), "dlb_url": output_url}
            return result
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def analyze_media(input_url):
    if not _is_connected():
        return _mock_analyze()
    try:
        resp = requests.post(
            f"{DOLBY_API_BASE}analyze",
            headers=_headers(),
            json={"input": input_url, "content": {"type": "music"}},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            job_id = data.get("job_id")
            result = _poll_job(job_id, "analyze")
            if result["status"] == "complete":
                return {"status": "complete", "job_id": job_id, "analysis": result.get("data", {})}
            return result
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_download_url(dlb_url):
    if not _is_connected():
        return {"status": "mock", "url": None}
    try:
        resp = requests.get(f"{DOLBY_API_BASE}output", params={"url": dlb_url}, headers=_headers(), timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return {"status": "complete", "url": data.get("url")}
        return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _mock_master(input_url):
    return {"status": "mock", "job_id": None, "output_url": None,
            "message": "Dolby.io API not configured. Set DOLBY_API_KEY in .streamlit/secrets.toml"}


def _mock_enhance(input_url):
    return {"status": "mock", "job_id": None, "output_url": None,
            "message": "Dolby.io API not configured. Set DOLBY_API_KEY in .streamlit/secrets.toml"}


def _mock_analyze():
    return {"status": "mock",
            "analysis": {"loudness": {"integrated": -14.0, "range": 8.0, "peak": -1.0},
                         "noise": {"level": "low"}, "clipping": {"detected": False}},
            "message": "Dolby.io API not configured. Using mock analysis data."}
