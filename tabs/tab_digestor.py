"""Tab: Mix Digestor -- Drop a mix, extract the full tracklist. AudD-powered."""

import streamlit as st
import json
import os
import time

try:
    from utils.audd_client import (
        extract_tracklist_enterprise,
        format_tracklist_text,
        format_tracklist_markdown,
        get_api_token,
    )
    HAS_AUDD = True
except ImportError:
    HAS_AUDD = False

try:
    from utils.audio_engine import analyze_audio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


def render():
    st.info("🔧 Testing in Progress — AudD enterprise API. Upload functionality being validated.")
    st.markdown("### Mix Digestor")
    st.caption("Drop a mix. Get every track. Powered by AudD audio fingerprinting.")

    if not HAS_AUDD:
        st.error("AudD client not available. Check utils/audd_client.py.")
        return

    token = get_api_token()
    if not token:
        st.warning("AudD API token not configured. Add AUDD_API_TOKEN to Streamlit secrets.")
        return

    # Session state for results
    if "digestor_results" not in st.session_state:
        st.session_state.digestor_results = {}
    if "digestor_history" not in st.session_state:
        st.session_state.digestor_history = []

    col_upload, col_results = st.columns([1, 2])

    with col_upload:
        st.markdown("#### Drop a Mix")

        input_method = st.radio(
            "Source", ["Upload File", "URL"],
            key="digestor_input_method", horizontal=True,
        )

        mix_name = st.text_input("Mix Name", key="digestor_name", placeholder="J.A.W. - Tingling and Numb")

        if input_method == "Upload File":
            uploaded = st.file_uploader(
                "Audio file", type=["mp3", "wav", "flac", "m4a", "ogg"],
                key="digestor_upload",
            )
            url = None
        else:
            uploaded = None
            url = st.text_input("Audio URL", key="digestor_url", placeholder="https://...")

        st.markdown("---")
        st.markdown("#### Settings")
        st.caption("AudD Enterprise scans the full mix and identifies every track with timestamps.")

        if st.button("DIGEST", key="digestor_go", type="primary", use_container_width=True):
            if not uploaded and not url:
                st.error("Drop a file or paste a URL first.")
            else:
                with st.spinner("Digesting mix... This can take a few minutes for long mixes."):
                    start_time = time.time()

                    if uploaded:
                        file_data = uploaded.read()
                        result = extract_tracklist_enterprise(file_data=file_data)
                    else:
                        result = extract_tracklist_enterprise(url=url)

                    elapsed = round(time.time() - start_time, 1)

                    if result.get("error"):
                        st.error(f"Error: {result['error']}")
                    else:
                        result["mix_name"] = mix_name or "Untitled Mix"
                        result["elapsed"] = elapsed
                        st.session_state.digestor_results = result

                        st.session_state.digestor_history.append({
                            "name": result["mix_name"],
                            "tracks": result.get("unique_tracks", 0),
                            "time": elapsed,
                        })

                        st.rerun()

        # Audio analysis (bonus)
        if uploaded and HAS_AUDIO:
            with st.expander("Audio Analysis"):
                if st.button("Analyze Audio", key="digestor_analyze"):
                    with st.spinner("Analyzing..."):
                        uploaded.seek(0)
                        data = uploaded.read()
                        analysis = analyze_audio(data)
                        if "error" not in analysis:
                            c1, c2 = st.columns(2)
                            c1.metric("BPM", str(analysis.get("bpm", "?")))
                            c2.metric("Key", str(analysis.get("key", "?")))
                            c3, c4 = st.columns(2)
                            c3.metric("Loudness", f"{analysis.get('rms_db', '?')} dB")
                            c4.metric("Duration", f"{analysis.get('duration', '?')}s")
                        else:
                            st.error(analysis["error"])

        # History
        if st.session_state.digestor_history:
            st.markdown("---")
            st.markdown("#### History")
            for h in reversed(st.session_state.digestor_history):
                st.caption(f"{h['name']} — {h['tracks']} tracks ({h['time']}s)")

    with col_results:
        result = st.session_state.digestor_results

        if not result or not result.get("tracks"):
            st.markdown("#### Tracklist")
            st.markdown("---")
            st.info("Drop a mix and hit DIGEST. The tracklist appears here.")
            st.markdown("")
            st.markdown("**How it works:**")
            st.markdown("1. Upload a mix or paste a URL")
            st.markdown("2. AudD scans the full audio with 150M+ track fingerprints")
            st.markdown("3. Every identified track gets timestamped")
            st.markdown("4. Tracks not on Spotify are flagged `UNRELEASED`")
            return

        # Header
        name = result.get("mix_name", "Mix")
        st.markdown(f"#### {name}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Tracks", result.get("unique_tracks", 0))
        c2.metric("Fingerprints", result.get("raw_matches", 0))
        c3.metric("Scan Time", f"{result.get('elapsed', '?')}s")

        unreleased_count = sum(1 for t in result["tracks"] if t.get("unreleased"))
        if unreleased_count:
            st.markdown(f"`{unreleased_count}` tracks marked **UNRELEASED** (not found on Spotify/Apple Music)")

        st.markdown("---")

        # Tracklist display
        for track in result["tracks"]:
            pos = track.get("position", "?")
            ts = track.get("timestamp", "??:??")
            artist = track.get("artist", "Unknown")
            title = track.get("title", "Unknown")
            unreleased = track.get("unreleased", False)

            # Track row
            col_num, col_info, col_links = st.columns([1, 6, 3])

            with col_num:
                st.markdown(f"**{ts}**")

            with col_info:
                label_text = f" · {track['label']}" if track.get("label") else ""
                if unreleased:
                    st.markdown(f"**{artist}** — *{title}* `UNRELEASED`{label_text}")
                else:
                    st.markdown(f"**{artist}** — *{title}*{label_text}")

            with col_links:
                links = []
                if track.get("spotify_url"):
                    links.append(f"[Spotify]({track['spotify_url']})")
                if track.get("apple_music_url"):
                    links.append(f"[Apple]({track['apple_music_url']})")
                if links:
                    st.markdown(" · ".join(links))
                elif unreleased:
                    st.caption("No streaming links")

        # Export options
        st.markdown("---")
        st.markdown("#### Export")
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            text_export = format_tracklist_text(result)
            st.download_button(
                "Download Tracklist (.txt)",
                text_export,
                file_name=f"{name.replace(' ', '_')}_tracklist.txt",
                mime="text/plain",
                key="digestor_dl_txt",
                use_container_width=True,
            )

        with exp_col2:
            json_export = json.dumps(result, indent=2, default=str)
            st.download_button(
                "Download JSON",
                json_export,
                file_name=f"{name.replace(' ', '_')}_tracklist.json",
                mime="application/json",
                key="digestor_dl_json",
                use_container_width=True,
            )

        # Copy-friendly text
        with st.expander("Plain Text Tracklist (Copy/Paste)"):
            st.code(text_export, language=None)
