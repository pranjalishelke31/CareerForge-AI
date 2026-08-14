# =============================================================================
# pages/0_Signup.py — CareerForge AI Premium Signup Page
# =============================================================================
#
# Same dark split-layout as Login, with:
#   - Password strength indicator
#   - Confirm password visual match
# =============================================================================

import streamlit as st
import auth
import theme

st.set_page_config(
    page_title="Sign Up | CareerForge AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# If already logged in, skip to home
if auth.is_authenticated():
    st.switch_page("app.py")

theme.inject_auth_css()

st.markdown("""
<style>
.block-container { padding-top: 0 !important; }

/* ── Left branding panel ── */
.brand-panel {
    padding: 3rem 2.5rem;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.brand-logo-row {
    display: flex; align-items: center; gap: 12px; margin-bottom: 2.5rem;
}
.brand-logo-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
}
.brand-logo-text { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; }
.brand-logo-sub  { font-size: 0.78rem; color: rgba(255,255,255,0.45); }

.brand-headline {
    font-size: 2.8rem; font-weight: 900; line-height: 1.15;
    color: #f1f5f9; margin-bottom: 0.5rem;
}
.brand-headline .accent { color: #a78bfa; }
.brand-desc {
    color: rgba(255,255,255,0.55); font-size: 1rem;
    line-height: 1.7; margin-bottom: 2.5rem; max-width: 400px;
}

.feature-item {
    display: flex; align-items: flex-start; gap: 14px;
    margin-bottom: 1rem; padding: 0.85rem 1rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease forwards; opacity: 0;
}
.feature-item:nth-child(1) { animation-delay: 0.1s; }
.feature-item:nth-child(2) { animation-delay: 0.2s; }
.feature-item:nth-child(3) { animation-delay: 0.3s; }
.feature-item:nth-child(4) { animation-delay: 0.4s; }
.feature-item:nth-child(5) { animation-delay: 0.5s; }
.feature-item:hover {
    background: rgba(124,58,237,0.08);
    border-color: rgba(124,58,237,0.25);
    transform: translateX(4px);
}
.feature-icon-box {
    width: 36px; height: 36px; min-width: 36px;
    background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.feature-title { font-size: 0.9rem; font-weight: 600; color: #f1f5f9; margin-bottom: 2px; }
.feature-desc  { font-size: 0.78rem; color: rgba(255,255,255,0.45); }

/* ── Right glass card ── */
div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
}
div[data-testid="stForm"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 28px !important;
    padding: 2.5rem !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    box-shadow:
        0 0 0 1px rgba(124,58,237,0.08),
        0 20px 60px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.08) !important;
    max-width: 440px !important;
    margin: auto !important;
    animation: slideInRight 0.5s ease forwards;
}

.auth-title    { font-size: 1.8rem; font-weight: 800; color: #f1f5f9; margin-bottom: 0.3rem; }
.auth-subtitle { color: rgba(255,255,255,0.45); font-size: 0.92rem; margin-bottom: 1.8rem; }

.auth-divider {
    display: flex; align-items: center; gap: 12px; margin: 1.2rem 0;
}
.auth-divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.08); }
.auth-divider-text { color: rgba(255,255,255,0.3); font-size: 0.82rem; font-weight: 500; }
.auth-footer {
    text-align: center; margin-top: 1.5rem;
    color: rgba(255,255,255,0.25); font-size: 0.78rem; line-height: 1.6;
}
.auth-footer a { color: #a78bfa; text-decoration: none; }

/* Password strength */
.pw-bar-wrap {
    height: 4px; background: rgba(255,255,255,0.08);
    border-radius: 99px; margin-top: 6px; overflow: hidden;
}
.pw-bar-fill {
    height: 100%; border-radius: 99px;
    transition: width 0.3s ease, background 0.3s ease;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(24px); }
    to   { opacity: 1; transform: translateX(0); }
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# LAYOUT
# =============================================================================
left, right = st.columns([1.1, 0.9], gap="large")

# ── LEFT: Branding ──
with left:
    signup_brand = (
        '<div class="brand-panel">'
        '<div class="brand-logo-row">'
        '<div class="brand-logo-icon">⚡</div>'
        '<div><div class="brand-logo-text">CareerForge AI</div>'
        '<div class="brand-logo-sub">Your AI Career Companion</div></div></div>'
        '<div class="brand-headline">Join thousands<br>building their<br>'
        '<span class="accent">career with AI.</span></div>'
        '<div class="brand-desc">Create your free account and get personalized career guidance '
        'powered by Google Gemini and machine learning.</div>'
        '<div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.1em;color:rgba(255,255,255,0.3);margin-bottom:0.8rem;">What you get</div>'
        '<div class="feature-item"><div class="feature-icon-box">🎯</div>'
        '<div><div class="feature-title">Personalized Career Paths</div>'
        '<div class="feature-desc">AI recommends careers based on your skills</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">📊</div>'
        '<div><div class="feature-title">Skill Gap Analysis</div>'
        '<div class="feature-desc">See exactly what you\'re missing</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">🗺️</div>'
        '<div><div class="feature-title">ML-Powered Roadmap</div>'
        '<div class="feature-desc">3-phase structured learning plan</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">🤖</div>'
        '<div><div class="feature-title">Gemini AI Mentor</div>'
        '<div class="feature-desc">Chat with your personal career advisor</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">🔒</div>'
        '<div><div class="feature-title">Secure Account</div>'
        '<div class="feature-desc">bcrypt-encrypted — your data stays private</div></div></div>'
        '</div>'
    )
    st.markdown(signup_brand, unsafe_allow_html=True)

    # Placeholder to preserve column spacing


# ── RIGHT: Signup Form ──
with right:
    with st.form("signup_form", clear_on_submit=False):
        st.markdown('<div class="auth-title">Create your account ✨</div><div class="auth-subtitle">Free forever — no credit card required</div>', unsafe_allow_html=True)
        username = st.text_input("Full Name", placeholder="e.g. Aarav Sharma")
        email    = st.text_input("Email Address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

        # Password strength hint
        if password:
            length = len(password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            if length < 6:
                strength, width, color, label = 1, "25%", "#ef4444", "Weak"
            elif length < 10 or not (has_upper or has_digit):
                strength, width, color, label = 2, "55%", "#f59e0b", "Medium"
            else:
                strength, width, color, label = 3, "100%", "#10b981", "Strong"

            st.markdown(f"""
            <div style="margin-bottom:0.5rem;">
                <div style="font-size:0.78rem; color:{color}; margin-bottom:3px;">
                    Password strength: <strong>{label}</strong>
                </div>
                <div class="pw-bar-wrap">
                    <div class="pw-bar-fill" style="width:{width}; background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Create Account →", use_container_width=True)

    if submitted:
        if not username or not email or not password or not confirm:
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("❌ Passwords do not match. Please try again.")
        elif len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters.")
        else:
            result = auth.create_user(username, email, password)
            if result["success"]:
                st.success("✅ Account created! Signing you in...")
                st.balloons()
                st.switch_page("pages/0_Login.py")
            else:
                st.error(f"❌ {result['error']}")

    st.markdown("""
    <div class="auth-divider">
        <div class="auth-divider-line"></div>
        <div class="auth-divider-text">OR</div>
        <div class="auth-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Sign in instead →", key="goto_login", use_container_width=True):
        st.switch_page("pages/0_Login.py")

    st.markdown("""
    <div class="auth-footer">
        By signing up, you agree to our
        <a href="#">Terms &amp; Privacy Policy</a>
    </div>
    """, unsafe_allow_html=True)
