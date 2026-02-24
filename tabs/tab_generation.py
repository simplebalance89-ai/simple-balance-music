"""Tab 5: AI Music Generation — MusicGen via Replicate + MIDI generation."""

import streamlit as st
import io
import os

try:
    from utils.replicate_client import generate_music, _is_connected as replicate_connected
    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False
    replicate_connected = lambda: False

try:
    from utils.midi_engine import (
        generate_midi_from_text, create_chord_progression, create_drum_pattern,
        create_bassline, midi_to_audio,
    )
    HAS_MIDI = True
except ImportError:
    HAS_MIDI = False

try:
    from utils.mau5trap_presets import BPM_PRESETS, KEY_PRESETS, CHORD_PROGRESSIONS, GENRE_TEMPLATES
    HAS_PRESETS = True
except ImportError:
    HAS_PRESETS = False

try:
    from utils.audio_engine import analyze_audio, is_available as audio_available
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


MUSICGEN_MODELS = {
    "meta/musicgen:large": "MusicGen Large (best quality, ~30s max)",
    "meta/musicgen:medium": "MusicGen Medium (faster, good quality)",
    "meta/musicgen:small": "MusicGen Small (fastest, lower quality)",
}


def render():
    st.markdown("### AI Music Generation")
    st.caption("Generate music with MusicGen (Meta) via Replicate. Create MIDI with AI. mau5trap presets built in.")

    gen_mode = st.radio("Mode", ["AI Audio Generation", "MIDI Generation", "mau5trap Templates"],
                         horizontal=True, key="gen_mode")

    if gen_mode == "AI Audio Generation":
        _render_audio_gen()
    elif gen_mode == "MIDI Generation":
        _render_midi_gen()
    else:
        _render_templates()


def _render_audio_gen():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Text-to-Music (MusicGen)")
        prompt = st.text_area(
            "Describe the music",
            key="gen_prompt",
            placeholder="Dark progressive house, 128 BPM, minor key, rolling bassline, "
                        "atmospheric pads, subtle vocal chops, building energy...",
            height=100,
        )

        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            model = st.selectbox("Model", list(MUSICGEN_MODELS.keys()),
                                  format_func=lambda x: MUSICGEN_MODELS[x], key="gen_model")
        with gc2:
            duration = st.slider("Duration (sec)", 5, 30, 15, key="gen_dur")
        with gc3:
            temperature = st.slider("Creativity", 0.5, 1.5, 1.0, 0.1, key="gen_temp")

        cfg = st.slider("Prompt Adherence (CFG)", 1, 10, 3, key="gen_cfg")

        if st.button("Generate", key="gen_go", type="primary"):
            if not prompt:
                st.warning("Enter a description first.")
            elif HAS_REPLICATE and replicate_connected():
                with st.spinner(f"Generating {duration}s of music via MusicGen..."):
                    result = generate_music(
                        prompt=prompt,
                        duration=duration,
                        model=model,
                        temperature=temperature,
                        classifier_free_guidance=cfg,
                    )
                if result.get("status") == "complete" and result.get("url"):
                    st.success("Generation complete!")
                    st.audio(result["url"])
                    st.markdown(f"[Download audio]({result['url']})")

                    # Analyze generated audio
                    if HAS_AUDIO:
                        try:
                            import requests
                            resp = requests.get(result["url"], timeout=30)
                            if resp.status_code == 200:
                                analysis = analyze_audio(io.BytesIO(resp.content))
                                if "error" not in analysis:
                                    mc1, mc2, mc3 = st.columns(3)
                                    mc1.metric("Detected BPM", analysis.get("bpm", "?"))
                                    mc2.metric("Detected Key", analysis.get("key", "?"))
                                    mc3.metric("Loudness", f"{analysis.get('rms_db', '?')} dB")
                        except Exception:
                            pass
                elif result.get("status") == "error":
                    st.error(f"Generation failed: {result.get('error', 'Unknown')}")
                else:
                    st.info(f"Status: {result.get('status')} — {result.get('message', '')}")
            else:
                st.warning("Replicate API not configured. Set REPLICATE_API_TOKEN in secrets.")

    with col2:
        st.markdown("#### Prompt Ideas")
        prompts = {
            "mau5trap Progressive": "Dark progressive house, 128 BPM, Am, rolling bass, sidechain pump, atmospheric pads, building tension",
            "TESTPILOT Techno": "Minimal dark techno, 132 BPM, driving kick, industrial textures, hypnotic loop, acid bassline",
            "Melodic Breakdown": "Emotional melodic techno breakdown, 125 BPM, piano arpeggios, lush reverb, cinematic strings",
            "Deep House Groove": "Deep house groove, 122 BPM, warm analog bass, smooth chords, subtle percussion, vinyl warmth",
            "Ambient Intro": "Ambient electronic intro, slow build, ethereal pads, granular textures, space and silence",
        }
        for name, p in prompts.items():
            if st.button(name, key=f"gen_preset_{name[:10]}"):
                st.session_state["gen_prompt"] = p
                st.rerun()

        st.markdown("---")
        st.markdown("#### API Status")
        if HAS_REPLICATE and replicate_connected():
            st.success("Replicate (MusicGen): Connected")
        else:
            st.warning("Replicate: Not configured")


def _render_midi_gen():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### AI MIDI Generation")
        st.caption("Describe music in text, get MIDI output via Azure OpenAI.")

        midi_prompt = st.text_area(
            "Describe the MIDI pattern",
            key="midi_prompt",
            placeholder="A melancholic chord progression in A minor with arpeggiated patterns...",
            height=80,
        )
        mc1, mc2 = st.columns(2)
        with mc1:
            midi_bpm = st.number_input("BPM", 60, 200, 128, key="midi_bpm")
        with mc2:
            midi_model = st.text_input("Model", "gpt-4o", key="midi_model")

        if st.button("Generate MIDI", key="midi_gen_go", type="primary") and midi_prompt:
            if HAS_MIDI:
                with st.spinner("Generating MIDI via AI..."):
                    result = generate_midi_from_text(midi_prompt, model=midi_model, bpm=midi_bpm)
                if result.get("status") == "complete":
                    st.success("MIDI generated!")
                    if result.get("abc_notation"):
                        with st.expander("ABC Notation"):
                            st.code(result["abc_notation"])
                    midi_path = result.get("midi_path")
                    if midi_path and os.path.exists(midi_path):
                        with open(midi_path, "rb") as f:
                            st.download_button("Download MIDI", f.read(), "generated.mid", key="midi_dl")
                else:
                    st.warning(f"MIDI generation: {result.get('message', result.get('status'))}")
            else:
                st.error("MIDI engine not available. Install: pretty_midi, music21, mido")

        st.markdown("---")
        st.markdown("#### Quick MIDI Generators")

        # Chord Progression
        st.markdown("**Chord Progression**")
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            chord_root = st.selectbox("Root", ["A", "B", "C", "D", "E", "F", "G", "F#", "Ab", "Bb"], key="chord_root")
        with cp2:
            chord_scale = st.selectbox("Scale", ["minor", "major", "dorian", "phrygian"], key="chord_scale")
        with cp3:
            if HAS_PRESETS:
                prog_name = st.selectbox("Progression", list(CHORD_PROGRESSIONS.keys()),
                                          format_func=lambda x: CHORD_PROGRESSIONS[x]["label"], key="chord_prog")
                chord_prog = CHORD_PROGRESSIONS[prog_name]["progression"]
            else:
                chord_prog = ["i", "VI", "III", "VII"]
                st.text("i - VI - III - VII")

        chord_bpm = st.number_input("BPM", 60, 200, 128, key="chord_bpm")
        if st.button("Generate Chords", key="chord_gen") and HAS_MIDI:
            with st.spinner("Generating..."):
                path = create_chord_progression(chord_root, chord_scale, chord_prog, chord_bpm)
            if isinstance(path, str) and os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button("Download Chord MIDI", f.read(), "chords.mid", key="chord_dl")
                st.success("Chord progression MIDI generated!")

        # Drum Pattern
        st.markdown("**Drum Pattern**")
        dp1, dp2, dp3 = st.columns(3)
        with dp1:
            drum_style = st.selectbox("Style", ["progressive_house", "techno", "deep_house", "breakbeat", "testpilot"], key="drum_style")
        with dp2:
            drum_bpm = st.number_input("BPM", 60, 200, 128, key="drum_bpm")
        with dp3:
            drum_bars = st.number_input("Bars", 1, 16, 4, key="drum_bars")

        if st.button("Generate Drums", key="drum_gen") and HAS_MIDI:
            with st.spinner("Generating..."):
                path = create_drum_pattern(drum_style, drum_bpm, drum_bars)
            if isinstance(path, str) and os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button("Download Drum MIDI", f.read(), f"drums_{drum_style}.mid", key="drum_dl")
                st.success("Drum pattern MIDI generated!")

        # Bassline
        st.markdown("**Bassline**")
        bass_root = st.selectbox("Bass Root", ["A", "C", "D", "E", "F", "G"], key="bass_root")
        bass_bpm = st.number_input("BPM", 60, 200, 128, key="bass_bpm")
        if st.button("Generate Bassline", key="bass_gen") and HAS_MIDI:
            with st.spinner("Generating..."):
                path = create_bassline(bass_root, bpm=bass_bpm)
            if isinstance(path, str) and os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button("Download Bass MIDI", f.read(), "bassline.mid", key="bass_dl")
                st.success("Bassline MIDI generated!")

    with col2:
        st.markdown("#### MIDI Tips")
        st.markdown("""
- **Chord MIDI** loads into any DAW (Ableton, FL Studio, Logic)
- **Drum MIDI** maps to General MIDI drum kit
- **Bassline MIDI** includes sidechain-style rests
- All MIDI is editable after import
- Combine chord + drum + bass for a full arrangement skeleton
""")

        st.markdown("---")
        st.markdown("#### Status")
        if HAS_MIDI:
            st.success("MIDI engine: Ready")
        else:
            st.warning("MIDI engine: Not available")


def _render_templates():
    st.markdown("#### mau5trap Production Templates")
    st.caption("One-click genre templates with all parameters pre-configured.")

    if not HAS_PRESETS:
        st.warning("mau5trap presets module not available.")
        return

    for name, template in GENRE_TEMPLATES.items():
        with st.expander(f"{name.replace('_', ' ').title()}", expanded=False):
            st.markdown(f"_{template['description']}_")
            tc1, tc2, tc3, tc4 = st.columns(4)
            tc1.metric("BPM", template["bpm"])
            tc2.metric("Key", template["key"])
            tc3.metric("Sidechain", template["sidechain"])
            tc4.metric("Drums", template["drum_style"])

            if st.button(f"Generate Full Stack", key=f"tmpl_{name}"):
                if HAS_MIDI:
                    with st.spinner(f"Generating {name} MIDI stack..."):
                        # Get progression
                        prog_key = template.get("progression", "mau5trap_classic")
                        prog = CHORD_PROGRESSIONS.get(prog_key, {}).get("progression", ["i", "VI", "III", "VII"])

                        chord_path = create_chord_progression(template["key"].replace("m", ""), "minor", prog, template["bpm"])
                        drum_path = create_drum_pattern(template["drum_style"], template["bpm"], 4)
                        bass_path = create_bassline(template["key"].replace("m", ""), bpm=template["bpm"])

                    st.success(f"Generated {name} MIDI stack!")
                    for label, path in [("Chords", chord_path), ("Drums", drum_path), ("Bass", bass_path)]:
                        if isinstance(path, str) and os.path.exists(path):
                            with open(path, "rb") as f:
                                st.download_button(f"Download {label} MIDI", f.read(), f"{name}_{label.lower()}.mid",
                                                    key=f"tmpl_dl_{name}_{label}")
                else:
                    st.error("MIDI engine not available.")
