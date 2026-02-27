"""Tab 6: Festival & Events Radar."""

import streamlit as st
from datetime import datetime, timedelta

try:
    from utils.apis import get_edmtrain_events, get_bandsintown_events
except ImportError:
    get_edmtrain_events = None
    get_bandsintown_events = None

try:
    from utils.ai_client import chat
except ImportError:
    chat = None


MAU5TRAP_ROSTER = [
    "deadmau5",
    "REZZ",
    "No Mana",
    "BlackGummy",
    "Attlas",
    "Notaker",
    "Rinzen",
    "Morgin Madison",
    "Lamorn",
    "Bensley",
    "i_o",
    "Tommy Trash",
    "Feed Me",
    "Grabbitz",
    "Matt Lange",
    "PEEKABOO",
    "Gallya",
    "Speaker Honey",
    "Sian",
    "HNTR",
]

FESTIVALS_2026 = [
    {"name": "Ultra Music Festival", "city": "Miami", "date": "Mar 27-29, 2026", "genre": "EDM / House / Techno", "website": "https://ultramusicfestival.com"},
    {"name": "Coachella", "city": "LA", "date": "Apr 10-12 & Apr 17-19, 2026", "genre": "Multi-genre", "website": "https://coachella.com"},
    {"name": "EDC Las Vegas", "city": "Las Vegas", "date": "May 15-17, 2026", "genre": "EDM / Trance / Bass", "website": "https://lasvegas.electricdaisycarnival.com"},
    {"name": "Movement Detroit", "city": "Detroit", "date": "May 23-25, 2026", "genre": "Techno / House", "website": "https://movement.us"},
    {"name": "Sonar Barcelona", "city": "Barcelona", "date": "Jun 18-20, 2026", "genre": "Electronic / Experimental", "website": "https://sonar.es"},
    {"name": "Tomorrowland", "city": "Belgium", "date": "Jul 17-19 & Jul 24-26, 2026", "genre": "EDM / House / Techno", "website": "https://tomorrowland.com"},
    {"name": "ADE", "city": "Amsterdam", "date": "Oct 14-18, 2026", "genre": "Electronic", "website": "https://amsterdam-dance-event.nl"},
    {"name": "III Points", "city": "Miami", "date": "Oct 2026 (TBA)", "genre": "Electronic / Indie", "website": "https://iiipoints.com"},
    {"name": "Awakenings", "city": "Amsterdam", "date": "Jun-Jul 2026", "genre": "Techno", "website": "https://awakenings.com"},
    {"name": "Time Warp", "city": "Mannheim", "date": "Apr 4-5, 2026", "genre": "Techno / House", "website": "https://time-warp.de"},
    {"name": "Drumcode Festival", "city": "Amsterdam", "date": "Aug 2026 (TBA)", "genre": "Techno", "website": "https://drumcodefestival.com"},
    {"name": "Creamfields", "city": "UK", "date": "Aug 27-30, 2026", "genre": "EDM / Dance", "website": "https://creamfields.com"},
    {"name": "Burning Man", "city": "Nevada", "date": "Aug 23-31, 2026", "genre": "Multi-genre / Art", "website": "https://burningman.org"},
    {"name": "HARD Summer", "city": "LA", "date": "Aug 2026 (TBA)", "genre": "EDM / Hip-Hop", "website": "https://hardsummer.com"},
    {"name": "Afterlife Voyage", "city": "Ibiza", "date": "Summer 2026", "genre": "Melodic Techno", "website": "https://afterlifeofc.com"},
]

EVENTS_SYSTEM_PROMPT = (
    "You are the Simple Balance event advisor. Help find shows, festivals, "
    "and events worth attending or submitting tracks to. Focus on mau5trap roster "
    "events, Afterlife events, and major electronic festivals. "
    "Cities: Miami, LA, NYC, Chicago, Las Vegas, Ibiza, Berlin, Amsterdam. "
    "For each event: name, artists, venue, city, date, why it matters, link."
)


def render():
    st.warning("⚠️ TBD — Event data is placeholder. Real event integration coming soon.")
    st.markdown("### Festival & Events Radar")
    st.caption("Track shows. Filter by city. Never miss a mau5trap night.")

    if "fest_tracked" not in st.session_state:
        st.session_state.fest_tracked = [
            "deadmau5", "REZZ", "No Mana", "Colyn", "Tale of Us",
            "Anyma", "Lane 8", "Adam Beyer", "Township Rebellion",
        ]
    if "fest_results" not in st.session_state:
        st.session_state.fest_results = []

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("#### Filters")
        city = st.selectbox("City", ["Miami", "Los Angeles", "New York", "Chicago", "Las Vegas", "Ibiza", "Berlin", "Amsterdam"], key="fest_city")
        days = st.slider("Days Ahead", 7, 180, 30, key="fest_days")
        mau5trap_only = st.checkbox("mau5trap artists only", key="fest_mau5trap")

        if st.button("Search Events", key="fest_search", type="primary"):
            if get_edmtrain_events:
                evts = get_edmtrain_events(city, days)
                if mau5trap_only and evts:
                    rl = [m.lower() for m in MAU5TRAP_ROSTER]
                    evts = [e for e in evts if any(a.get("name","").lower() in rl for a in e.get("artists",[]))]
                st.session_state.fest_results = evts

        st.markdown("---")
        st.markdown("#### Tracked Artists")
        new_a = st.text_input("Add artist", key="fest_add", placeholder="Artist name...")
        if st.button("Track", key="fest_track_btn") and new_a:
            if new_a not in st.session_state.fest_tracked:
                st.session_state.fest_tracked.append(new_a)
                st.success(f"Now tracking {new_a}")

        rl = [m.lower() for m in MAU5TRAP_ROSTER]
        for i, art in enumerate(st.session_state.fest_tracked):
            c1, c2 = st.columns([4, 1])
            lbl = f"**{art}** (mau5trap)" if art.lower() in rl else art
            c1.markdown(lbl)
            if c2.button("x", key=f"fest_rm_{i}"):
                st.session_state.fest_tracked.pop(i)
                st.rerun()

        st.markdown("---")
        st.markdown("#### Artist Event Lookup")
        aq = st.text_input("Artist name", key="fest_aq", placeholder="Search shows...")
        if st.button("Find Shows", key="fest_ago") and aq:
            if get_bandsintown_events:
                bev = get_bandsintown_events(aq)
                if bev:
                    for ev in bev[:5]:
                        vn = ev.get("venue", {})
                        title = ev.get("title", aq)
                        st.markdown(f"**{title}**")
                        st.caption(f"{vn.get(chr(110)+chr(97)+chr(109)+chr(101), chr(39)+chr(39))} -- {vn.get(chr(99)+chr(105)+chr(116)+chr(121), chr(39)+chr(39))}")
                        st.markdown("---")
                else:
                    st.info("No events found. Configure Bandsintown API key.")

    with col1:
        events = st.session_state.fest_results
        if events:
            st.markdown(f"#### Events near {city}")
            tl = [t.lower() for t in st.session_state.fest_tracked]
            for e in events:
                arts = e.get("artists", [])
                anames = ", ".join(a.get("name","") for a in arts) if arts else "TBA"
                vn = e.get("venue", {})
                vname = vn.get("name","TBA") if isinstance(vn, dict) else str(vn)
                vloc = vn.get("location", city) if isinstance(vn, dict) else city
                tm = any(a.get("name","").lower() in tl for a in arts) if arts else False
                mm = any(a.get("name","").lower() in rl for a in arts) if arts else False
                tag = " **[mau5trap]**" if mm else (" **[TRACKED]**" if tm else "")
                with st.expander(f"{e.get(chr(100)+chr(97)+chr(116)+chr(101), chr(84)+chr(66)+chr(65))} -- {e.get(chr(110)+chr(97)+chr(109)+chr(101), chr(69)+chr(118)+chr(101)+chr(110)+chr(116))}{tag}"):
                    st.markdown(f"**Artists:** {anames}")
                    st.markdown(f"**Venue:** {vname} -- {vloc}")
                    st.markdown(f"**Ages:** {e.get(chr(97)+chr(103)+chr(101)+chr(115), chr(84)+chr(66)+chr(65))}")
                    link = e.get("link")
                    if link:
                        st.markdown(f"[Event Link]({link})")
        else:
            st.markdown("#### Major 2026 Festivals")
            st.caption("Click Search Events for live data, or browse the curated calendar.")
            for fest in FESTIVALS_2026:
                with st.expander(f"{fest[chr(100)+chr(97)+chr(116)+chr(101)]} -- {fest[chr(110)+chr(97)+chr(109)+chr(101)]} ({fest[chr(99)+chr(105)+chr(116)+chr(121)]})"):
                    st.markdown(f"**Genre:** {fest[chr(103)+chr(101)+chr(110)+chr(114)+chr(101)]}")
                    st.markdown(f"**Location:** {fest[chr(99)+chr(105)+chr(116)+chr(121)]}")
                    ws = fest[chr(119)+chr(101)+chr(98)+chr(115)+chr(105)+chr(116)+chr(101)]
                    st.markdown(f"**Website:** [{ws}]({ws})")

        st.markdown("---")
        st.markdown("#### mau5trap Roster")
        mcols = st.columns(4)
        for i, artist in enumerate(MAU5TRAP_ROSTER):
            mcols[i%4].markdown(artist)

        st.markdown("---")

        if chat:
            st.markdown("#### Event Advisor")
            st.caption("AI-generated suggestions — verify all event details independently before purchasing tickets.")
            ck = "fest_messages"
            if ck not in st.session_state:
                st.session_state[ck] = []
            for msg in st.session_state[ck]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if prompt := st.chat_input("Find mau5trap shows...", key="fest_input"):
                st.session_state[ck].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                msgs = st.session_state[ck].copy()
                with st.chat_message("assistant"):
                    with st.spinner("Checking lineups..."):
                        reply = chat(EVENTS_SYSTEM_PROMPT, msgs)
                        st.markdown(reply)
                        st.session_state[ck].append({"role": "assistant", "content": reply})
