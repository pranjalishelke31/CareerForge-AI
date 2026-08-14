# =============================================================================
# theme.py — CareerForge AI Shared Design System
# =============================================================================
#
# USAGE:
#   import theme
#   theme.inject_global_css()    # on every protected page
#   theme.inject_auth_css()      # on login / signup pages only
#
# DESIGN TOKENS:
#   Background  : #0a0a1a  (deep navy black)
#   Surface     : rgba(255,255,255,0.04)  (glass card)
#   Border      : rgba(255,255,255,0.08)
#   Primary     : #7c3aed → #4f46e5  (purple gradient)
#   Accent      : #a78bfa
#   Text-1      : #f1f5f9  (headings)
#   Text-2      : rgba(255,255,255,0.60)  (body)
#   Font        : Outfit (Google Fonts)
# =============================================================================

import streamlit as st


# ---------------------------------------------------------------------------
# FULL-APP CSS (all protected pages: dashboard + inner pages)
# ---------------------------------------------------------------------------
_GLOBAL_CSS = """
<style>
/* Non-render-blocking font loading via preconnect in the HTML head is preferred,
   but for Streamlit we use the @import as a fallback with display=swap */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Base ── */
html, body, .stApp {
    font-family: 'Outfit', sans-serif;
}

/* ── App background ── */
.stApp {
    background: #0a0a1a !important;
    min-height: 100vh;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a1a; }
::-webkit-scrollbar-thumb { background: #3f3f70; border-radius: 3px; }

/* ── Remove Streamlit branding ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Block container padding ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d23 0%, #12122e 50%, #0a0a1a 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.2) !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] a {
    color: #a78bfa !important;
}
[data-testid="stSidebar"] .stMarkdown a {
    color: #a78bfa !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.78rem !important;
}

/* Hide default Streamlit sidebar page navigation list */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ══════════════════════════════════════════
   HEADINGS & TEXT
   ══════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9 !important;
    font-family: 'Outfit', sans-serif !important;
}
p, li, label, .stMarkdown, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif !important;
}

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.5) !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ══════════════════════════════════════════
   FORM INPUTS
══════════════════════════════════════════ */
.stTextInput > label,
.stSelectbox > label,
.stNumberInput > label,
.stTextArea > label,
.stMultiSelect > label {
    color: rgba(255,255,255,0.75) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

/* ── All text/number/textarea inputs — white bg, dark text, always visible ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFFFF !important;
    border: 1.5px solid rgba(124,58,237,0.25) !important;
    border-radius: 12px !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    padding: 0.6rem 0.9rem !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
    outline: none !important;
    background: #FFFFFF !important;
    color: #111827 !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #9ca3af !important;
    opacity: 1 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
}
.stSelectbox > div > div > div {
    color: #f1f5f9 !important;
}

/* Multiselect */
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
[data-baseweb="tag"] {
    background: rgba(124,58,237,0.3) !important;
    border: 1px solid rgba(124,58,237,0.5) !important;
    border-radius: 8px !important;
}

/* ══════════════════════════════════════════
   TABS
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: rgba(255,255,255,0.55) !important;
    font-weight: 500 !important;
    font-family: 'Outfit', sans-serif !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #f1f5f9 !important;
    background: rgba(255,255,255,0.06) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #fff !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════
   METRICS
══════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(124,58,237,0.4) !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.12) !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ══════════════════════════════════════════
   ALERTS
══════════════════════════════════════════ */
.stSuccess {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(16,185,129,0.25) !important;
    border-radius: 12px !important;
    color: #6ee7b7 !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    border-radius: 12px !important;
    color: #fca5a5 !important;
}
.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border: 1px solid rgba(245,158,11,0.25) !important;
    border-radius: 12px !important;
    color: #fcd34d !important;
}
.stInfo {
    background: rgba(124,58,237,0.08) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    border-radius: 12px !important;
    color: #c4b5fd !important;
}

/* ══════════════════════════════════════════
   DATAFRAMES
══════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* ══════════════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    margin-bottom: 0.75rem !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    background: rgba(124,58,237,0.08) !important;
    border-color: rgba(124,58,237,0.2) !important;
}

/* ── Chat input — white bg, dark text, fully visible ── */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.02) !important;
    padding: 0.5rem !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    border: 1.5px solid rgba(124,58,237,0.3) !important;
    border-radius: 14px !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
    background: #FFFFFF !important;
    color: #111827 !important;
}

/* ══════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════ */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #a78bfa) !important;
    border-radius: 99px !important;
}
.stProgress > div > div > div {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 99px !important;
}

/* ══════════════════════════════════════════
   SPINNER
══════════════════════════════════════════ */
.stSpinner > div { border-top-color: #7c3aed !important; }

/* ══════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════ */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ══════════════════════════════════════════
   UTILITY CLASSES
══════════════════════════════════════════ */

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(124,58,237,0.35);
    box-shadow: 0 8px 32px rgba(124,58,237,0.12);
}

/* Page header banner */
.page-header {
    background: linear-gradient(135deg,
        rgba(124,58,237,0.18) 0%,
        rgba(79,70,229,0.12) 50%,
        rgba(10,10,26,0) 100%);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(124,58,237,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.page-header h1 {
    color: #f1f5f9 !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    margin: 0 0 0.4rem !important;
}
.page-header p {
    color: rgba(255,255,255,0.6) !important;
    margin: 0 !important;
    font-size: 0.95rem !important;
}

/* Skill badge */
.skill-badge {
    display: inline-block;
    background: rgba(124,58,237,0.15);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 20px;
    padding: 5px 14px;
    margin: 3px;
    font-size: 0.85rem;
    color: #c4b5fd;
    font-weight: 500;
    transition: all 0.2s;
}
.skill-badge:hover {
    background: rgba(124,58,237,0.25);
    border-color: rgba(124,58,237,0.6);
}

/* Gradient text */
.gradient-text {
    background: linear-gradient(135deg, #a78bfa, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Purple glow button variant */
.btn-outline {
    display: inline-block;
    border: 1.5px solid rgba(124,58,237,0.5);
    color: #a78bfa;
    border-radius: 12px;
    padding: 0.5rem 1.2rem;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
}
.btn-outline:hover {
    background: rgba(124,58,237,0.12);
    border-color: #7c3aed;
}
</style>
"""

# ---------------------------------------------------------------------------
# AUTH PAGES CSS (login / signup — no sidebar, full-screen dark)
# ---------------------------------------------------------------------------
_AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

html, body, .stApp { font-family: 'Outfit', sans-serif; }

/* Full-screen dark background */
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #130f40 0%, #0a0a1a 40%, #0d0620 70%, #0a0a1a 100%) !important;
    min-height: 100vh;
}

/* Hide sidebar & collapse button */
[data-testid="stSidebar"]      { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }

/* Remove top padding */
.block-container { padding-top: 0 !important; }

/* Remove Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Auth buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.4) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 40px rgba(124,58,237,0.6) !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
}

/* ── Auth inputs ── */
.stTextInput > label {
    color: rgba(255,255,255,0.75) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    margin-bottom: 4px !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.25) !important;
}

/* ── Success / Error ── */
.stSuccess {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important;
    color: #6ee7b7 !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 12px !important;
    color: #fca5a5 !important;
}
.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 12px !important;
    color: #fcd34d !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a1a; }
::-webkit-scrollbar-thumb { background: #3f3f70; border-radius: 3px; }
</style>
"""


def render_sidebar():
    """Render the standard shared sidebar navigation."""
    import auth
    import database as db

    user = auth.get_current_user()
    if not user:
        return

    with st.sidebar:
        # Logo + Branding
        st.markdown("""
        <div style='padding:1rem 0 1.2rem; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:1.2rem;'>
            <div style='display:flex;align-items:center;gap:10px;'>
                <div style='width:36px;height:36px;background:linear-gradient(135deg,#7c3aed,#4f46e5);
                            border-radius:10px;display:flex;align-items:center;justify-content:center;
                            font-size:1.1rem;box-shadow:0 4px 14px rgba(124,58,237,0.4);'>⚡</div>
                <div>
                    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>CareerForge AI</div>
                    <div style='font-size:0.72rem;color:rgba(255,255,255,0.35);'>AI Career Platform</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # User profile card
        initials = user["username"][0].upper() if user.get("username") else "U"
        st.markdown(f"""
        <div style='background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.2);
                    border-radius:14px;padding:0.9rem 1rem;margin-bottom:1.2rem;'>
            <div style='display:flex;align-items:center;gap:10px;'>
                <div style='width:38px;height:38px;background:linear-gradient(135deg,#7c3aed,#4f46e5);
                            border-radius:10px;display:flex;align-items:center;justify-content:center;
                            font-size:1rem;font-weight:800;color:white;'>{initials}</div>
                <div>
                    <div style='font-size:0.9rem;font-weight:600;color:#f1f5f9;'>{user['username']}</div>
                    <div style='font-size:0.75rem;color:rgba(255,255,255,0.4);'>{user['email']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='font-size:0.72rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.1em;color:rgba(255,255,255,0.3);margin-bottom:0.6rem;'>
            Navigation
        </div>
        """, unsafe_allow_html=True)

        # Unified navigation using page_link
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/1_Register.py", label="Register Profile", icon="📝")
        st.page_link("pages/2_Skills.py", label="Skills Catalog", icon="🧠")
        st.page_link("pages/3_Careers.py", label="Careers Match", icon="💼")
        st.page_link("pages/4_SkillGap.py", label="Skill Gap Analysis", icon="📊")
        st.page_link("pages/5_Roadmap.py", label="Learning Roadmap", icon="🗺️")
        st.page_link("pages/6_AIMentor.py", label="AI Mentor", icon="🤖")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.07);margin:1rem 0;'>", unsafe_allow_html=True)

        # Platform stats
        try:
            students_df = db.get_all_students()
            careers_df  = db.get_all_careers()
            skills_df   = db.get_all_skills()
            st.markdown("""
            <div style='font-size:0.72rem;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;color:rgba(255,255,255,0.3);margin-bottom:0.6rem;'>
                Platform Stats
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.metric("Students", len(students_df))
            c2.metric("Careers",  len(careers_df))
            c1.metric("Skills",   len(skills_df))
        except Exception:
            pass

        st.markdown("<hr style='border-color:rgba(255,255,255,0.07);margin:1rem 0;'>", unsafe_allow_html=True)

        if st.button("🚪 Sign Out", key="sidebar_logout_btn", use_container_width=True):
            auth.logout()


def inject_global_css():
    """Inject the full dark-glass design system CSS into the current Streamlit page."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
    render_sidebar()


def inject_auth_css():
    """Inject auth-page-specific CSS (login / signup). No sidebar, full-screen dark."""
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
