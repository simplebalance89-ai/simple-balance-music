"""Tab 6: Festival & Events Radar — EDMTrain, Bandsintown, Songkick."""

import streamlit as st
from utils.apis import get_edmtrain_events, get_bandsintown_events
from utils.ai_client import chat


EVENTS_SYSTEM_PROMPT = """You are Peter and Jimmy's event advisor for Simple Balance. You help find shows, festivals, and events worth attending.

KEY CONTEXT:
- Peter and Jimmy are brothers. Music is how they communicate.
- They need to hit more shows together. Last one was Colyn at Encore, Vegas.
- MGK Lost Americana Tour, West Palm Beach, May 27, 2026 is confirmed.
- Cities: LA, Miami, Vegas, Palm Springs. Open to travel for the right show.

TRACKED ARTISTS (always flag these):
- Colyn, Tale of Us, Anyma (Afterlife)
- Upercent
- Township Rebellion
- Glowal
- Lane 8 (This Never Happened)
- MGK, Papa Roach
- Brunello
- Tim Engelhardt
- Adam Beyer (Drumcode)

RESPONSE FORMAT:
For each event, include:
- Event name and lineup
- Venue and city
- Date
- Why Peter/Jimmy should care
- Ticket link if available

When asked "Who should I see this weekend?" — filter by date, location, and artist match."""


def render():
    st.markdown("### Festival & Events Radar")
    st.caption("Find shows. Track artists. Never miss a set.")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("#### Quick Filters")
        city = st.selectbox("City", ["Los Angeles", "Miami", "Las Vegas",
                                      "Palm Springs", "New York", "Chicago"],
                            key="fest_city")
        days = st.slider("Days Ahead", 7, 90, 30, key="fest_days")

        if st.button("Search Events", key="fest_search", type="primary"):
            events = get_edmtrain_events(city, days)
            st.session_state["fest_results"] = events

        st.markdown("---")
        st.markdown("#### Tracked Artists")
        tracked = ["Colyn", "Tale of Us", "Anyma", "Upercent", "Township Rebellion",
                   "Glowal", "Lane 8", "MGK", "Papa Roach", "Brunello",
                   "Tim Engelhardt", "Adam Beyer"]
        for artist in tracked:
            st.markdown(f"- {artist}")

        st.markdown("---")
        st.markdown("#### Artist Event Lookup")
        artist_q = st.text_input("Artist name", key="fest_artist_q", placeholder="Search artist events...")
        if st.button("Find Shows", key="fest_artist_go") and artist_q:
            events = get_bandsintown_events(artist_q)
            if events:
                for e in events[:5]:
                    venue = e.get("venue", {})
                    st.markdown(f"""
**{e.get('title', artist_q)}**
{venue.get('name', '')} — {venue.get('city', '')}, {venue.get('region', '')}
{e.get('datetime', '')[:10]}
""")
            else:
                st.info("No events found. Try with Bandsintown API key configured.")

        st.markdown("---")
        st.markdown("#### Upcoming (Confirmed)")
        st.markdown("""
**MGK Lost Americana Tour**
West Palm Beach — May 27, 2026
Peter + Jimmy. Gladys bought tickets.
""")

    with col1:
        # Event results display
        events = st.session_state.get("fest_results", [])
        if events:
            st.markdown(f"#### Events in {city}")
            for e in events:
                artists = e.get("artists", [])
                artist_names = ", ".join(a.get("name", "") for a in artists) if artists else "TBA"
                venue = e.get("venue", {})
                venue_name = venue.get("name", "TBA") if isinstance(venue, dict) else str(venue)
                venue_loc = venue.get("location", city) if isinstance(venue, dict) else city

                # Check if tracked artist
                tracked_match = any(
                    a.get("name", "").lower() in [t.lower() for t in tracked]
                    for a in artists
                ) if artists else False

                marker = " **[TRACKED]**" if tracked_match else ""

                st.markdown(f"""
---
**{e.get('name', 'Event')}**{marker}
**Artists:** {artist_names}
**Venue:** {venue_name} — {venue_loc}
**Date:** {e.get('date', 'TBA')}
**Ages:** {e.get('ages', 'TBA')}
""")
        else:
            st.markdown("#### Events")
            st.info("Select a city and click **Search Events** to load upcoming shows.")

        st.markdown("---")

        # AI advisor chat
        chat_key = "fest_messages"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        st.markdown("#### Event Advisor")
        if prompt := st.chat_input("Who should I see this weekend?", key="fest_input"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})

            context = f"Current events data: {events}\n\nUser question: {prompt}"
            msg_with_context = st.session_state[chat_key].copy()
            msg_with_context[-1]["content"] = context

            with st.spinner("Checking lineups..."):
                reply = chat(EVENTS_SYSTEM_PROMPT, msg_with_context)
                st.markdown(reply)
                st.session_state[chat_key].append({"role": "assistant", "content": reply})
