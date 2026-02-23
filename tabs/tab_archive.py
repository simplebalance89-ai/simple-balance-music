"""Tab 8: Jimmy's Mix Archive — Catalog, tag, search 18+ archived mixes."""

import streamlit as st
from utils.ai_client import chat

# Jimmy's 18 archived mixes
JIMMY_MIXES = [
    {"title": "AUG 25 Stream", "filename": "J.A.W.-AUG 25 Stream.mp3", "tags": ["stream", "live"], "energy_avg": 4, "mood": "Driving"},
    {"title": "Back Pain", "filename": "J.A.W.-Back Pain.mp3", "tags": ["personal", "grind"], "energy_avg": 3, "mood": "Deep"},
    {"title": "Crazy Storm", "filename": "J.A.W.-Crazy Storm.mp3", "tags": ["intense", "weather"], "energy_avg": 5, "mood": "Euphoric"},
    {"title": "Final Headgear", "filename": "J.A.W.-Final Headgear.mp3", "tags": ["headphones", "late-night"], "energy_avg": 4, "mood": "Dark"},
    {"title": "Here with you guys", "filename": "J.A.W.-Here with you guys(1).mp3", "tags": ["community", "grateful"], "energy_avg": 3, "mood": "Emotional"},
    {"title": "Let me think", "filename": "J.A.W.-Let me think.mp3", "tags": ["contemplative", "deep"], "energy_avg": 3, "mood": "Deep"},
    {"title": "Letting it Go", "filename": "J.A.W.-Letting it Go.mp3", "tags": ["release", "cathartic"], "energy_avg": 4, "mood": "Emotional"},
    {"title": "Little Behind", "filename": "J.A.W.-Little Behind.mp3", "tags": ["chill", "catch-up"], "energy_avg": 2, "mood": "Chill"},
    {"title": "Mommy Night out", "filename": "J.A.W.-Mommy Night out.mp3", "tags": ["jenna", "night-out"], "energy_avg": 4, "mood": "Driving"},
    {"title": "No More pacifier", "filename": "J.A.W.-No More pacifier.mp3", "tags": ["kids", "milestone"], "energy_avg": 3, "mood": "Deep"},
    {"title": "Prince of Darkness", "filename": "J.A.W.-Prince of Darkness.mp3", "tags": ["dark", "underground"], "energy_avg": 5, "mood": "Dark"},
    {"title": "Rainy afternoons", "filename": "J.A.W.-Rainy afternoons.mp3", "tags": ["weather", "mood", "chill"], "energy_avg": 2, "mood": "Chill"},
    {"title": "REAL AMERICAN", "filename": "J.A.W.-REAL AMERICAN.mp3", "tags": ["patriotic", "bold"], "energy_avg": 5, "mood": "Euphoric"},
    {"title": "So Daddy", "filename": "J.A.W.-So Daddy.mp3", "tags": ["kids", "family"], "energy_avg": 3, "mood": "Emotional"},
    {"title": "Thanks for having me", "filename": "J.A.W.-Thanks for having me.mp3", "tags": ["grateful", "closer"], "energy_avg": 3, "mood": "Emotional"},
    {"title": "Werid Crowd", "filename": "J.A.W.-Werid Crowd.mp3", "tags": ["crowd", "eclectic"], "energy_avg": 4, "mood": "Driving"},
]

ARCHIVE_PROMPT = """You are the J.A.W. Mix Archive assistant. You help Peter search and explore Jimmy's 18 archived DJ mixes.

JIMMY'S MIXES:
""" + "\n".join(f"- {m['title']} (Energy: {m['energy_avg']}/6, Mood: {m['mood']}, Tags: {', '.join(m['tags'])})" for m in JIMMY_MIXES) + """

JIMMY CONTEXT:
- VJ Wilson. J.A.W. DJs through headphones (kids in the house).
- Liam (3) and Logan (2) — hence headphone sessions.
- Each mix title tells a story of what was happening in Jimmy's life when he recorded it.
- NF is Jimmy's boy. Papa Roach is to Jimmy what MGK is to Peter.

Help Peter find specific mixes, understand the story behind them, or suggest which mix fits a mood."""


def render():
    st.markdown("### Jimmy's Mix Archive")
    st.caption(f"J.A.W. Collection — {len(JIMMY_MIXES)} mixes. VJ Wilson through headphones.")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("#### Filter")
        mood_filter = st.multiselect("Mood", ["Chill", "Deep", "Driving", "Euphoric", "Dark", "Emotional"],
                                      key="arch_mood")
        energy_range = st.slider("Energy Range", 1, 6, (1, 6), key="arch_energy")
        search_text = st.text_input("Search", key="arch_search", placeholder="Search title or tags...")

        # Filter mixes
        filtered = JIMMY_MIXES.copy()
        if mood_filter:
            filtered = [m for m in filtered if m["mood"] in mood_filter]
        if energy_range != (1, 6):
            filtered = [m for m in filtered if energy_range[0] <= m["energy_avg"] <= energy_range[1]]
        if search_text:
            search_lower = search_text.lower()
            filtered = [m for m in filtered if
                       search_lower in m["title"].lower() or
                       any(search_lower in t for t in m["tags"])]

        st.markdown(f"**{len(filtered)}/{len(JIMMY_MIXES)}** mixes shown")

        st.markdown("---")
        st.markdown("#### Stats")
        moods = {}
        for m in JIMMY_MIXES:
            moods[m["mood"]] = moods.get(m["mood"], 0) + 1
        for mood, count in sorted(moods.items(), key=lambda x: -x[1]):
            st.markdown(f"- **{mood}:** {count} mixes")

        avg_energy = sum(m["energy_avg"] for m in JIMMY_MIXES) / len(JIMMY_MIXES)
        st.metric("Average Energy", f"{avg_energy:.1f}/6")

    with col1:
        st.markdown("#### Mix Collection")

        for m in filtered:
            energy_bar = "█" * m["energy_avg"] + "░" * (6 - m["energy_avg"])
            tags_str = " ".join(f"`{t}`" for t in m["tags"])

            with st.expander(f"**{m['title']}** — {m['mood']} | {energy_bar} {m['energy_avg']}/6"):
                st.markdown(f"""
**File:** `{m['filename']}`
**Mood:** {m['mood']}
**Energy:** {energy_bar} {m['energy_avg']}/6
**Tags:** {tags_str}
""")

        st.markdown("---")

        # AI search
        chat_key = "archive_messages"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        st.markdown("#### Ask About the Archive")
        if prompt := st.chat_input("Find the mix with that Brunello track...", key="arch_input"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})

            with st.spinner("Searching archive..."):
                reply = chat(ARCHIVE_PROMPT, st.session_state[chat_key])
                st.markdown(reply)
                st.session_state[chat_key].append({"role": "assistant", "content": reply})
