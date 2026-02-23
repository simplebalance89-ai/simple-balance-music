"""Tab 7: Set Builder — Drag-and-drop set planning with BPM/key analysis."""

import streamlit as st
import pandas as pd
from utils.ai_client import chat

SET_BUILDER_PROMPT = """You are the J.A.W. Set Builder AI. You help Peter and Jimmy build DJ sets with perfect energy flow.

Given a list of tracks with BPM, key, and energy, you:
1. Analyze the flow
2. Flag any energy rule violations
3. Suggest reordering for smoother transitions
4. Recommend bridge tracks where needed

ENERGY RULES:
- Max jump: +2 levels per track
- Max drop: -1 level per track
- Opening: energy 2-3 max
- Peak duration: 3-5 tracks max
- BPM jump: ±8 BPM max (±15 with harmonic mix)

Respond with a numbered tracklist and energy flow visualization."""


def render():
    st.markdown("### Set Builder")
    st.caption("Plan your set. Visualize energy flow. Get AI suggestions.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Build Your Set")

        # Initialize set list
        if "set_tracks" not in st.session_state:
            st.session_state.set_tracks = []

        # Add track form
        with st.expander("Add Track", expanded=True):
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                track_name = st.text_input("Track", key="sb_track", placeholder="Track name")
                artist = st.text_input("Artist", key="sb_artist", placeholder="Artist name")
            with t_col2:
                bpm = st.number_input("BPM", 60, 180, 125, key="sb_bpm")
                key = st.selectbox("Key", ["Am", "Bm", "Cm", "Dm", "Em", "Fm", "Gm",
                                            "A", "B", "C", "D", "E", "F", "G"], key="sb_key")
            with t_col3:
                energy = st.slider("Energy (1-6)", 1, 6, 3, key="sb_energy")
                genre = st.text_input("Genre", key="sb_genre", placeholder="e.g. Melodic Techno")

            if st.button("Add to Set", key="sb_add"):
                if track_name and artist:
                    st.session_state.set_tracks.append({
                        "track": track_name,
                        "artist": artist,
                        "bpm": bpm,
                        "key": key,
                        "energy": energy,
                        "genre": genre,
                    })
                    st.success(f"Added: {track_name} — {artist}")

        # Display current set
        if st.session_state.set_tracks:
            st.markdown("#### Current Set")

            for i, track in enumerate(st.session_state.set_tracks):
                energy_bar = "█" * track["energy"] + "░" * (6 - track["energy"])
                cols = st.columns([0.5, 3, 1, 1, 1, 0.5])
                cols[0].markdown(f"**{i + 1}**")
                cols[1].markdown(f"**{track['track']}** — {track['artist']}")
                cols[2].markdown(f"`{track['bpm']} BPM`")
                cols[3].markdown(f"`{track['key']}`")
                cols[4].markdown(f"`{energy_bar}`")
                if cols[5].button("X", key=f"sb_rm_{i}"):
                    st.session_state.set_tracks.pop(i)
                    st.rerun()

            # Energy flow visualization
            st.markdown("#### Energy Flow")
            energy_data = pd.DataFrame({
                "Track #": range(1, len(st.session_state.set_tracks) + 1),
                "Energy": [t["energy"] for t in st.session_state.set_tracks],
                "BPM": [t["bpm"] for t in st.session_state.set_tracks],
            })

            st.line_chart(energy_data.set_index("Track #")["Energy"], height=200)

            # Violation check
            violations = []
            for i in range(1, len(st.session_state.set_tracks)):
                prev = st.session_state.set_tracks[i - 1]
                curr = st.session_state.set_tracks[i]
                e_diff = curr["energy"] - prev["energy"]
                bpm_diff = abs(curr["bpm"] - prev["bpm"])

                if e_diff > 2:
                    violations.append(f"Track {i + 1}: Energy jump +{e_diff} (max +2)")
                if e_diff < -1:
                    violations.append(f"Track {i + 1}: Energy drop {e_diff} (max -1)")
                if bpm_diff > 8:
                    violations.append(f"Track {i + 1}: BPM jump ±{bpm_diff} (max ±8)")

            if st.session_state.set_tracks[0]["energy"] > 3:
                violations.append(f"Track 1: Opening energy {st.session_state.set_tracks[0]['energy']} (max 3)")

            if violations:
                st.warning("**Energy Alerts:**\n" + "\n".join(f"- {v}" for v in violations))
            else:
                st.success("Energy flow looks clean!")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Get AI Suggestions", key="sb_ai", type="primary"):
                    set_text = "\n".join(
                        f"{i + 1}. {t['track']} — {t['artist']} ({t['bpm']} BPM, {t['key']}, Energy {t['energy']})"
                        for i, t in enumerate(st.session_state.set_tracks)
                    )
                    prompt = f"Analyze this set and suggest improvements:\n\n{set_text}"
                    with st.spinner("Analyzing set..."):
                        reply = chat(SET_BUILDER_PROMPT, [{"role": "user", "content": prompt}])
                        st.markdown(reply)

            with col_b:
                if st.button("Clear Set", key="sb_clear"):
                    st.session_state.set_tracks = []
                    st.rerun()

        else:
            st.info("Add tracks to start building your set.")

    with col2:
        st.markdown("#### Set Templates")

        templates = {
            "Standard 2-Hour": [
                {"track": "Opener", "artist": "TBD", "bpm": 118, "key": "Am", "energy": 2, "genre": "Deep House"},
                {"track": "Warm Up", "artist": "TBD", "bpm": 120, "key": "Cm", "energy": 3, "genre": "Melodic House"},
                {"track": "Build 1", "artist": "TBD", "bpm": 124, "key": "Dm", "energy": 4, "genre": "Progressive"},
                {"track": "Peak 1", "artist": "TBD", "bpm": 128, "key": "Em", "energy": 5, "genre": "Melodic Techno"},
                {"track": "Peak 2", "artist": "TBD", "bpm": 130, "key": "Fm", "energy": 6, "genre": "Melodic Techno"},
                {"track": "Sustain", "artist": "TBD", "bpm": 126, "key": "Dm", "energy": 5, "genre": "Progressive"},
                {"track": "Wind Down", "artist": "TBD", "bpm": 122, "key": "Am", "energy": 4, "genre": "Melodic House"},
                {"track": "Closer", "artist": "TBD", "bpm": 118, "key": "Gm", "energy": 3, "genre": "Deep House"},
            ],
            "Journey (Emotional Arc)": [
                {"track": "Ground", "artist": "TBD", "bpm": 115, "key": "Am", "energy": 2, "genre": "Ambient"},
                {"track": "Rise", "artist": "TBD", "bpm": 120, "key": "Cm", "energy": 3, "genre": "Deep House"},
                {"track": "Release", "artist": "TBD", "bpm": 126, "key": "Dm", "energy": 5, "genre": "Progressive"},
                {"track": "Breathe", "artist": "TBD", "bpm": 120, "key": "Em", "energy": 3, "genre": "Melodic"},
                {"track": "Anticipate", "artist": "TBD", "bpm": 126, "key": "Fm", "energy": 5, "genre": "Melodic Techno"},
                {"track": "Transcend", "artist": "TBD", "bpm": 132, "key": "Gm", "energy": 6, "genre": "Techno"},
                {"track": "Land", "artist": "TBD", "bpm": 118, "key": "Am", "energy": 2, "genre": "Ambient"},
            ],
        }

        for name, tracks in templates.items():
            if st.button(f"Load: {name}", key=f"sb_tmpl_{name}"):
                st.session_state.set_tracks = tracks.copy()
                st.rerun()

        st.markdown("---")
        st.markdown("#### Export")
        if st.session_state.get("set_tracks"):
            export_text = "SET LIST — Simple Balance\n"
            export_text += "=" * 40 + "\n\n"
            for i, t in enumerate(st.session_state.set_tracks):
                export_text += f"{i + 1}. {t['track']} — {t['artist']}\n"
                export_text += f"   {t['bpm']} BPM | {t['key']} | Energy {t['energy']}/6\n\n"

            st.download_button("Download Tracklist", export_text, "setlist.txt",
                              "text/plain", key="sb_export")
