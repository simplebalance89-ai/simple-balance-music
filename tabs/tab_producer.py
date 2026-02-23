"""Tab 9: Producer Tools — Sample search, chord progressions, reference analysis."""

import streamlit as st
from utils.ai_client import chat

PRODUCER_PROMPT = """You are a music production assistant for Simple Balance. You help with:
1. Chord progressions — suggest progressions by mood/genre
2. Song structure — arrangement advice
3. Reference track analysis — break down what makes a track work
4. Sound design tips — synthesis, layering, processing
5. Remix workflow — how to approach a remix from stems

Keep it practical. Peter and Jimmy are DJs transitioning into production. Speak their language."""


CHORD_PROGRESSIONS = {
    "Emotional / Melodic": [
        ("i - VI - III - VII", "Am - F - C - G", "Classic emotional progression. Lane 8, Township Rebellion."),
        ("i - iv - VI - V", "Am - Dm - F - E", "Tension and release. Afterlife sound."),
        ("i - III - VII - IV", "Am - C - G - D", "Uplifting with forward motion."),
    ],
    "Dark / Driving": [
        ("i - VII - VI - VII", "Am - G - F - G", "Minimal, hypnotic. Upercent territory."),
        ("i - iv - v - i", "Am - Dm - Em - Am", "Dark loop. Underground techno."),
        ("i - bVI - bVII - i", "Am - F - G - Am", "Moody, cinematic tension."),
    ],
    "Deep / Groovy": [
        ("ii - V - I - vi", "Dm - G - C - Am", "Jazz-influenced deep house."),
        ("I - vi - IV - V", "C - Am - F - G", "Classic feel-good. Works every time."),
        ("i - iv - i - VII", "Am - Dm - Am - G", "Rolling deep house groove."),
    ],
    "Euphoric / Big Room": [
        ("VI - VII - i - i", "F - G - Am - Am", "The EDM anthem progression."),
        ("I - V - vi - IV", "C - G - Am - F", "Euphoric build. Festival territory."),
        ("vi - IV - I - V", "Am - F - C - G", "Emotional build to release."),
    ],
}


def render():
    st.markdown("### Producer Tools")
    st.caption("Chord progressions. Reference analysis. Sample search. Remix workflow.")

    tab_chords, tab_reference, tab_samples, tab_chat = st.tabs([
        "Chord Progressions", "Reference Analyzer", "Sample Search", "Production AI"
    ])

    with tab_chords:
        st.markdown("#### Chord Progression Generator")

        mood = st.selectbox("Mood / Style", list(CHORD_PROGRESSIONS.keys()), key="prod_mood")

        progressions = CHORD_PROGRESSIONS[mood]
        for roman, chords, desc in progressions:
            st.markdown(f"""
---
**{roman}**
`{chords}`
*{desc}*
""")

        st.markdown("---")
        st.markdown("#### Custom Progression")
        custom_key = st.selectbox("Root Key", ["C", "D", "E", "F", "G", "A", "B",
                                                "Cm", "Dm", "Em", "Fm", "Gm", "Am", "Bm"],
                                   key="prod_custom_key")
        custom_mood = st.text_input("Describe the feeling", key="prod_custom_mood",
                                     placeholder="Dark and hypnotic with a build...")

        if st.button("Generate Progression", key="prod_gen") and custom_mood:
            with st.spinner("Generating..."):
                prompt = f"Generate 3 chord progressions in {custom_key} that feel '{custom_mood}'. For each, show roman numerals, actual chords, and a 1-line description of the vibe."
                reply = chat(PRODUCER_PROMPT, [{"role": "user", "content": prompt}])
                st.markdown(reply)

    with tab_reference:
        st.markdown("#### Reference Track Analyzer")
        st.markdown("Paste a track name and get a breakdown of what makes it work.")

        ref_track = st.text_input("Track name", key="prod_ref_track",
                                   placeholder="e.g. Colyn - Oxygen Levels Low")

        if st.button("Analyze", key="prod_ref_go") and ref_track:
            with st.spinner("Analyzing..."):
                prompt = f"""Analyze this reference track for production insights: "{ref_track}"

Break down:
1. Estimated BPM and Key
2. Energy profile (opening, peak, cooldown)
3. Arrangement structure (intro, breakdown, drop, outro)
4. Sound design elements (bass, leads, pads, percussion)
5. Mix characteristics (stereo width, frequency balance)
6. What makes this track work — the secret sauce
7. How to achieve a similar feel in production"""
                reply = chat(PRODUCER_PROMPT, [{"role": "user", "content": prompt}])
                st.markdown(reply)

    with tab_samples:
        st.markdown("#### Sample Search")
        st.info("**Phase 2** — Freesound API integration for royalty-free sample search.")

        sample_query = st.text_input("Search samples", key="prod_sample_q",
                                      placeholder="e.g. vinyl crackle, sub bass hit, vocal chop...")
        sample_type = st.multiselect("Type", ["One-Shot", "Loop", "Atmosphere", "Foley", "Vocal"],
                                      key="prod_sample_type")

        if st.button("Search", key="prod_sample_go"):
            st.info("Connect Freesound API for real sample search results.")

        st.markdown("---")
        st.markdown("#### Quick Sample Packs")
        packs = {
            "Melodic House Essentials": "Pads, arps, soft percussion, vinyl textures",
            "Dark Techno Toolkit": "Industrial hits, metallic textures, distorted kicks",
            "Vocal Chops": "Processed vocal stabs, whispers, shouts",
            "Organic Percussion": "Congas, bongos, shakers, tribal elements",
        }
        for name, desc in packs.items():
            st.markdown(f"**{name}** — {desc}")

    with tab_chat:
        st.markdown("#### Production AI")

        chat_key = "producer_messages"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state[chat_key]:
            with st.chat_message("assistant"):
                st.markdown("**Producer Tools** ready. Ask about sound design, arrangement, mixing, or production workflow.")

        if prompt := st.chat_input("Ask about production...", key="prod_input"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = chat(PRODUCER_PROMPT, st.session_state[chat_key])
                    st.markdown(reply)
                    st.session_state[chat_key].append({"role": "assistant", "content": reply})
