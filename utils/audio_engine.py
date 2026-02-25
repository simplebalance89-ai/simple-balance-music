"""
Local audio processing engine for Simple Balance Music.
Uses Spotify Pedalboard for DSP and librosa for analysis.
"""

import os
import tempfile

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    sf = None
    HAS_SOUNDFILE = False

try:
    from pedalboard import (
        Pedalboard, Compressor, Gain, Limiter,
        LowShelfFilter, HighShelfFilter, HighpassFilter,
        LowpassFilter, Reverb, Chorus,
    )
    from pedalboard.io import AudioFile
    HAS_PEDALBOARD = True
except ImportError:
    HAS_PEDALBOARD = False

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    librosa = None
    HAS_LIBROSA = False


def _check_deps(*required):
    """Check that required dependencies are available."""
    missing = []
    dep_map = {"pedalboard": HAS_PEDALBOARD, "librosa": HAS_LIBROSA, "soundfile": HAS_SOUNDFILE, "numpy": HAS_NUMPY}
    for dep in required:
        if not dep_map.get(dep, False):
            missing.append(dep)
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}"
    return True, ""


def _load_audio(audio_path):
    """Load audio file, return (array, sample_rate)."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        ok2, _ = _check_deps("soundfile", "numpy")
        if not ok2:
            raise ImportError(msg)
        audio, sr = sf.read(audio_path)
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        else:
            audio = audio.T
        return audio.astype(np.float32), sr
    with AudioFile(audio_path) as f:
        audio = f.read(f.frames)
        sr = f.samplerate
    return audio, sr


def _save_audio(audio, sr, output_path):
    """Save audio array to file."""
    ok, _ = _check_deps("pedalboard")
    if ok:
        with AudioFile(output_path, "w", samplerate=sr, num_channels=audio.shape[0]) as f:
            f.write(audio)
    else:
        sf.write(output_path, audio.T, sr)
    return output_path


def _default_output(audio_path, suffix):
    """Generate default output path."""
    base, ext = os.path.splitext(audio_path)
    return f"{base}_{suffix}{ext or '.wav'}"


def apply_sidechain(audio_path, kick_path, threshold=-20.0, ratio=4.0, attack_ms=5.0, release_ms=100.0, output_path=None):
    """Apply sidechain compression triggered by a kick drum track."""
    ok, msg = _check_deps("pedalboard", "numpy")
    if not ok:
        raise ImportError(msg)
    audio, sr = _load_audio(audio_path)
    kick, kick_sr = _load_audio(kick_path)
    if kick_sr != sr and HAS_LIBROSA:
        kick_mono = librosa.resample(kick[0] if kick.ndim > 1 else kick, orig_sr=kick_sr, target_sr=sr)
        kick = kick_mono.reshape(1, -1)
    kick_mono = np.mean(kick, axis=0) if kick.ndim > 1 and kick.shape[0] > 1 else kick.flatten()
    audio_len = audio.shape[-1]
    if len(kick_mono) < audio_len:
        kick_mono = np.pad(kick_mono, (0, audio_len - len(kick_mono)))
    else:
        kick_mono = kick_mono[:audio_len]
    envelope = np.abs(kick_mono)
    attack_samples = max(1, int(sr * attack_ms / 1000.0))
    release_samples = max(1, int(sr * release_ms / 1000.0))
    smoothed = np.zeros_like(envelope)
    for i in range(1, len(envelope)):
        if envelope[i] > smoothed[i - 1]:
            coeff = 1.0 - np.exp(-1.0 / attack_samples)
        else:
            coeff = 1.0 - np.exp(-1.0 / release_samples)
        smoothed[i] = smoothed[i - 1] + coeff * (envelope[i] - smoothed[i - 1])
    threshold_lin = 10 ** (threshold / 20.0)
    gain_reduction = np.ones_like(smoothed)
    above = smoothed > threshold_lin
    if np.any(above):
        gain_reduction[above] = (threshold_lin / smoothed[above]) ** (1.0 - 1.0 / ratio)
    for ch in range(audio.shape[0]):
        audio[ch] *= gain_reduction
    if output_path is None:
        output_path = _default_output(audio_path, "sidechained")
    return _save_audio(audio, sr, output_path)


def apply_eq(audio_path, low_cut=32.0, high_shelf=12000.0, low_shelf_gain_db=0.0, high_shelf_gain_db=0.0, output_path=None):
    """Apply parametric EQ to audio."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        raise ImportError(msg)
    audio, sr = _load_audio(audio_path)
    plugins = []
    if low_cut > 0:
        plugins.append(HighpassFilter(cutoff_frequency_hz=low_cut))
    if low_shelf_gain_db != 0:
        plugins.append(LowShelfFilter(cutoff_frequency_hz=200.0, gain_db=low_shelf_gain_db))
    if high_shelf_gain_db != 0:
        plugins.append(HighShelfFilter(cutoff_frequency_hz=high_shelf, gain_db=high_shelf_gain_db))
    if plugins:
        board = Pedalboard(plugins)
        audio = board(audio, sr)
    if output_path is None:
        output_path = _default_output(audio_path, "eq")
    return _save_audio(audio, sr, output_path)


def apply_reverb(audio_path, room_size=0.5, wet=0.3, damping=0.5, width=1.0, output_path=None):
    """Apply reverb to audio."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        raise ImportError(msg)
    audio, sr = _load_audio(audio_path)
    board = Pedalboard([Reverb(room_size=room_size, wet_level=wet, dry_level=1.0 - wet, damping=damping, width=width)])
    audio = board(audio, sr)
    if output_path is None:
        output_path = _default_output(audio_path, "reverb")
    return _save_audio(audio, sr, output_path)


def apply_compression(audio_path, threshold=-20.0, ratio=4.0, attack_ms=5.0, release_ms=50.0, output_path=None):
    """Apply dynamic compression to audio."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        raise ImportError(msg)
    audio, sr = _load_audio(audio_path)
    board = Pedalboard([Compressor(threshold_db=threshold, ratio=ratio, attack_ms=attack_ms, release_ms=release_ms)])
    audio = board(audio, sr)
    if output_path is None:
        output_path = _default_output(audio_path, "compressed")
    return _save_audio(audio, sr, output_path)


def apply_limiter(audio_path, threshold=-1.0, release_ms=100.0, output_path=None):
    """Apply brickwall limiter to audio."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        raise ImportError(msg)
    audio, sr = _load_audio(audio_path)
    board = Pedalboard([Limiter(threshold_db=threshold, release_ms=release_ms)])
    audio = board(audio, sr)
    if output_path is None:
        output_path = _default_output(audio_path, "limited")
    return _save_audio(audio, sr, output_path)


def master_chain(audio_path, preset="mau5trap", output_path=None):
    """Apply full mastering chain: EQ -> Compression -> Gain -> Limiter."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        raise ImportError(msg)
    from utils.mau5trap_presets import MASTERING_PRESETS
    params = MASTERING_PRESETS.get(preset, MASTERING_PRESETS["mau5trap"])
    audio, sr = _load_audio(audio_path)
    plugins = []
    eq = params.get("eq", {})
    if eq.get("high_pass", 0) > 0:
        plugins.append(HighpassFilter(cutoff_frequency_hz=eq["high_pass"]))
    if eq.get("low_shelf_gain", 0) != 0:
        plugins.append(LowShelfFilter(cutoff_frequency_hz=eq.get("low_shelf_freq", 200), gain_db=eq["low_shelf_gain"]))
    if eq.get("high_shelf_gain", 0) != 0:
        plugins.append(HighShelfFilter(cutoff_frequency_hz=eq.get("high_shelf_freq", 12000), gain_db=eq["high_shelf_gain"]))
    comp = params.get("compression", {})
    if comp:
        plugins.append(Compressor(threshold_db=comp.get("threshold", -18), ratio=comp.get("ratio", 3.0), attack_ms=comp.get("attack_ms", 10), release_ms=comp.get("release_ms", 100)))
    gain_db = params.get("makeup_gain_db", 0)
    if gain_db != 0:
        plugins.append(Gain(gain_db=gain_db))
    limiter = params.get("limiter", {})
    plugins.append(Limiter(threshold_db=limiter.get("threshold", -1.0), release_ms=limiter.get("release_ms", 100)))
    board = Pedalboard(plugins)
    audio = board(audio, sr)
    if output_path is None:
        output_path = _default_output(audio_path, f"mastered_{preset}")
    return _save_audio(audio, sr, output_path)


def analyze_audio(audio_path):
    """Analyze audio file and return BPM, key, loudness, peak, duration."""
    ok, msg = _check_deps("librosa", "numpy")
    if not ok:
        return _mock_analysis(msg)
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        duration = librosa.get_duration(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo) if not hasattr(tempo, "__len__") else float(tempo[0])
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = chroma.mean(axis=1)
        pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key_idx = int(np.argmax(chroma_mean))
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        major_corr = np.corrcoef(np.roll(chroma_mean, -key_idx), major_profile)[0, 1]
        minor_corr = np.corrcoef(np.roll(chroma_mean, -key_idx), minor_profile)[0, 1]
        key_name = f"{pitch_classes[key_idx]}m" if minor_corr > major_corr else pitch_classes[key_idx]
        rms = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms))
        loudness_lufs = 20 * np.log10(rms_mean + 1e-10) - 0.691
        peak_db = float(20 * np.log10(np.max(np.abs(y)) + 1e-10))
        return {"bpm": round(bpm, 1), "key": key_name, "loudness_lufs": round(loudness_lufs, 1), "peak_db": round(peak_db, 1), "duration_sec": round(duration, 2), "sample_rate": sr, "status": "complete"}
    except Exception as e:
        return _mock_analysis(str(e))


def _mock_analysis(reason=""):
    """Return mock analysis when deps are missing."""
    return {"bpm": 128.0, "key": "Am", "loudness_lufs": -10.5, "peak_db": -0.3, "duration_sec": 0.0, "sample_rate": 44100, "status": "mock", "message": f"Audio analysis unavailable. {reason}".strip()}


# ===== MISSING FUNCTIONS (9) — required by tabs =====


def is_available():
    """Check if audio processing dependencies are available."""
    return HAS_PEDALBOARD or (HAS_SOUNDFILE and HAS_NUMPY)


def apply_master_chain(audio_path, preset="mau5trap", output_path=None):
    """Alias for master_chain — used by tab_mastering."""
    return master_chain(audio_path, preset=preset, output_path=output_path)


def apply_effect(audio_path, effect_name, output_path=None, **params):
    """Apply a single named effect to audio. Used by tab_mastering individual effects."""
    ok, msg = _check_deps("pedalboard")
    if not ok:
        raise ImportError(msg)
    audio, sr = _load_audio(audio_path)
    effect_map = {
        "compressor": lambda: Compressor(
            threshold_db=params.get("threshold", -20),
            ratio=params.get("ratio", 4.0),
            attack_ms=params.get("attack_ms", 5.0),
            release_ms=params.get("release_ms", 50.0),
        ),
        "reverb": lambda: Reverb(
            room_size=params.get("room_size", 0.5),
            wet_level=params.get("wet", 0.3),
            dry_level=1.0 - params.get("wet", 0.3),
            damping=params.get("damping", 0.5),
            width=params.get("width", 1.0),
        ),
        "chorus": lambda: Chorus(
            rate_hz=params.get("rate", 1.0),
            depth=params.get("depth", 0.25),
            mix=params.get("mix", 0.5),
        ),
        "highpass": lambda: HighpassFilter(cutoff_frequency_hz=params.get("cutoff", 80.0)),
        "lowpass": lambda: LowpassFilter(cutoff_frequency_hz=params.get("cutoff", 12000.0)),
        "limiter": lambda: Limiter(
            threshold_db=params.get("threshold", -1.0),
            release_ms=params.get("release_ms", 100.0),
        ),
        "gain": lambda: Gain(gain_db=params.get("gain_db", 0.0)),
    }
    builder = effect_map.get(effect_name.lower())
    if builder is None:
        raise ValueError(f"Unknown effect: {effect_name}. Available: {list(effect_map.keys())}")
    board = Pedalboard([builder()])
    audio = board(audio, sr)
    if output_path is None:
        output_path = _default_output(audio_path, effect_name)
    return _save_audio(audio, sr, output_path)


def get_waveform_data(audio_path, max_points=2000):
    """Return downsampled waveform data for Plotly visualization."""
    ok, msg = _check_deps("librosa", "numpy")
    if not ok:
        return {"x": [], "y": [], "status": "unavailable", "message": msg}
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        duration = len(y) / sr
        if len(y) > max_points:
            step = len(y) // max_points
            y_down = y[::step][:max_points]
        else:
            y_down = y
        x = np.linspace(0, duration, len(y_down))
        return {"x": x.tolist(), "y": y_down.tolist(), "duration": duration, "sample_rate": sr, "status": "complete"}
    except Exception as e:
        return {"x": [], "y": [], "status": "error", "message": str(e)}


def get_frequency_spectrum(audio_path, n_fft=2048):
    """Return frequency spectrum data for Plotly visualization."""
    ok, msg = _check_deps("librosa", "numpy")
    if not ok:
        return {"frequencies": [], "magnitudes": [], "status": "unavailable", "message": msg}
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        S = np.abs(librosa.stft(y, n_fft=n_fft))
        S_mean = S.mean(axis=1)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        S_db = 20 * np.log10(S_mean + 1e-10)
        return {"frequencies": freqs.tolist(), "magnitudes": S_db.tolist(), "status": "complete"}
    except Exception as e:
        return {"frequencies": [], "magnitudes": [], "status": "error", "message": str(e)}


def get_spectrogram_data(audio_path, n_fft=2048, hop_length=512):
    """Return spectrogram data for Plotly heatmap visualization."""
    ok, msg = _check_deps("librosa", "numpy")
    if not ok:
        return {"times": [], "frequencies": [], "spectrogram": [], "status": "unavailable", "message": msg}
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
        S_db = librosa.amplitude_to_db(S, ref=np.max)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=hop_length)
        max_freq_idx = np.searchsorted(freqs, 8000)
        return {
            "times": times.tolist(),
            "frequencies": freqs[:max_freq_idx].tolist(),
            "spectrogram": S_db[:max_freq_idx].tolist(),
            "status": "complete",
        }
    except Exception as e:
        return {"times": [], "frequencies": [], "spectrogram": [], "status": "error", "message": str(e)}


# ===== CAMELOT WHEEL =====

CAMELOT_WHEEL = {
    "C": "8B", "Am": "8A", "G": "9B", "Em": "9A",
    "D": "10B", "Bm": "10A", "A": "11B", "F#m": "11A",
    "E": "12B", "C#m": "12A", "B": "1B", "G#m": "1A",
    "F#": "2B", "D#m": "2A", "Gb": "2B", "Ebm": "2A",
    "Db": "3B", "Bbm": "3A", "C#": "3B",
    "Ab": "4B", "Fm": "4A", "G#": "4B",
    "Eb": "5B", "Cm": "5A", "D#": "5B",
    "Bb": "6B", "Gm": "6A", "A#": "6B",
    "F": "7B", "Dm": "7A",
}


def key_to_camelot(key):
    """Convert a musical key to Camelot notation."""
    if not key:
        return "?"
    return CAMELOT_WHEEL.get(key, "?")


def are_keys_compatible(key1, key2):
    """Check if two keys are harmonically compatible (adjacent on Camelot wheel)."""
    c1 = key_to_camelot(key1)
    c2 = key_to_camelot(key2)
    if c1 == "?" or c2 == "?":
        return False
    num1, letter1 = int(c1[:-1]), c1[-1]
    num2, letter2 = int(c2[:-1]), c2[-1]
    if num1 == num2 and letter1 == letter2:
        return True
    if num1 == num2 and letter1 != letter2:
        return True
    if letter1 == letter2 and abs(num1 - num2) == 1:
        return True
    if letter1 == letter2 and sorted([num1, num2]) == [1, 12]:
        return True
    return False


def get_compatible_camelot(key):
    """Return list of compatible Camelot keys for a given key."""
    camelot = key_to_camelot(key)
    if camelot == "?":
        return []
    num, letter = int(camelot[:-1]), camelot[-1]
    compatible = []
    compatible.append(f"{num}{letter}")
    other = "A" if letter == "B" else "B"
    compatible.append(f"{num}{other}")
    up = num + 1 if num < 12 else 1
    down = num - 1 if num > 1 else 12
    compatible.append(f"{up}{letter}")
    compatible.append(f"{down}{letter}")
    return compatible
