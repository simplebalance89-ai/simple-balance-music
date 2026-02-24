"""Tab 10: Dashboard -- Session stats, API status, mau5trap submission checklist."""

import streamlit as st
from datetime import datetime


def render():
    st.markdown("### Dashboard")
    st.caption("Session stats. API status. mau5trap submission checklist.")

    # Session stats
    s = st.session_state.get("stats", {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Queries", s.get("total_queries", 0))
    tok_in = s.get("total_tokens_in", 0)
    tok_out = s.get("total_tokens_out", 0)
    m2.metric("Tokens Used", str(tok_in + tok_out))
    n_tracks = len(st.session_state.get("set_tracks", []))
    m3.metric("Set Tracks", n_tracks)
    m4.metric("Mixes Archived", "18")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        # mau5trap Submission Checklist
        st.markdown("#### mau5trap Submission Checklist")
        if "checklist" not in st.session_state:
            st.session_state.checklist = {
                "headroom": False,
                "mastered": False,
                "clip": False,
                "info": False,
                "submitted": False,
            }

        cl = st.session_state.checklist
        cl["headroom"] = st.checkbox("Track mixed to -6dB headroom", value=cl["headroom"], key="cl_head")
        cl["mastered"] = st.checkbox("Mastered to streaming specs (-14 LUFS)", value=cl["mastered"], key="cl_master")
        cl["clip"] = st.checkbox("Best 20-second clip identified", value=cl["clip"], key="cl_clip")
        cl["info"] = st.checkbox("Track info filled (title, BPM, key, genre)", value=cl["info"], key="cl_info")
        cl["submitted"] = st.checkbox("Submitted via demos@mau5trap.com or LabelRadar", value=cl["submitted"], key="cl_sub")

        done = sum(1 for v in cl.values() if v)
        total = len(cl)
        st.progress(done / total, text=str(done) + "/" + str(total) + " complete")
        if done == total:
            st.success("Ready to submit to mau5trap!")
        st.markdown("**Submit via:** demos@mau5trap.com or [LabelRadar](https://www.labelradar.com)")

        st.markdown("---")
        # Activity feed
        st.markdown("#### Recent Activity")
        if "activity_feed" not in st.session_state:
            st.session_state.activity_feed = [
                "Platform launched -- Simple Balance Music AI Command Center is live.",
                "18 J.A.W. mixes archived and tagged. Full catalog searchable.",
                "MIDI generators online -- chord, drum, and bass patterns.",
                "mau5trap submission checklist activated.",
            ]
        for item in st.session_state.activity_feed:
            st.markdown("- " + item)

        st.markdown("---")
        # Quick links
        st.markdown("#### Quick Links")
        links = [
            ("Tab 1", "J.A.W. DJ Command"),
            ("Tab 2", "Music Discovery"),
            ("Tab 3", "AI Mastering Studio"),
            ("Tab 4", "Stem Separation Lab"),
            ("Tab 5", "AI Music Generation"),
            ("Tab 6", "Festival & Events Radar"),
            ("Tab 7", "Set Builder"),
            ("Tab 8", "Mix Archive"),
            ("Tab 9", "Producer Tools"),
        ]
        qcols = st.columns(3)
        for i, (num, name) in enumerate(links):
            qcols[i % 3].markdown("**" + num + ":** " + name)

    with col2:
        # API Status
        st.markdown("#### API Status")
        apis = {
            "Azure OpenAI": bool(st.secrets.get("AZURE_OPENAI_KEY", "")),
            "Replicate": bool(st.secrets.get("REPLICATE_API_TOKEN", "")),
            "Dolby.io": bool(st.secrets.get("DOLBY_API_KEY", "")),
            "Last.fm": bool(st.secrets.get("LASTFM_API_KEY", "")),
            "EDMTrain": bool(st.secrets.get("EDMTRAIN_API_KEY", "")),
            "Bandsintown": bool(st.secrets.get("BANDSINTOWN_APP_ID", "")),
        }
        for api_name, connected in apis.items():
            if connected:
                st.success(api_name + ": Connected")
            else:
                st.warning(api_name + ": Demo Mode")

