"""
Simple Balance — Music AI Command Center
Peter + Jimmy Wilson | J.A.W. | Built on Azure AI

10 Modules:
1. J.A.W. DJ Command — Energy flow, set building, track curation
2. Music Discovery — Find tracks by mood, meaning, connection
3. AI Mastering Studio — Upload → master → export
4. Stem Separation Lab — Demucs / LALAL.AI stem extraction
5. AI Music Generation — Mubert / AIVA DMCA-free generation
6. Festival & Events Radar — EDMTrain, Bandsintown, Songkick
7. Set Builder — Drag-and-drop set planning with energy flow
8. Jimmy's Mix Archive — 18+ J.A.W. mixes cataloged and searchable
9. Producer Tools — Chords, reference analysis, samples
10. Dashboard — Activity feed, stats, calendar
"""

import streamlit as st
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Simple Balance — Music AI",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Session Stats ---
if "stats" not in st.session_state:
    st.session_state.stats = {
        "total_queries": 0,
        "total_tokens_in": 0,
        "total_tokens_out": 0,
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a1a; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0d0d24 0%, #1a1a3a 50%, #2a1a4a 100%);
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 16px;
        border: 1px solid #2a2a5a;
    }
    .main-header h1 { color: #ffffff; font-size: 26px; margin: 0; font-weight: 700; }
    .main-header p { color: #FFC000; font-size: 13px; margin: 4px 0 0 0; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #0d0d24;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8890b0;
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        color: #FFC000 !important;
        background-color: #1a1a3a !important;
    }

    /* Cards */
    [data-testid="stExpander"] {
        background-color: #141428;
        border: 1px solid #1e1e40;
        border-radius: 8px;
    }

    /* Chat */
    .stChatMessage {
        background-color: #141428 !important;
        border: 1px solid #1e1e40 !important;
        border-radius: 8px !important;
    }
    .stChatMessage p, .stChatMessage span, .stChatMessage li, .stChatMessage td { color: #e2e8f0 !important; }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3, .stChatMessage h4 { color: #FFC000 !important; }
    .stChatMessage strong { color: #FFC000 !important; }
    .stChatMessage code {
        color: #a78bfa !important;
        background-color: #1e1e40 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    .stChatMessage pre {
        background-color: #0d0d24 !important;
        border: 1px solid #2a2a5a !important;
        border-radius: 6px !important;
    }
    .stChatMessage pre code { color: #e2e8f0 !important; background-color: transparent !important; }
    .stChatMessage table th {
        background-color: #1a1a3a !important;
        color: #FFC000 !important;
        padding: 8px 12px !important;
    }
    .stChatMessage table td {
        padding: 6px 12px !important;
        border-bottom: 1px solid #1e1e40 !important;
        color: #e2e8f0 !important;
    }

    /* Inputs */
    div[data-testid="stChatInput"] textarea {
        background-color: #141428 !important;
        border: 1px solid #2a2a5a !important;
        color: #e2e8f0 !important;
    }

    /* Buttons */
    .stButton button {
        background-color: #1a1a3a !important;
        color: #FFC000 !important;
        border: 1px solid #2a2a5a !important;
    }
    .stButton button:hover { background-color: #2a1a4a !important; color: #ffffff !important; }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #141428;
        border: 1px solid #1e1e40;
        border-radius: 8px;
        padding: 12px;
    }
    [data-testid="stMetricLabel"] { color: #8890b0 !important; }
    [data-testid="stMetricValue"] { color: #FFC000 !important; }

    /* Progress bars */
    .stProgress > div > div { background-color: #FFC000 !important; }

    /* Footer */
    .footer { color: #4a4a6a; font-size: 11px; text-align: center; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🎧 Simple Balance — Music AI Command Center</h1>
    <p>Peter + Jimmy Wilson | J.A.W. | 10 Modules | Built on Azure AI</p>
</div>
""", unsafe_allow_html=True)

# --- Import Tabs ---
from tabs.tab_jaw import render as render_jaw
from tabs.tab_discovery import render as render_discovery
from tabs.tab_mastering import render as render_mastering
from tabs.tab_stems import render as render_stems
from tabs.tab_generation import render as render_generation
from tabs.tab_festivals import render as render_festivals
from tabs.tab_setbuilder import render as render_setbuilder
from tabs.tab_archive import render as render_archive
from tabs.tab_producer import render as render_producer
from tabs.tab_dashboard import render as render_dashboard

# --- Tab Navigation ---
tabs = st.tabs([
    "🎧 J.A.W. DJ Command",
    "🎵 Music Discovery",
    "🎛️ AI Mastering",
    "🔀 Stem Separation",
    "🎹 AI Generation",
    "📡 Events Radar",
    "📋 Set Builder",
    "💿 Jimmy's Archive",
    "🔧 Producer Tools",
    "📊 Dashboard",
])

with tabs[0]:
    render_jaw()
with tabs[1]:
    render_discovery()
with tabs[2]:
    render_mastering()
with tabs[3]:
    render_stems()
with tabs[4]:
    render_generation()
with tabs[5]:
    render_festivals()
with tabs[6]:
    render_setbuilder()
with tabs[7]:
    render_archive()
with tabs[8]:
    render_producer()
with tabs[9]:
    render_dashboard()

# --- Footer ---
s = st.session_state.stats
total_tokens = s["total_tokens_in"] + s["total_tokens_out"]
st.markdown(f"""
<div class="footer">
    Simple Balance — Music AI Command Center | Session: {s['total_queries']} queries, {total_tokens:,} tokens<br>
    Peter + Jimmy Wilson | J.A.W. | Built with Sinton.ia
</div>
""", unsafe_allow_html=True)
