# =============================================================================
# app.py — CareerForge AI Main Dashboard
# =============================================================================
#
# PHASE 5 ADDITIONS (preserved):
#   - require_login() guard (unauthenticated users → Login page)
#   - Logout button in the sidebar
#
# UI REDESIGN (this file):
#   - Premium dark navy dashboard
#   - Animated welcome hero
#   - Glass metric cards
#   - Navigation feature tiles
# =============================================================================

import streamlit as st
import database as db
import auth
import theme
from datetime import datetime

# =============================================================================
# PAGE CONFIGURATION — Must be the FIRST Streamlit call in the script
# =============================================================================
st.set_page_config(
    page_title="CareerForge AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "CareerForge AI — Personalized Career Guidance for Engineering Students"
    }
)

# =============================================================================
# AUTH GUARD
# =============================================================================
auth.require_login()
user = auth.get_current_user()

# =============================================================================
# SHARED CSS
# =============================================================================
theme.inject_global_css()

# Dashboard-specific extra CSS
st.markdown("""
<style>
/* ── Hero ── */
.dash-hero {
    background: linear-gradient(135deg,
        rgba(124,58,237,0.2) 0%,
        rgba(79,70,229,0.12) 40%,
        rgba(10,10,26,0) 100%);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    animation: fadeIn 0.6s ease forwards;
}
.dash-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(124,58,237,0.2) 0%, transparent 70%);
    pointer-events: none;
}
.dash-hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(79,70,229,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-greeting {
    font-size: 0.85rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: #a78bfa; margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2.4rem; font-weight: 900; color: #f1f5f9;
    line-height: 1.2; margin-bottom: 0.6rem;
}
.hero-title .accent { color: #a78bfa; }
.hero-sub { color: rgba(255,255,255,0.5); font-size: 1rem; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.78rem; font-weight: 600; color: #6ee7b7;
    margin-top: 1rem;
}
.hero-badge::before { content: '●'; color: #10b981; font-size: 0.5rem; }

/* ── Feature nav cards ── */
.feature-nav {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 1.5rem;
    text-align: center; transition: all 0.3s ease;
    cursor: pointer;
    animation: fadeInUp 0.5s ease forwards; opacity: 0;
}
.feature-nav:nth-child(1) { animation-delay: 0.1s; }
.feature-nav:nth-child(2) { animation-delay: 0.2s; }
.feature-nav:nth-child(3) { animation-delay: 0.3s; }
.feature-nav:nth-child(4) { animation-delay: 0.4s; }
.feature-nav:hover {
    border-color: rgba(124,58,237,0.4);
    box-shadow: 0 8px 32px rgba(124,58,237,0.15);
    transform: translateY(-5px);
}
.feature-nav-icon {
    font-size: 2rem; margin-bottom: 0.6rem;
    display: block;
    filter: drop-shadow(0 0 12px rgba(124,58,237,0.4));
}
.feature-nav-title {
    font-size: 0.95rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.3rem;
}
.feature-nav-desc { font-size: 0.8rem; color: rgba(255,255,255,0.4); }

/* ── Architecture table ── */
.arch-table {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.5rem;
}

/* ── Tech badges ── */
.tech-badge {
    display: inline-block;
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.82rem; color: #c4b5fd; margin: 4px; font-weight: 500;
}

/* Sidebar nav items */
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 0.6rem 0.8rem; border-radius: 10px;
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.9rem; font-weight: 500;
    transition: all 0.2s; margin-bottom: 2px;
    text-decoration: none !important;
}
.nav-item:hover {
    background: rgba(124,58,237,0.12) !important;
    color: #f1f5f9 !important;
}

/* Sidebar avatar bubble */
.avatar-bubble {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 800; color: white;
    box-shadow: 0 4px 16px rgba(124,58,237,0.35);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================
@st.cache_resource
def init_db():
    db.initialize_database()
    return True

init_db()

# Database initialization handles caching and will keep the connection pools hot.

# =============================================================================
# HERO SECTION
# =============================================================================
now = datetime.now()
greeting_hour = now.hour
greeting_word  = "Good morning" if greeting_hour < 12 else ("Good afternoon" if greeting_hour < 17 else "Good evening")
date_str = now.strftime("%A, %B %d")

st.markdown(f"""
<div class="dash-hero">
    <div class="hero-greeting">⚡ {greeting_word}</div>
    <div class="hero-title">
        Welcome back, <span class="accent">{user['username']}</span>
    </div>
    <div class="hero-sub">
        {date_str} · Your AI-powered career dashboard is ready.
    </div>
    <div class="hero-badge"> System Online — AI Ready</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# QUICK STATS
# =============================================================================
try:
    students_df = db.get_all_students()
    careers_df  = db.get_all_careers()
    skills_df   = db.get_all_skills()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎓 Students", len(students_df), help="Total registered students")
    col2.metric("💼 Career Paths", len(careers_df), help="Available career tracks")
    col3.metric("🧠 Skills Tracked", len(skills_df), help="Skills in the master catalog")
    col4.metric("🤖 AI Mentor", "Active", help="Gemini AI chatbot status")
except Exception:
    st.info("Loading platform data...")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# FEATURE NAVIGATION TILES
# =============================================================================
st.markdown("""
<div style='font-size:0.8rem;font-weight:600;text-transform:uppercase;
            letter-spacing:0.1em;color:rgba(255,255,255,0.35);margin-bottom:1rem;'>
    ✨ Platform Features
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-nav">
        <span class="feature-nav-icon">📝</span>
        <div class="feature-nav-title">Student Profile</div>
        <div class="feature-nav-desc">Register your academic background, branch & CGPA</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-nav">
        <span class="feature-nav-icon">💡</span>
        <div class="feature-nav-title">Career Match</div>
        <div class="feature-nav-desc">AI matches your skills to engineering career paths</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-nav">
        <span class="feature-nav-icon">📊</span>
        <div class="feature-nav-title">Skill Gap Analysis</div>
        <div class="feature-nav-desc">See exactly which skills you need to acquire</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-nav">
        <span class="feature-nav-icon">🤖</span>
        <div class="feature-nav-title">AI Mentor</div>
        <div class="feature-nav-desc">Chat with Gemini AI for personalized guidance</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# HOW IT WORKS
# =============================================================================
st.markdown("""
<div style='font-size:0.8rem;font-weight:600;text-transform:uppercase;
            letter-spacing:0.1em;color:rgba(255,255,255,0.35);margin-bottom:1rem;'>
    🏗️ How It Works
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="arch-table">
    """, unsafe_allow_html=True)
    st.markdown("""
**The 5-Phase Build:**

| Phase | Feature | Technology |
|-------|---------|------------|
| **1** | Student registration + profile storage | Streamlit + MySQL |
| **2** | Rule-based career recommendations + skill gap | Jaccard Similarity |
| **3** | ML-powered personalized roadmap | Scikit-learn |
| **4** | AI career mentor chatbot | Google Gemini |
| **5** | Authentication + secure accounts | bcrypt + Sessions |

**Data Flow:**
```
Login → Student Profile → Skills → Recommendation Engine → Career Match → Roadmap
```
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
**Quick Start:**
1. 👉 Click **Register** in the sidebar
2. Fill in your profile details
3. Go to **Skills** and add what you know
4. Visit **Careers** to see your matches
5. Use **Skill Gap** to find what to learn
6. Get your **Roadmap** from the ML engine
7. Chat with the **AI Mentor** for guidance
    """)

# =============================================================================
# TECH STACK BADGES
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;'>
    <span class="tech-badge">Python</span>
    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">MySQL</span>
    <span class="tech-badge">Scikit-learn</span>
    <span class="tech-badge">Google Gemini</span>
    <span class="tech-badge">bcrypt</span>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;color:rgba(255,255,255,0.2);font-size:0.82rem;'>
    Built with ❤️ using Python · Streamlit · MySQL · Scikit-learn · Google Gemini · bcrypt<br>
    CareerForge AI — Flagship AI/Data Science Project
</div>
""", unsafe_allow_html=True)
