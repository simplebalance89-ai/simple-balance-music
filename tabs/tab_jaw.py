"""Tab 1: J.A.W. DJ Command — Energy flow, set building, track suggestions."""

import streamlit as st
from utils.ai_client import chat
from utils.apis import search_beatport

JAW_SYSTEM_PROMPT = """You are the J.A.W. Music GPT — Simple Balance DJ System. You are Peter and Jimmy's DJ advisor, track curator, and energy flow guardian.

Music is how the brothers communicate. This isn't entertainment — it's language.

YOUR JOB:
1. Help select tracks for sets, moods, and moments
2. Maintain energy flow across a session
3. Protect the floor from energy crashes
4. Remember what works and what doesn't

ENERGY FLOW RULES (NON-NEGOTIABLE):
- Max energy jump: +2 levels per track (HARD STOP)
- Max energy drop: -1 level per track (WARN unless intentional cooldown)
- Peak duration: 3-5 tracks max (FLAG after 5)
- Opening energy: 2-3 max (HARD STOP)
- Closer energy: 4-5 target

BPM RULES:
- Max BPM jump: ±8 BPM (WARN)
- Max BPM jump with harmonic mix: ±15 BPM (ALLOW if key-matched)
- Genre shift: Requires 2-track bridge

REPETITION RULES:
- Same artist: Min 5 tracks apart (HARD STOP)
- Same track: Once per set (HARD STOP)
- Same key: Max 3 consecutive (WARN)

ENERGY SCALE:
1 ░░░░░░░░░░ Ambient — Meditation, stillness
2 ██░░░░░░░░ Chill — Background, conversation-friendly
3 ████░░░░░░ Warm — Opening, bodies start moving
4 ██████░░░░ Build — Anticipation, hands up
5 ████████░░ Peak — Dance floor locked in
6 ██████████ Full Send — Release, euphoria, arms in the air

SET TEMPLATES:
Standard 2-Hour: Open (2-3) → Build (3-4) → Peak (5-6) → Sustain (4-5) → Close (3-4)
Journey (Emotional Arc): Ground (2) → Rise (3-4) → Release (5) → Breathe (3) → Anticipate (4-5) → Transcend (6) → Land (3-2)
Chill Session: Energy 2-3 throughout, BPM 90-115

MOOD PROFILES:
| Mood | Energy | BPM | Characteristics |
|------|--------|-----|-----------------|
| Chill | 1-3 | 80-110 | Warm pads, soft percussion, space |
| Deep | 3-4 | 118-124 | Hypnotic, rolling, minimal drops |
| Driving | 4-5 | 125-132 | Relentless, forward motion, bass |
| Euphoric | 5-6 | 128-138 | Builds, releases, hands up |
| Dark | 4-6 | 130-145 | Tension, industrial, underground |
| Emotional | 3-5 | 115-130 | Vocals, melody, heart open |

TRACK SUGGESTION FORMAT:
```
TRACK SUGGESTION
━━━━━━━━━━━━━━━━━━━
Track:    [Title]
Artist:   [Name]
BPM:      [XXX]
Key:      [X major/minor]
Energy:   [████░░░░░░] X/6
Mood:     [Tag]
Why:      [1-2 sentence reason]
Mix Note: [Transition tip]
━━━━━━━━━━━━━━━━━━━
```

ENERGY ALERT FORMAT (use when rules violated):
```
⚠️ ENERGY ALERT
━━━━━━━━━━━━━━━
Issue:      [Description]
Current:    Energy [X], BPM [XXX]
Risk:       [What could go wrong]
Suggestion: [How to fix]
```

KEY ARTISTS PETER VIBES WITH:
- Afterlife label (Colyn, Tale of Us)
- Upercent (Valencia, dark controlled chaos)
- Township Rebellion (melodic, emotional)
- Glowal (the Sinton.ia origin artist)
- Brunello (Lost In The Mellow Circus, Ghost Dance)
- Lane 8 / This Never Happened label
- Tim Engelhardt (Reality — the Asylum Hawaii bomb)
- Philip Bader (Crazy — Moon Harbour decompression)

PROHIBITED:
- Never crash from 5-6 to 1-2 without warning
- Never repeat artist within 5 tracks
- Never open above energy 3
- Never stack 6+ peak tracks without suggesting a valley
- Never ignore a genre shift — always bridge

The best sets aren't remembered for the bangers. They're remembered for how they made people feel.

— J.A.W. / Simple Balance"""


def render():
    st.markdown("### J.A.W. DJ Command")
    st.caption("Energy flow guardian. Track curator. Set builder.")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("#### Quick Tools")

        # Beatport Search
        with st.expander("Beatport Search", expanded=False):
            query = st.text_input("Search tracks", key="bp_search", placeholder="Artist, track, or genre...")
            bpm_range = st.slider("BPM Range", 80, 160, (118, 135), key="bp_bpm")
            if st.button("Search Beatport", key="bp_go"):
                results = search_beatport(query, bpm_min=bpm_range[0], bpm_max=bpm_range[1])
                for t in results:
                    energy_bar = "█" * t.get("energy", 3) + "░" * (6 - t.get("energy", 3))
                    st.markdown(f"""
**{t['title']}** — {t['artist']}
`{t.get('bpm', '?')} BPM` `{t.get('key', '?')}` `{energy_bar} {t.get('energy', '?')}/6`
*{t.get('label', '')} — {t.get('genre', '')}*
---""")

        # Harmonic Mixer
        with st.expander("Harmonic Key Checker", expanded=False):
            key_options = ["Am", "Bm", "Cm", "Dm", "Em", "Fm", "Gm",
                          "A", "B", "C", "D", "E", "F", "G",
                          "Abm", "Bbm", "Ebm", "F#m",
                          "Ab", "Bb", "Eb", "F#"]
            current_key = st.selectbox("Current track key", key_options, key="hk_current")
            next_key = st.selectbox("Next track key", key_options, key="hk_next")

            # Camelot wheel compatibility
            camelot = {
                "Ab": "4B", "Abm": "4A", "A": "11B", "Am": "8A",
                "Bb": "6B", "Bbm": "1A", "B": "1B", "Bm": "10A",
                "C": "8B", "Cm": "5A", "D": "10B", "Dm": "7A",
                "Eb": "5B", "Ebm": "2A", "E": "12B", "Em": "9A",
                "F": "7B", "Fm": "4A", "F#": "2B", "F#m": "11A",
                "G": "9B", "Gm": "6A",
            }
            if st.button("Check Compatibility", key="hk_check"):
                c1 = camelot.get(current_key, "?")
                c2 = camelot.get(next_key, "?")
                if c1 != "?" and c2 != "?":
                    n1, l1 = int(c1[:-1]), c1[-1]
                    n2, l2 = int(c2[:-1]), c2[-1]
                    compatible = (
                        (n1 == n2 and l1 == l2) or  # Same key
                        (n1 == n2 and l1 != l2) or  # Relative major/minor
                        (abs(n1 - n2) == 1 or abs(n1 - n2) == 11) and l1 == l2  # Adjacent
                    )
                    if compatible:
                        st.success(f"**Compatible!** {current_key} ({c1}) → {next_key} ({c2})")
                    else:
                        st.warning(f"**Risky mix.** {current_key} ({c1}) → {next_key} ({c2}) — Consider a bridge track.")

        # Energy Scale Reference
        with st.expander("Energy Scale", expanded=False):
            st.markdown("""
```
1 ░░░░░░░░░░ Ambient
2 ██░░░░░░░░ Chill
3 ████░░░░░░ Warm
4 ██████░░░░ Build
5 ████████░░ Peak
6 ██████████ Full Send
```

**Templates:**
- **Standard 2hr:** 2→3→4→5→6→5→4→3
- **Journey:** 2→3→4→5→3→4→5→6→3→2
- **Chill:** 2→3 throughout
""")

    with col1:
        # Chat interface
        chat_key = "jaw_messages"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state[chat_key]:
            with st.chat_message("assistant"):
                st.markdown("**J.A.W. Music** ready. I'm your DJ advisor and energy flow guardian. Say **demo** for a walkthrough, or tell me the vibe.")

        if prompt := st.chat_input("Describe the vibe, or type 'demo'...", key="jaw_input"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Curating..."):
                    reply = chat(JAW_SYSTEM_PROMPT, st.session_state[chat_key])
                    st.markdown(reply)
                    st.session_state[chat_key].append({"role": "assistant", "content": reply})
