"""Tab 7: Set Builder -- Track-by-track set planner with energy/BPM/key analysis."""

import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from utils.audio_engine import key_to_camelot, are_keys_compatible
except ImportError:
    key_to_camelot = None
    are_keys_compatible = None

try:
    from utils.ai_client import chat
except ImportError:
    chat = None


ALL_KEYS = ["Am", "Bm", "Cm", "Dm", "Em", "Fm", "Gm",
            "A", "B", "C", "D", "E", "F", "G",
            "F#m", "G#m", "C#m", "D#m", "Bbm",
            "F#", "Ab", "Bb", "Db", "Eb"]

SET_PROMPT = (
    "You are a DJ set building AI. Analyze track lists for energy flow, "
    "BPM transitions, and harmonic compatibility. Suggest reordering, "
    "bridge tracks, and improvements. Flag energy jumps over +2 or drops "
    "below -1. Max BPM jump is 8 without harmonic mixing. Opening energy "
    "should be 2-3, peak duration 3-5 tracks max."
)

PRESETS = {
    "Opening Set (60min)": [
        {"track": "Ambient Intro", "artist": "TBD", "bpm": 116, "key": "Am", "energy": 2, "notes": "Atmospheric opener"},
        {"track": "Warm Groove", "artist": "TBD", "bpm": 118, "key": "Cm", "energy": 3, "notes": "Build the room"},
        {"track": "First Wave", "artist": "TBD", "bpm": 120, "key": "Dm", "energy": 4, "notes": "First energy push"},
        {"track": "Sustain", "artist": "TBD", "bpm": 122, "key": "Em", "energy": 4, "notes": "Hold the energy"},
        {"track": "Peak Tease", "artist": "TBD", "bpm": 124, "key": "Fm", "energy": 5, "notes": "Tease the peak"},
        {"track": "Gentle Close", "artist": "TBD", "bpm": 120, "key": "Am", "energy": 3, "notes": "Hand off to next DJ"},
    ],
    "Peak Time (90min)": [
        {"track": "Statement", "artist": "TBD", "bpm": 124, "key": "Am", "energy": 4, "notes": "Start with intent"},
        {"track": "Build", "artist": "TBD", "bpm": 126, "key": "Cm", "energy": 5, "notes": "Push up"},
        {"track": "Peak 1", "artist": "TBD", "bpm": 128, "key": "Dm", "energy": 7, "notes": "First peak"},
        {"track": "Breathe", "artist": "TBD", "bpm": 126, "key": "Em", "energy": 5, "notes": "Let them breathe"},
        {"track": "Peak 2", "artist": "TBD", "bpm": 130, "key": "Fm", "energy": 8, "notes": "Biggest moment"},
        {"track": "Sustain", "artist": "TBD", "bpm": 128, "key": "Gm", "energy": 7, "notes": "Keep it going"},
        {"track": "Cool Down", "artist": "TBD", "bpm": 124, "key": "Am", "energy": 5, "notes": "Ease back"},
        {"track": "Close", "artist": "TBD", "bpm": 122, "key": "Dm", "energy": 4, "notes": "Smooth close"},
    ],
    "After Hours (120min)": [
        {"track": "Deep Start", "artist": "TBD", "bpm": 118, "key": "Am", "energy": 2, "notes": "Minimal, hypnotic"},
        {"track": "Layers", "artist": "TBD", "bpm": 120, "key": "Cm", "energy": 3, "notes": "Add texture"},
        {"track": "Dark Build", "artist": "TBD", "bpm": 124, "key": "Dm", "energy": 5, "notes": "Underground vibe"},
        {"track": "Tension", "artist": "TBD", "bpm": 126, "key": "Fm", "energy": 6, "notes": "Dark peak"},
        {"track": "Release", "artist": "TBD", "bpm": 124, "key": "Gm", "energy": 4, "notes": "Breakdown"},
        {"track": "Rebuild", "artist": "TBD", "bpm": 126, "key": "Am", "energy": 6, "notes": "Second wave"},
        {"track": "Fade", "artist": "TBD", "bpm": 122, "key": "Dm", "energy": 3, "notes": "Wind down"},
        {"track": "Ambient Close", "artist": "TBD", "bpm": 118, "key": "Am", "energy": 1, "notes": "Lights up"},
    ],
}


def render():
    st.markdown("### Set Builder")
    st.caption("Plan your set. Visualize energy flow. Check harmonic compatibility.")

    if "set_tracks" not in st.session_state:
        st.session_state.set_tracks = []

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Build Your Set")

        with st.expander("Add Track", expanded=True):
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                track_name = st.text_input("Track", key="sb_track", placeholder="Track name")
                artist = st.text_input("Artist", key="sb_artist", placeholder="Artist")
            with tc2:
                bpm = st.number_input("BPM", 60, 200, 125, key="sb_bpm")
                key = st.selectbox("Key", ALL_KEYS, key="sb_key")
            with tc3:
                energy = st.slider("Energy (1-10)", 1, 10, 5, key="sb_energy")
                notes = st.text_input("Notes", key="sb_notes", placeholder="Transition notes...")

            if st.button("Add to Set", key="sb_add"):
                if track_name and artist:
                    st.session_state.set_tracks.append({
                        "track": track_name, "artist": artist,
                        "bpm": bpm, "key": key, "energy": energy, "notes": notes,
                    })
                    st.success(f"Added: {track_name}")
                    st.rerun()

        # Display current set
        tracks = st.session_state.set_tracks
        if tracks:
            st.markdown("#### Current Set")
            for i, t in enumerate(tracks):
                name = t["track"]
                art = t["artist"]
                b = t["bpm"]
                k = t["key"]
                e = t["energy"]
                n = t.get("notes", "")
                cam = ""
                if key_to_camelot:
                    cam = " [" + key_to_camelot(k) + "]"
                cols = st.columns([0.5, 3, 1, 1, 2, 0.5])
                cols[0].write(str(i + 1))
                cols[1].markdown("**" + name + "** -- " + art)
                cols[2].write(str(b) + " BPM")
                cols[3].write(k + cam)
                cols[4].progress(e / 10, text=str(e) + "/10")
                if cols[5].button("X", key="sb_rm_" + str(i)):
                    st.session_state.set_tracks.pop(i)
                    st.rerun()

            # Energy flow visualization
            st.markdown("#### Energy Flow")
            if HAS_PLOTLY:
                nums = list(range(1, len(tracks) + 1))
                energies = [t["energy"] for t in tracks]
                bpms = [t["bpm"] for t in tracks]
                labels = [t["track"] for t in tracks]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=nums, y=energies, mode="lines+markers",
                    name="Energy", text=labels,
                    line=dict(color="#FFC000", width=3),
                    marker=dict(size=10),
                ))
                fig.update_layout(
                    plot_bgcolor="#0a0a1a",
                    paper_bgcolor="#0a0a1a",
                    font_color="#e2e8f0",
                    xaxis_title="Track #",
                    yaxis_title="Energy",
                    yaxis=dict(range=[0, 11]),
                    height=300,
                    margin=dict(l=40, r=20, t=20, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)
                # BPM transition chart
                st.markdown("#### BPM Transitions")
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=nums, y=bpms, text=bpms,
                    marker_color="#a78bfa",
                    textposition="auto",
                ))
                fig2.update_layout(
                    plot_bgcolor="#0a0a1a",
                    paper_bgcolor="#0a0a1a",
                    font_color="#e2e8f0",
                    xaxis_title="Track #",
                    yaxis_title="BPM",
                    height=250,
                    margin=dict(l=40, r=20, t=20, b=40),
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                edata = pd.DataFrame({
                    "Track": range(1, len(tracks) + 1),
                    "Energy": [t["energy"] for t in tracks],
                    "BPM": [t["bpm"] for t in tracks],
                })
                st.line_chart(edata.set_index("Track")["Energy"], height=200)

            # Key compatibility check
            st.markdown("#### Harmonic Compatibility")
            violations = []
            for idx in range(1, len(tracks)):
                prev = tracks[idx - 1]
                curr = tracks[idx]
                ediff = curr["energy"] - prev["energy"]
                bdiff = abs(curr["bpm"] - prev["bpm"])
                if ediff > 2:
                    violations.append("Track " + str(idx+1) + ": Energy jump +" + str(ediff) + " (max +2)")
                if ediff < -1:
                    violations.append("Track " + str(idx+1) + ": Energy drop " + str(ediff) + " (max -1)")
                if bdiff > 8:
                    violations.append("Track " + str(idx+1) + ": BPM jump " + str(bdiff) + " (max 8)")
                if are_keys_compatible:
                    pk = prev["key"]
                    ck = curr["key"]
                    if not are_keys_compatible(pk, ck):
                        msg = "Track " + str(idx+1) + ": Key clash"
                        violations.append(msg)
            e0 = tracks[0]["energy"]
            if e0 > 3:
                violations.append("Track 1: Opening energy too high")
            if violations:
                for v in violations:
                    st.warning(v)
            else:
                st.success("Flow and harmonic compatibility look clean.")

            # Set duration calculator
            avg_len = 5.5  # minutes per track avg
            total_min = len(tracks) * avg_len
            hrs = int(total_min // 60)
            mins = int(total_min % 60)
            dur_str = str(hrs) + "h " + str(mins) + "m" if hrs else str(mins) + " min"
            st.metric("Est. Set Duration", dur_str, str(len(tracks)) + " tracks")

            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                if chat and st.button("AI Suggestions", key="sb_ai"):
                    with st.spinner("Analyzing set..."):
                        stxt = str(tracks)
                        r = chat(SET_PROMPT, [{"role":"user","content":stxt}])
                        st.markdown(r)
            with ac2:
                if st.button("Clear Set", key="sb_clear"):
                    st.session_state.set_tracks = []
                    st.rerun()
            with ac3:
                exp = "SET LIST\n"
                for idx, tr in enumerate(tracks):
                    exp += str(idx+1) + ". " + tr["track"] + "\n"
                st.download_button("Export", exp, "setlist.md", key="sb_exp")

        else:
            st.info("Add tracks to start building your set.")

    with col2:
        st.markdown("#### Set Presets")
        for pname, ptracks in PRESETS.items():
            if st.button("Load: " + pname, key="sb_p_" + pname[:8]):
                st.session_state.set_tracks = list(ptracks)
                st.rerun()

        st.markdown("---")
        st.markdown("#### Key Reference")
        st.markdown("Camelot Wheel: compatible keys for smooth mixing")
        st.markdown("- Same number: A/B swap (energy shift)")
        st.markdown("- +/- 1 same letter (pitch shift)")
        st.markdown("- Example: 8A (Am) compatible with 8B (C), 7A (Dm), 9A (Em)")
