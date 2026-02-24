"""Tab 8: Mix Archive -- Catalog, search, analyze J.A.W. mixes."""

import streamlit as st
import os

try:
    from utils.audio_engine import analyze_audio, get_waveform_data
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

try:
    from utils.ai_client import chat
except ImportError:
    chat = None


JIMMY_MIXES = [
    {"title": "AUG 25 Stream", "filename": "J.A.W.-AUG 25 Stream.mp3", "tags": ["house", "stream"], "energy": 4, "mood": "Driving", "bpm_range": "120-128", "year": "2025"},
    {"title": "Back Pain", "filename": "J.A.W.-Back Pain.mp3", "tags": ["deep", "melodic"], "energy": 3, "mood": "Deep", "bpm_range": "118-124", "year": "2025"},
    {"title": "Crazy Storm", "filename": "J.A.W.-Crazy Storm.mp3", "tags": ["progressive", "peak"], "energy": 5, "mood": "Euphoric", "bpm_range": "124-132", "year": "2025"},
    {"title": "Final Headgear", "filename": "J.A.W.-Final Headgear.mp3", "tags": ["techno", "dark"], "energy": 4, "mood": "Dark", "bpm_range": "122-130", "year": "2025"},
    {"title": "Here with you guys", "filename": "J.A.W.-Here with you guys(1).mp3", "tags": ["melodic", "emotional"], "energy": 3, "mood": "Emotional", "bpm_range": "118-126", "year": "2025"},
    {"title": "Let me think", "filename": "J.A.W.-Let me think.mp3", "tags": ["deep", "minimal"], "energy": 3, "mood": "Deep", "bpm_range": "116-124", "year": "2025"},
    {"title": "Letting it Go", "filename": "J.A.W.-Letting it Go.mp3", "tags": ["melodic", "progressive"], "energy": 4, "mood": "Emotional", "bpm_range": "120-128", "year": "2025"},
    {"title": "Little Behind", "filename": "J.A.W.-Little Behind.mp3", "tags": ["chill", "ambient"], "energy": 2, "mood": "Chill", "bpm_range": "112-120", "year": "2025"},
    {"title": "Mommy Night out", "filename": "J.A.W.-Mommy Night out.mp3", "tags": ["house", "driving"], "energy": 4, "mood": "Driving", "bpm_range": "122-130", "year": "2025"},
    {"title": "No More pacifier", "filename": "J.A.W.-No More pacifier.mp3", "tags": ["deep", "house"], "energy": 3, "mood": "Deep", "bpm_range": "118-126", "year": "2025"},
    {"title": "Prince of Darkness", "filename": "J.A.W.-Prince of Darkness.mp3", "tags": ["dark", "techno"], "energy": 5, "mood": "Dark", "bpm_range": "126-134", "year": "2025"},
    {"title": "Rainy afternoons", "filename": "J.A.W.-Rainy afternoons.mp3", "tags": ["chill", "ambient", "downtempo"], "energy": 2, "mood": "Chill", "bpm_range": "110-118", "year": "2025"},
    {"title": "REAL AMERICAN", "filename": "J.A.W.-REAL AMERICAN.mp3", "tags": ["progressive", "euphoric"], "energy": 5, "mood": "Euphoric", "bpm_range": "126-136", "year": "2025"},
    {"title": "So Daddy", "filename": "J.A.W.-So Daddy.mp3", "tags": ["melodic", "emotional"], "energy": 3, "mood": "Emotional", "bpm_range": "118-124", "year": "2025"},
    {"title": "Thanks for having me", "filename": "J.A.W.-Thanks for having me.mp3", "tags": ["melodic", "emotional"], "energy": 3, "mood": "Emotional", "bpm_range": "116-124", "year": "2025"},
    {"title": "Werid Crowd", "filename": "J.A.W.-Werid Crowd.mp3", "tags": ["house", "driving"], "energy": 4, "mood": "Driving", "bpm_range": "122-130", "year": "2025"},
]

ARCHIVE_PROMPT = (
    "You are the J.A.W. Mix Archive assistant. Help search and explore "
    "Jimmy's archived DJ mixes. Jimmy (VJ Wilson) DJs through headphones "
    "because Liam (3) and Logan (2) are sleeping. Each mix title tells "
    "a story of what was happening in his life when he recorded it."
)


def render():
    st.markdown("### Mix Archive")
    st.caption("J.A.W. Collection -- " + str(len(JIMMY_MIXES)) + " mixes. VJ Wilson through headphones.")

    # Initialize comments storage
    if "mix_comments" not in st.session_state:
        st.session_state.mix_comments = {}

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("#### Filters")
        mood_filter = st.multiselect(
            "Mood", ["Chill", "Deep", "Driving", "Euphoric", "Dark", "Emotional"],
            key="arch_mood",
        )
        energy_range = st.slider("Energy Range", 1, 6, (1, 6), key="arch_energy")
        search_text = st.text_input("Search", key="arch_search", placeholder="Title or tags...")

        # Apply filters
        filtered = list(JIMMY_MIXES)
        if mood_filter:
            filtered = [m for m in filtered if m["mood"] in mood_filter]
        if energy_range != (1, 6):
            lo, hi = energy_range
            filtered = [m for m in filtered if lo <= m["energy"] <= hi]
        if search_text:
            q = search_text.lower()
            filtered = [m for m in filtered if q in m["title"].lower() or any(q in t for t in m["tags"])]

        st.metric("Showing", str(len(filtered)) + "/" + str(len(JIMMY_MIXES)))

        st.markdown("---")
        st.markdown("#### Stats")
        moods = {}
        for m in JIMMY_MIXES:
            md = m["mood"]
            moods[md] = moods.get(md, 0) + 1
        for mood, count in sorted(moods.items(), key=lambda x: -x[1]):
            st.markdown("- **" + mood + ":** " + str(count) + " mixes")
        avg_e = sum(m["energy"] for m in JIMMY_MIXES) / len(JIMMY_MIXES)
        st.metric("Average Energy", str(round(avg_e, 1)) + "/6")

        st.markdown("---")
        st.markdown("#### Analyze Mix")
        uploaded = st.file_uploader("Upload mix audio", type=["mp3","wav","flac"], key="arch_upload")
        if uploaded and HAS_AUDIO:
            if st.button("Analyze", key="arch_analyze"):
                with st.spinner("Analyzing audio..."):
                    data = uploaded.read()
                    result = analyze_audio(data)
                    if "error" not in result:
                        st.write("BPM: " + str(result.get("bpm", "?")))
                        st.write("Key: " + str(result.get("key", "?")))
                        st.write("Loudness: " + str(result.get("rms_db", "?")) + " dB")
                        st.write("Duration: " + str(result.get("duration", "?")) + "s")
                    else:
                        st.error(result["error"])
        elif uploaded and not HAS_AUDIO:
            st.info("Install librosa for audio analysis.")

    with col1:
        st.markdown("#### Mix Collection")
        for m in filtered:
            title = m["title"]
            mood = m["mood"]
            with st.expander(title):
                st.write(m)
                # Audio playback if file exists locally
                fpath = os.path.join("mixes", m["filename"])
                if os.path.exists(fpath):
                    st.audio(fpath)
                # Comments
                ckey = "comment_" + m["filename"]
                cur = st.session_state.mix_comments.get(ckey, "")
                note = st.text_area("Notes", value=cur, key=ckey)
                st.session_state.mix_comments[ckey] = note

        st.markdown("---")
        if chat:
            st.markdown("#### Ask About the Archive")
            ck = "archive_messages"
            if ck not in st.session_state:
                st.session_state[ck] = []
            for msg in st.session_state[ck]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if prompt := st.chat_input("Search the archive...", key="arch_input"):
                st.session_state[ck].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Searching..."):
                        r = chat(ARCHIVE_PROMPT, st.session_state[ck])
                        st.markdown(r)
                        st.session_state[ck].append({"role": "assistant", "content": r})
