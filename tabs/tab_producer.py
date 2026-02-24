"""Tab 9: Producer Tools — Reference analyzer, scale helper, production AI."""

import streamlit as st
import io
import os

try:
    from utils.midi_engine import (
        create_chord_progression, create_drum_pattern, create_bassline,
        _get_scale_notes, _get_drum_patterns, SCALE_INTERVALS, NOTE_MAP,
    )
    HAS_MIDI = True
except ImportError:
    HAS_MIDI = False

try:
    from utils.audio_engine import (
        analyze_audio, get_waveform_data, get_spectrogram_data,
        get_frequency_spectrum, key_to_camelot, get_compatible_camelot,
        is_available as audio_available,
    )
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

try:
    from utils.ai_client import chat
except ImportError:
    chat = None

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from utils.mau5trap_presets import CHORD_PROGRESSIONS, EQ_PROFILES, SIDECHAIN_PRESETS
    HAS_PRESETS = True
except ImportError:
    HAS_PRESETS = False


PRODUCER_PROMPT = (
    "You are a music production assistant for mau5trap-style electronic music. "
    "Help with chord progressions, sound design, mixing, arrangement, and production workflow. "
    "Keep it practical. Reference deadmau5, TESTPILOT, Strobe, etc. when relevant. "
    "Speak in terms DJs transitioning into production understand."
)

ROOT_NOTES = ["C", "D", "E", "F", "G", "A", "B", "F#", "Ab", "Bb", "Db", "Eb"]
SCALE_NAMES = list(SCALE_INTERVALS.keys()) if HAS_MIDI else ["major", "minor"]


def render():
    st.markdown("### Producer Tools")
    st.caption("Reference analysis. Scale/key tools. Production AI advisor.")

    tabs = st.tabs(["Reference Analyzer", "Scale/Key Helper", "Drum Grid", "Production AI"])

    # Reference Analyzer
    with tabs[0]:
        st.markdown("#### Reference Track Analyzer")
        ref_file = st.file_uploader("Upload reference track", type=["mp3", "wav", "flac"], key="prod_ref")

        if ref_file:
            audio_bytes = ref_file.read()
            st.audio(audio_bytes, format="audio/wav")

            if st.button("Analyze", key="prod_ref_go", type="primary"):
                if HAS_AUDIO and audio_available():
                    with st.spinner("Analyzing reference..."):
                        result = analyze_audio(io.BytesIO(audio_bytes))

                    if "error" not in result:
                        rc1, rc2, rc3, rc4 = st.columns(4)
                        rc1.metric("BPM", result.get("bpm", "?"))
                        rc2.metric("Key", result.get("key", "?"))
                        rc3.metric("Loudness", f"{result.get('rms_db', '?')} dB")
                        rc4.metric("Peak", f"{result.get('peak_db', '?')} dB")

                        rc5, rc6 = st.columns(2)
                        rc5.metric("Duration", f"{result.get('duration', '?')}s")
                        rc6.metric("Brightness", f"{result.get('brightness', '?')} Hz")

                        # Camelot
                        detected_key = result.get("key", "")
                        camelot = key_to_camelot(detected_key) if HAS_AUDIO else ""
                        if camelot:
                            compatible = get_compatible_camelot(camelot)
                            st.markdown(f"**Camelot:** {camelot} | **Compatible:** {', '.join(compatible)}")

                        # Waveform
                        if HAS_PLOTLY and HAS_NUMPY:
                            times, waveform = get_waveform_data(io.BytesIO(audio_bytes))
                            if times is not None:
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=times, y=waveform, mode="lines",
                                                          line=dict(color="#FFC000", width=1)))
                                fig.update_layout(
                                    title="Waveform",
                                    plot_bgcolor="#0a0a1a", paper_bgcolor="#0a0a1a",
                                    font_color="#e2e8f0", height=200,
                                    margin=dict(l=40, r=20, t=40, b=30),
                                    xaxis_title="Time (s)", yaxis_title="Amplitude",
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        # Frequency spectrum
                        if HAS_PLOTLY and HAS_NUMPY:
                            freqs, mags = get_frequency_spectrum(audio_bytes)
                            if freqs is not None:
                                fig2 = go.Figure()
                                fig2.add_trace(go.Scatter(x=freqs, y=mags, mode="lines",
                                                           line=dict(color="#a78bfa", width=1)))
                                fig2.update_layout(
                                    title="Frequency Spectrum",
                                    plot_bgcolor="#0a0a1a", paper_bgcolor="#0a0a1a",
                                    font_color="#e2e8f0", height=200,
                                    margin=dict(l=40, r=20, t=40, b=30),
                                    xaxis_title="Frequency (Hz)", yaxis_title="Magnitude",
                                    xaxis_type="log",
                                )
                                st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.error(result.get("error", "Analysis failed"))
                else:
                    st.error("Audio engine not available. Install: librosa, pedalboard, soundfile")
        else:
            st.info("Upload a reference track to analyze BPM, key, loudness, and spectrum.")

        # AI reference analysis by name
        if chat:
            ref_name = st.text_input("Or describe a track to analyze", key="prod_ref_name",
                                      placeholder="Colyn - Oxygen Levels Low")
            if st.button("AI Analyze", key="prod_ref_ai") and ref_name:
                prompt = "Analyze this track for production insights: " + ref_name
                with st.spinner("Analyzing..."):
                    r = chat(PRODUCER_PROMPT, [{"role": "user", "content": prompt}])
                    st.markdown(r)

    # Scale/Key Helper
    with tabs[1]:
        st.markdown("#### Scale & Key Reference")
        sk1, sk2 = st.columns(2)
        with sk1:
            root = st.selectbox("Root Note", ROOT_NOTES, key="sk_root")
        with sk2:
            scale = st.selectbox("Scale", SCALE_NAMES, key="sk_scale")

        if HAS_MIDI:
            notes = _get_scale_notes(root, scale, 4)
            note_names_list = list(NOTE_MAP.keys())
            display = []
            for n in notes:
                idx = n % 12
                for name, val in NOTE_MAP.items():
                    if val == idx:
                        display.append(name)
                        break
            st.markdown(f"**Notes:** {' - '.join(display)}")

        # Camelot reference
        st.markdown("---")
        st.markdown("#### Camelot Wheel Quick Reference")
        if HAS_AUDIO:
            test_key = root + "m" if scale == "minor" else root
            cam = key_to_camelot(test_key)
            if cam:
                compatible = get_compatible_camelot(cam)
                st.markdown(f"**{test_key}** = Camelot **{cam}**")
                st.markdown(f"**Compatible keys:** {', '.join(compatible)}")

        st.markdown("---")
        st.markdown("#### Common mau5trap Progressions")
        if HAS_PRESETS:
            for name, info in CHORD_PROGRESSIONS.items():
                prog_str = " - ".join(info["progression"])
                st.markdown(f"**{info['label']}:** {prog_str} | _{info['description']}_")

    # Drum Grid
    with tabs[2]:
        st.markdown("#### Drum Pattern Reference")
        if HAS_MIDI:
            patterns = _get_drum_patterns()
            style = st.selectbox("Style", list(patterns.keys()), key="dg_style")
            pat = patterns[style]

            st.markdown("**16-step grid:**")
            header = "             " + " ".join(f"{i+1:2d}" for i in range(16))
            st.text(header)
            for drum_type, hits in pat.items():
                row = drum_type.ljust(12) + " "
                for step in range(16):
                    row += " X " if step in hits else " . "
                st.text(row)

            dg1, dg2 = st.columns(2)
            with dg1:
                dg_bpm = st.number_input("BPM", 60, 200, 128, key="dg_bpm")
            with dg2:
                dg_bars = st.number_input("Bars", 1, 16, 4, key="dg_bars")

            if st.button("Generate MIDI", key="dg_gen", type="primary"):
                with st.spinner("Generating..."):
                    path = create_drum_pattern(style, dg_bpm, dg_bars)
                if isinstance(path, str) and os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button("Download Drum MIDI", f.read(), f"drums_{style}.mid", key="dg_dl")
                    st.success("Generated!")
        else:
            st.info("MIDI engine not available.")

    # Production AI
    with tabs[3]:
        st.markdown("#### Production AI Advisor")
        if chat:
            ck = "producer_messages"
            if ck not in st.session_state:
                st.session_state[ck] = []
            for msg in st.session_state[ck]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if not st.session_state[ck]:
                with st.chat_message("assistant"):
                    st.markdown("Production AI ready. Ask about sound design, arrangement, mixing, mastering, "
                                "or anything production-related. I speak mau5trap.")
            if prompt := st.chat_input("Ask about production...", key="prod_ai_input"):
                st.session_state[ck].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        reply = chat(PRODUCER_PROMPT, st.session_state[ck])
                        st.markdown(reply)
                        st.session_state[ck].append({"role": "assistant", "content": reply})
        else:
            st.info("Configure Azure OpenAI for production AI assistant.")
