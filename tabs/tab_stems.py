"""Tab 4: Stem Separation Lab — Demucs / LALAL.AI integration."""

import streamlit as st


def render():
    st.markdown("### Stem Separation Lab")
    st.caption("Upload any track. Get vocals, drums, bass, other. Powered by Demucs (Meta).")

    st.info("**Phase 2 Feature** — Full Demucs stem separation coming soon. "
            "Self-hosted FastAPI on Azure or LALAL.AI API.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Upload Track")
        uploaded = st.file_uploader("Drop a track to separate",
                                     type=["mp3", "wav", "flac", "aiff"],
                                     key="stem_upload")

        if uploaded:
            st.audio(uploaded)
            st.success(f"Loaded: **{uploaded.name}** ({uploaded.size / 1024 / 1024:.1f} MB)")

            st.markdown("#### Separation Model")
            model = st.selectbox("Model", [
                "Demucs v4 (htdemucs) — Best quality",
                "Demucs v4 (htdemucs_ft) — Fine-tuned, slower",
                "LALAL.AI Phoenix — Cloud API",
            ], key="stem_model")

            st.markdown("#### Output Stems")
            stems = st.multiselect("Select stems to extract", [
                "Vocals", "Drums", "Bass", "Other (instruments)",
            ], default=["Vocals", "Drums", "Bass", "Other (instruments)"], key="stem_select")

            output_format = st.selectbox("Output Format", ["WAV (24-bit)", "WAV (16-bit)", "FLAC", "MP3 320kbps"],
                                         key="stem_format")

            if st.button("Separate Stems", key="stem_go", type="primary"):
                with st.spinner("Separating stems..."):
                    import time
                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.05)
                        progress.progress(i + 1)

                st.success("Separation complete! (Demo mode)")

                # Demo output
                for stem in stems:
                    with st.expander(f"{stem}", expanded=True):
                        st.markdown(f"**{stem}** stem from {uploaded.name}")
                        st.markdown("*Connect Demucs API for real audio output*")

    with col2:
        st.markdown("#### Use Cases")
        st.markdown("""
**Remix Prep**
Extract stems from any track for remix work. Isolate vocals over your own production.

**Mashup Creation**
Combine vocals from one track with instrumentals from another. Perfect key/BPM matching.

**Acapella Extraction**
Pull clean vocals for DJ transitions, drops, or production samples.

**Practice / Analysis**
Isolate drum patterns to study. Remove vocals to practice mixing. Analyze bass lines.
""")

        st.markdown("---")
        st.markdown("#### Stem Queue")
        if "stem_queue" not in st.session_state:
            st.session_state.stem_queue = []

        if st.session_state.stem_queue:
            for item in st.session_state.stem_queue:
                st.markdown(f"- {item}")
        else:
            st.markdown("*No stems in queue*")

        st.markdown("---")
        st.markdown("#### API Status")
        lalal_key = st.secrets.get("LALAL_API_KEY", "")
        if lalal_key:
            st.success("LALAL.AI: Connected")
        else:
            st.warning("LALAL.AI: Not configured — using demo mode")
        st.info("Demucs: Self-hosted deployment pending")
