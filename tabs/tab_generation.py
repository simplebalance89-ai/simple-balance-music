"""Tab 5: AI Music Generation — Mubert / AIVA integration."""

import streamlit as st


MUBERT_GENRES = [
    "Ambient", "Chill", "Deep House", "Downtempo", "Drum & Bass",
    "Dubstep", "EDM", "Electro", "Future Bass", "House",
    "Lo-Fi", "Melodic Techno", "Minimal", "Progressive House",
    "Synthwave", "Tech House", "Techno", "Trance", "Trip Hop",
]

MUBERT_MOODS = [
    "Calm", "Dark", "Dreamy", "Energetic", "Epic",
    "Euphoric", "Focus", "Happy", "Intense", "Melancholic",
    "Motivating", "Mysterious", "Peaceful", "Powerful", "Relaxing",
    "Romantic", "Sad", "Uplifting", "Warm",
]


def render():
    st.markdown("### AI Music Generation")
    st.caption("Generate DMCA-free music with Mubert. Cinematic with AIVA. Infinite possibilities.")

    st.info("**Phase 2 Feature** — Mubert API ($49/mo) for infinite streams. "
            "AIVA for cinematic/orchestral. Currently in demo mode.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Generate Track")

        gen_type = st.radio("Generation Type", [
            "DJ Set Filler (Mubert)",
            "Cinematic / Orchestral (AIVA)",
            "Custom Mood Stream",
        ], key="gen_type")

        if gen_type == "DJ Set Filler (Mubert)":
            genre = st.selectbox("Genre", MUBERT_GENRES, key="gen_genre")
            mood = st.selectbox("Mood", MUBERT_MOODS, key="gen_mood")
            bpm = st.slider("BPM", 60, 180, 125, key="gen_bpm")
            duration = st.slider("Duration (seconds)", 30, 600, 120, key="gen_duration")

            st.markdown(f"""
**Preview:**
- Genre: {genre}
- Mood: {mood}
- BPM: {bpm}
- Duration: {duration}s ({duration // 60}:{duration % 60:02d})
""")

        elif gen_type == "Cinematic / Orchestral (AIVA)":
            style = st.selectbox("Style", [
                "Cinematic Epic", "Ambient Soundscape", "Classical Modern",
                "Electronic Cinematic", "Piano Solo", "Orchestral",
            ], key="gen_style")
            key = st.selectbox("Key", ["C Major", "A Minor", "D Minor", "F Major",
                                        "G Major", "E Minor", "Bb Major"], key="gen_key")
            duration = st.slider("Duration (seconds)", 30, 300, 90, key="gen_duration_aiva")

        else:
            prompt = st.text_area("Describe the music you want", key="gen_prompt",
                                  placeholder="Warm melodic house with rolling bass, "
                                             "gentle arpeggios, subtle vocal chops, 122 BPM...")
            duration = st.slider("Duration (seconds)", 30, 600, 180, key="gen_duration_custom")

        export_format = st.selectbox("Export Format", ["WAV", "MP3 320kbps", "FLAC"], key="gen_format")

        if st.button("Generate", key="gen_go", type="primary"):
            with st.spinner("Generating music..."):
                import time
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.04)
                    progress.progress(i + 1)
            st.success("Generation complete! (Demo mode — connect Mubert/AIVA API)")

    with col2:
        st.markdown("#### DMCA-Free Library")
        st.markdown("""
All generated tracks are **100% royalty-free** and **DMCA-safe**.

**Use cases:**
- DJ set fillers and transitions
- Background music for streams
- Content creation
- Podcast intros/outros
- Event background music
""")

        st.markdown("---")
        st.markdown("#### Generation History")
        if "gen_history" not in st.session_state:
            st.session_state.gen_history = []

        if st.session_state.gen_history:
            for item in st.session_state.gen_history:
                st.markdown(f"- {item}")
        else:
            st.markdown("*No generations yet*")

        st.markdown("---")
        st.markdown("#### API Status")
        mubert_key = st.secrets.get("MUBERT_API_KEY", "")
        if mubert_key:
            st.success("Mubert: Connected")
        else:
            st.warning("Mubert: Not configured ($49/mo) — demo mode")
        st.info("AIVA: Integration pending")

        st.markdown("---")
        st.markdown("#### Quick Presets")
        presets = {
            "Warm Up": "Ambient, Calm, 100 BPM, 120s",
            "Peak Energy": "Melodic Techno, Euphoric, 130 BPM, 180s",
            "Cool Down": "Chill, Relaxing, 110 BPM, 120s",
            "Transition": "Deep House, Dreamy, 122 BPM, 60s",
        }
        for name, desc in presets.items():
            st.markdown(f"**{name}:** {desc}")
