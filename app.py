"""
Simple Balance - Music AI Production Suite v2.0
J.A.W. | Peter + Jimmy Wilson | Production Edition
"""

import os
import streamlit as st
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Simple Balance - Music AI v2.0",
    page_icon="SB",
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


# --- API Status Check ---
def _get_secret(key):
    """Get secret from Streamlit secrets or env vars."""
    try:
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    return os.environ.get(key, "")


def _check_api_status():
    """Check which APIs are configured."""
    status = {}
    status["Replicate"] = bool(_get_secret("REPLICATE_API_TOKEN"))
    status["Dolby.io"] = bool(_get_secret("DOLBY_API_KEY"))
    status["Azure OpenAI"] = bool(_get_secret("AZURE_OPENAI_ENDPOINT") and _get_secret("AZURE_OPENAI_KEY"))
    status["AudD"] = bool(_get_secret("AUDD_API_TOKEN"))
    return status


# --- Custom CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a1a; }
    .main-header {
        background: linear-gradient(135deg, #0d0d24 0%, #1a1a3a 50%, #2a1a4a 100%);
        padding: 20px 28px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #2a2a5a;
    }
    .main-header h1 { color: #ffffff; font-size: 26px; margin: 0; font-weight: 700; }
    .main-header .subtitle { color: #FFC000; font-size: 13px; margin: 4px 0 0 0; }
    .main-header .version { color: #8890b0; font-size: 11px; margin: 2px 0 0 0; }
    .status-bar {
        background-color: #0d0d24; border: 1px solid #1e1e40; border-radius: 8px;
        padding: 8px 16px; margin-bottom: 12px; display: flex; gap: 20px; align-items: center;
    }
    .status-item { font-size: 12px; display: inline-flex; align-items: center; gap: 6px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
    .status-connected { background-color: #22c55e; }
    .status-disconnected { background-color: #ef4444; }
    .status-label { color: #8890b0; }
    .stTabs [data-baseweb="tab-list"] { gap: 0px; background-color: #0d0d24; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8890b0; background-color: transparent; border-radius: 6px; padding: 8px 16px; font-size: 13px; }
    .stTabs [aria-selected="true"] { color: #FFC000 !important; background-color: #1a1a3a !important; }
    [data-testid="stExpander"] { background-color: #141428; border: 1px solid #1e1e40; border-radius: 8px; }
    .stChatMessage { background-color: #141428 !important; border: 1px solid #1e1e40 !important; border-radius: 8px !important; }
    .stChatMessage p, .stChatMessage span, .stChatMessage li, .stChatMessage td { color: #e2e8f0 !important; }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3, .stChatMessage h4 { color: #FFC000 !important; }
    .stChatMessage strong { color: #FFC000 !important; }
    .stChatMessage code { color: #a78bfa !important; background-color: #1e1e40 !important; padding: 2px 6px !important; border-radius: 4px !important; }
    .stChatMessage pre { background-color: #0d0d24 !important; border: 1px solid #2a2a5a !important; border-radius: 6px !important; }
    .stChatMessage pre code { color: #e2e8f0 !important; background-color: transparent !important; }
    .stChatMessage table th { background-color: #1a1a3a !important; color: #FFC000 !important; padding: 8px 12px !important; }
    .stChatMessage table td { padding: 6px 12px !important; border-bottom: 1px solid #1e1e40 !important; color: #e2e8f0 !important; }
    div[data-testid="stChatInput"] textarea { background-color: #141428 !important; border: 1px solid #2a2a5a !important; color: #e2e8f0 !important; }
    .stButton button { background-color: #1a1a3a !important; color: #FFC000 !important; border: 1px solid #2a2a5a !important; }
    .stButton button:hover { background-color: #2a1a4a !important; color: #ffffff !important; }
    [data-testid="stMetric"] { background-color: #141428; border: 1px solid #1e1e40; border-radius: 8px; padding: 12px; }
    [data-testid="stMetricLabel"] { color: #8890b0 !important; }
    [data-testid="stMetricValue"] { color: #FFC000 !important; }
    .stProgress > div > div { background-color: #FFC000 !important; }
    .footer { color: #4a4a6a; font-size: 11px; text-align: center; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>Simple Balance | Music AI Production Suite</h1>
    <p class="subtitle">J.A.W. | Peter + Jimmy Wilson | Production Suite</p>
    <p class="version">v2.0 Production Edition</p>
</div>
""", unsafe_allow_html=True)

# --- API Status Bar ---
api_status = _check_api_status()
status_html_parts = []
for name, connected in api_status.items():
    dot_class = "status-connected" if connected else "status-disconnected"
    status_html_parts.append(
        f'<span class="status-item"><span class="status-dot {dot_class}"></span><span class="status-label">{name}</span></span>'
    )
status_html = " ".join(status_html_parts)
st.markdown(f'<div class="status-bar">{status_html}</div>', unsafe_allow_html=True)


# --- Import Tabs ---
from tabs.tab_jaw import render as render_jaw
from tabs.tab_discovery import render as render_discovery
from tabs.tab_mastering import render as render_mastering
from tabs.tab_stems import render as render_stems
from tabs.tab_generation import render as render_generation
from tabs.tab_festivals import render as render_festivals
from tabs.tab_setbuilder import render as render_setbuilder
from tabs.tab_archive import render as render_archive
from tabs.tab_digestor import render as render_digestor
from tabs.tab_producer import render as render_producer
from tabs.tab_dashboard import render as render_dashboard

# --- Tab Navigation ---
tabs = st.tabs([
    "DJ Command",
    "Discovery",
    "AI Mastering",
    "Stem Separation",
    "AI Generation",
    "Events Radar",
    "Set Builder",
    "Mix Archive",
    "Mix Digestor",
    "Producer Tools",
    "Dashboard",
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
    render_digestor()
with tabs[9]:
    render_producer()
with tabs[10]:
    render_dashboard()

# --- Footer ---
s = st.session_state.stats
total_tokens = s["total_tokens_in"] + s["total_tokens_out"]
queries = s["total_queries"]
footer_text = f"Simple Balance | Music AI Production Suite v2.0 | Session: {queries} queries, {total_tokens:,} tokens"
st.markdown(
    f'<div class="footer">{footer_text}<br>J.A.W. | Peter + Jimmy Wilson | Built with Sinton.ia</div>',
    unsafe_allow_html=True,
)
