"""Tab 3: AI Mastering Studio — Dolby.io + Spotify Pedalboard."""

import streamlit as st
import io

try:
    from utils.audio_engine import (
        analyze_audio, apply_master_chain, apply_effect,
        get_waveform_data, get_frequency_spectrum, is_available as audio_available,
    )
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

try:
    from utils.dolby_client import is_available as dolby_available
    HAS_DOLBY = True
except ImportError:
    HAS_DOLBY = False
    dolby_available = lambda: False

try:
    from utils.mau5trap_presets import MASTERING_PRESETS, EQ_PROFILES, SIDECHAIN_PRESETS
    HAS_PRESETS = True
except ImportError:
    HAS_PRESETS = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


MASTER_PRESETS = {
    "club": "Club / PA System — Punchy, loud, clear",
    "streaming": "Streaming (-14 LUFS) — Spotify/Apple optimized",
    "demo": "Demo Master — Balanced for label submission",
    "mau5trap_dark": "mau5trap Dark — Heavy lows, rolled highs",
    "vinyl": "Vinyl — Controlled bass, warm compression",
}


def render():
    st.markdown("### AI Mastering Studio")
    st.caption("Real-time mastering with Spotify Pedalboard. Cloud mastering via Dolby.io.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Upload Track")
        uploaded = st.file_uploader(
            "Drop your track here",
            type=["mp3", "wav", "flac", "aiff", "m4a"],
            key="master_upload",
        )

        if uploaded:
            audio_bytes = uploaded.read()
            st.audio(audio_bytes, format="audio/wav")
            st.success(f"Loaded: **{uploaded.name}** ({len(audio_bytes) / 1024 / 1024:.1f} MB)")

            # Analyze before mastering
            if HAS_AUDIO:
                with st.spinner("Analyzing..."):
                    analysis = analyze_audio(io.BytesIO(audio_bytes))
                if "error" not in analysis:
                    ac1, ac2, ac3, ac4 = st.columns(4)
                    ac1.metric("BPM", analysis.get("bpm", "?"))
                    ac2.metric("Key", analysis.get("key", "?"))
                    ac3.metric("Loudness", f"{analysis.get('rms_db', '?')} dB")
                    ac4.metric("Peak", f"{analysis.get('peak_db', '?')} dB")

            st.markdown("#### Mastering Preset")
            preset = st.selectbox(
                "Preset", list(MASTER_PRESETS.keys()),
                format_func=lambda x: MASTER_PRESETS[x],
                key="master_preset",
            )

            st.markdown("#### Fine-Tune")
            ca, cb = st.columns(2)
            with ca:
                extra_gain = st.slider("Extra Gain (dB)", -6.0, 6.0, 0.0, 0.5, key="master_gain")
            with cb:
                export_format = st.selectbox("Export", ["WAV", "FLAC"], key="master_format")

            if st.button("Master Track", key="master_go", type="primary"):
                if HAS_AUDIO and audio_available():
                    with st.spinner("Mastering with Pedalboard..."):
                        mastered = apply_master_chain(audio_bytes, preset=preset)
                        if extra_gain != 0:
                            mastered = apply_effect(mastered, "gain", gain_db=extra_gain)

                    st.success("Mastering complete!")
                    st.audio(mastered, format="audio/wav")

                    # Before/after analysis
                    after = analyze_audio(io.BytesIO(mastered))
                    if "error" not in after:
                        st.markdown("**Before vs After:**")
                        bc1, bc2 = st.columns(2)
                        bc1.metric("Before Loudness", f"{analysis.get('rms_db', '?')} dB")
                        bc2.metric("After Loudness", f"{after.get('rms_db', '?')} dB")

                    st.download_button(
                        "Download Mastered",
                        mastered,
                        f"mastered_{uploaded.name}",
                        key="master_dl",
                    )
                else:
                    st.error("Pedalboard/librosa not available. Install: pip install pedalboard librosa soundfile")

            # Individual effects
            st.markdown("---")
            st.markdown("#### Apply Single Effect")
            effect = st.selectbox("Effect", [
                "compressor", "reverb", "delay", "chorus",
                "highpass", "lowpass", "limiter", "gain",
            ], key="master_fx")

            fx_params = {}
            if effect == "compressor":
                fx_params["threshold"] = st.slider("Threshold (dB)", -40, 0, -20, key="fx_thresh")
                fx_params["ratio"] = st.slider("Ratio", 1.0, 20.0, 4.0, 0.5, key="fx_ratio")
            elif effect == "reverb":
                fx_params["room_size"] = st.slider("Room Size", 0.0, 1.0, 0.5, 0.05, key="fx_room")
                fx_params["wet"] = st.slider("Wet", 0.0, 1.0, 0.3, 0.05, key="fx_wet")
            elif effect == "delay":
                fx_params["time"] = st.slider("Delay (s)", 0.05, 1.0, 0.25, 0.05, key="fx_dtime")
                fx_params["feedback"] = st.slider("Feedback", 0.0, 0.9, 0.3, 0.05, key="fx_fb")
            elif effect in ("highpass", "lowpass"):
                fx_params["cutoff"] = st.slider("Cutoff (Hz)", 20, 16000, 200 if effect == "highpass" else 8000, key="fx_cut")
            elif effect == "gain":
                fx_params["gain_db"] = st.slider("Gain (dB)", -12.0, 12.0, 0.0, 0.5, key="fx_gdb")

            if st.button("Apply Effect", key="master_fx_go"):
                if HAS_AUDIO and audio_available():
                    with st.spinner(f"Applying {effect}..."):
                        processed = apply_effect(audio_bytes, effect, **fx_params)
                    st.audio(processed, format="audio/wav")
                    st.download_button("Download", processed, f"{effect}_{uploaded.name}", key="fx_dl")

    with col2:
        st.markdown("#### Mastering Reference")
        if HAS_PRESETS:
            for name, info in MASTERING_PRESETS.items():
                with st.expander(info["label"]):
                    st.markdown(f"**Target LUFS:** {info['target_lufs']}")
                    st.markdown(f"**Compression:** {info['compression']['ratio']}:1 @ {info['compression']['threshold']} dB")
                    st.markdown(f"**Limiter:** {info['limiter']['threshold']} dB")
                    st.markdown(f"_{info['description']}_")

        st.markdown("---")
        st.markdown("#### EQ Profiles")
        if HAS_PRESETS:
            for name, info in EQ_PROFILES.items():
                with st.expander(info["label"]):
                    st.markdown(f"HP: {info['high_pass']} Hz | Low Shelf: {info['low_shelf_gain']:+.1f} dB @ {info['low_shelf_freq']} Hz")
                    st.markdown(f"High Shelf: {info['high_shelf_gain']:+.1f} dB @ {info['high_shelf_freq']} Hz")
                    st.markdown(f"_{info['description']}_")

        st.markdown("---")
        st.markdown("#### API Status")
        if HAS_AUDIO:
            if audio_available():
                st.success("Pedalboard + librosa: Ready")
            else:
                st.warning("Pedalboard/librosa: Not installed")
        else:
            st.warning("Audio engine: Not available")

        if HAS_DOLBY and dolby_available():
            st.success("Dolby.io: Connected")
        else:
            st.info("Dolby.io: Not configured (optional cloud mastering)")
