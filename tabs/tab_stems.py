"""Tab 4: Stem Separation Lab — Demucs via Replicate."""

import streamlit as st
import requests
import io

try:
    from utils.replicate_client import separate_stems, _is_connected as replicate_connected
    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False
    replicate_connected = lambda: False

try:
    from utils.audio_engine import analyze_audio, get_waveform_data, is_available as audio_available
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


def render():
    st.markdown("### Stem Separation Lab")
    st.caption("Separate any track into vocals, drums, bass, and other. Powered by Demucs (Meta) via Replicate.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Upload Track")
        uploaded = st.file_uploader(
            "Drop a track to separate",
            type=["mp3", "wav", "flac", "aiff"],
            key="stem_upload",
        )

        if uploaded:
            audio_bytes = uploaded.read()
            st.audio(audio_bytes, format="audio/wav")
            st.success(f"Loaded: **{uploaded.name}** ({len(audio_bytes) / 1024 / 1024:.1f} MB)")

            # Analyze first
            if HAS_AUDIO and audio_available():
                with st.spinner("Analyzing..."):
                    analysis = analyze_audio(io.BytesIO(audio_bytes))
                if "error" not in analysis:
                    ac1, ac2, ac3 = st.columns(3)
                    ac1.metric("BPM", analysis.get("bpm", "?"))
                    ac2.metric("Key", analysis.get("key", "?"))
                    ac3.metric("Duration", f"{analysis.get('duration', '?')}s")

            st.markdown("#### Separation Settings")
            stems_count = st.radio("Stems", [2, 4], index=1, horizontal=True, key="stem_count",
                                    format_func=lambda x: f"{x} stems" + (" (vocals/instrumental)" if x == 2 else " (vocals/drums/bass/other)"))

            if st.button("Separate Stems", key="stem_go", type="primary"):
                if HAS_REPLICATE and replicate_connected():
                    with st.spinner("Separating stems via Demucs on Replicate... (this may take 1-3 minutes)"):
                        # For Replicate, we need a URL — upload to temp storage or use data URI
                        # In production, you'd upload to S3/GCS first
                        # For now, show that the API is connected and ready
                        st.info("Stem separation requires the audio file to be accessible via URL. "
                                "Upload your track to a cloud storage service and provide the URL below.")

                        audio_url = st.text_input("Audio URL", key="stem_url",
                                                   placeholder="https://storage.example.com/track.wav")
                        if audio_url:
                            result = separate_stems(audio_url, stems=stems_count)
                            if result.get("status") == "complete":
                                st.success("Separation complete!")
                                stem_names = ["vocals", "drums", "bass", "other"] if stems_count == 4 else ["vocals", "other"]
                                for stem_name in stem_names:
                                    url = result.get(stem_name)
                                    if url:
                                        with st.expander(f"{stem_name.title()}", expanded=True):
                                            st.audio(url)
                                            st.markdown(f"[Download {stem_name}]({url})")
                            elif result.get("status") == "error":
                                st.error(f"Separation failed: {result.get('error', 'Unknown error')}")
                            else:
                                st.warning(f"Status: {result.get('status')} — {result.get('message', '')}")
                else:
                    st.warning("Replicate API not configured. Set REPLICATE_API_TOKEN in secrets.")
                    st.markdown("**Demo mode:** Here's what each stem would contain:")
                    for stem in ["Vocals", "Drums", "Bass", "Other"]:
                        with st.expander(stem):
                            st.markdown(f"**{stem}** stem from {uploaded.name}")

        # URL-based separation
        st.markdown("---")
        st.markdown("#### Separate from URL")
        st.caption("Provide a direct link to an audio file.")
        url_input = st.text_input("Audio file URL", key="stem_url_direct",
                                   placeholder="https://example.com/track.wav")
        if url_input and st.button("Separate from URL", key="stem_url_go"):
            if HAS_REPLICATE and replicate_connected():
                with st.spinner("Separating stems..."):
                    result = separate_stems(url_input, stems=4)
                    if result.get("status") == "complete":
                        st.success("Separation complete!")
                        for stem_name in ["vocals", "drums", "bass", "other"]:
                            url = result.get(stem_name)
                            if url:
                                with st.expander(f"{stem_name.title()}", expanded=True):
                                    st.audio(url)
                                    st.markdown(f"[Download {stem_name}]({url})")
                    elif result.get("status") == "error":
                        st.error(f"Error: {result.get('error')}")
                    else:
                        st.info(f"Status: {result.get('status')} — {result.get('message', '')}")
            else:
                st.warning("Replicate API not configured.")

    with col2:
        st.markdown("#### Use Cases")
        st.markdown("""
**Remix Prep**
Extract stems from any track for remix work. Isolate vocals over your own production.

**Mashup Creation**
Combine vocals from one track with instrumentals from another.

**Acapella Extraction**
Pull clean vocals for DJ transitions, drops, or production samples.

**Practice / Analysis**
Isolate drum patterns to study. Remove vocals to practice mixing.
""")

        st.markdown("---")
        st.markdown("#### How It Works")
        st.markdown("""
1. **Upload** or provide URL to your audio file
2. **Demucs v4** (Meta) runs on Replicate GPU cloud
3. **4 stems** returned: vocals, drums, bass, other
4. **Download** each stem individually
""")

        st.markdown("---")
        st.markdown("#### API Status")
        if HAS_REPLICATE and replicate_connected():
            st.success("Replicate (Demucs): Connected")
        else:
            st.warning("Replicate: Not configured — set REPLICATE_API_TOKEN")
        if HAS_AUDIO:
            st.success("Audio analysis: Ready")
        else:
            st.info("librosa: Not installed (optional analysis)")
