# =============================================================================
# pages/0_Login.py — CareerForge AI Premium Login Page
# =============================================================================
#
# Full dark-theme redesign:
#   Left  — Animated branding panel with particles, features, stats
#   Right — Glassmorphism login card
# =============================================================================

import streamlit as st
import streamlit.components.v1 as components
import database as db
import auth
import theme

st.set_page_config(
    page_title="Login | CareerForge AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# If already logged in, skip to home
if auth.is_authenticated():
    st.switch_page("app.py")

# Inject auth CSS (dark full-screen, no sidebar)
theme.inject_auth_css()

# =============================================================================
# ANIMATED PARTICLE BACKGROUND + LAYOUT CSS
# =============================================================================
st.markdown("""
<style>
/* Particle canvas */
#particle-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
}

/* Ensure content stays above canvas */
.block-container { position: relative; z-index: 1; }

/* ── Left branding panel ── */
.brand-panel {
    padding: 3rem 2.5rem;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.brand-logo-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 2.5rem;
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
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1.1;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
}
.brand-headline .accent { color: #a78bfa; }

.brand-desc {
    color: rgba(255,255,255,0.55);
    font-size: 1rem;
    line-height: 1.7;
    margin-bottom: 2.5rem;
    max-width: 420px;
}

/* Feature items */
.feature-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 1.1rem;
    padding: 0.9rem 1rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease forwards;
    opacity: 0;
}
.feature-item:nth-child(1) { animation-delay: 0.1s; }
.feature-item:nth-child(2) { animation-delay: 0.2s; }
.feature-item:nth-child(3) { animation-delay: 0.3s; }
.feature-item:nth-child(4) { animation-delay: 0.4s; }
.feature-item:hover {
    background: rgba(124,58,237,0.08);
    border-color: rgba(124,58,237,0.25);
    transform: translateX(4px);
}
.feature-icon-box {
    width: 38px; height: 38px; min-width: 38px;
    background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.feature-title { font-size: 0.92rem; font-weight: 600; color: #f1f5f9; margin-bottom: 2px; }
.feature-desc  { font-size: 0.8rem; color: rgba(255,255,255,0.45); }

/* Stats row */
.stats-row {
    display: flex;
    gap: 1.5rem;
    margin-top: 2.5rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255,255,255,0.07);
}
.stat-item { text-align: left; }
.stat-num { font-size: 1.4rem; font-weight: 800; color: #a78bfa; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.45); margin-top: 1px; }

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

.auth-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 0.3rem;
}
.auth-subtitle {
    color: rgba(255,255,255,0.45);
    font-size: 0.92rem;
    margin-bottom: 2rem;
}

.auth-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.2rem 0;
}
.auth-divider-line {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
}
.auth-divider-text {
    color: rgba(255,255,255,0.3);
    font-size: 0.82rem;
    font-weight: 500;
}

.auth-footer {
    text-align: center;
    margin-top: 1.5rem;
    color: rgba(255,255,255,0.25);
    font-size: 0.78rem;
    line-height: 1.6;
}
.auth-footer a { color: #a78bfa; text-decoration: none; }

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(24px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-12px); }
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PARTICLE ANIMATION (lightweight canvas JS)
# =============================================================================
components.html("""
<canvas id="particle-canvas" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;"></canvas>
<script>
(function() {
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    let W = window.innerWidth, H = window.innerHeight;
    canvas.width = W; canvas.height = H;
    window.addEventListener('resize', () => {
        W = window.innerWidth; H = window.innerHeight;
        canvas.width = W; canvas.height = H;
    });
    const NUM = 60;
    const particles = Array.from({length: NUM}, () => ({
        x: Math.random() * W, y: Math.random() * H,
        r: Math.random() * 1.8 + 0.4,
        dx: (Math.random() - 0.5) * 0.35,
        dy: (Math.random() - 0.5) * 0.35,
        a: Math.random() * 0.6 + 0.1,
    }));
    function draw() {
        ctx.clearRect(0, 0, W, H);
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(167,139,250,${p.a})`;
            ctx.fill();
            p.x += p.dx; p.y += p.dy;
            if (p.x < 0 || p.x > W) p.dx *= -1;
            if (p.y < 0 || p.y > H) p.dy *= -1;
        });
        // Draw connecting lines
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const d = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y);
                if (d < 120) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(124,58,237,${0.12 * (1 - d/120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", height=0)

# =============================================================================
# LAYOUT
# =============================================================================
left, right = st.columns([1.1, 0.9], gap="large")

# ── LEFT: Branding ──
with left:
    brand_html = (
        '<div class="brand-panel">'
        '<div class="brand-logo-row">'
        '<div class="brand-logo-icon">⚡</div>'
        '<div><div class="brand-logo-text">CareerForge AI</div>'
        '<div class="brand-logo-sub">Your AI Career Companion</div></div></div>'
        '<div class="brand-headline">Discover.<br>Learn.<br><span class="accent">Succeed.</span></div>'
        '<div class="brand-desc">CareerForge AI uses the power of AI to guide students toward the '
        'right skills, careers, and opportunities. Powered by Google Gemini.</div>'
        '<div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:0.1em;color:rgba(255,255,255,0.3);margin-bottom:0.8rem;">Why CareerForge AI?</div>'
        '<div class="feature-item"><div class="feature-icon-box">🎯</div>'
        '<div><div class="feature-title">AI Career Guidance</div>'
        '<div class="feature-desc">Personalized career recommendations using AI</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">📊</div>'
        '<div><div class="feature-title">Skill Gap Analysis</div>'
        '<div class="feature-desc">Find missing skills required for your dream career</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">🗺️</div>'
        '<div><div class="feature-title">Learning Roadmap</div>'
        '<div class="feature-desc">Get a step-by-step growth plan</div></div></div>'
        '<div class="feature-item"><div class="feature-icon-box">🤖</div>'
        '<div><div class="feature-title">AI Mentor</div>'
        '<div class="feature-desc">Chat with your personal career advisor</div></div></div>'
        '<div class="stats-row">'
        '<div class="stat-item"><div class="stat-num">10K+</div><div class="stat-label">Students Guided</div></div>'
        '<div class="stat-item"><div class="stat-num">500+</div><div class="stat-label">Skills Covered</div></div>'
        '<div class="stat-item"><div class="stat-num">30+</div><div class="stat-label">Career Paths</div></div>'
        '<div class="stat-item"><div class="stat-num">95%</div><div class="stat-label">Success Rate</div></div>'
        '</div></div>'
    )
    st.markdown(brand_html, unsafe_allow_html=True)

# ── RIGHT: Login Form ──
with right:
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div class="auth-title">Welcome Back 👋</div><div class="auth-subtitle">Login to continue your journey</div>', unsafe_allow_html=True)
        email    = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Login →", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in both email and password.")
        else:
            user = auth.authenticate_user(email, password)
            if user:
                auth.login_user(user)
                st.success(f"Welcome back, **{user['username']}**! Redirecting...")
                st.switch_page("app.py")
            else:
                st.error("❌ Invalid email or password. Please try again.")

    st.markdown("""
    <div class="auth-divider">
        <div class="auth-divider-line"></div>
        <div class="auth-divider-text">OR</div>
        <div class="auth-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("👤  Create New Account", key="goto_signup", use_container_width=True):
        st.switch_page("pages/0_Signup.py")

    st.markdown("""
    <div class="auth-footer">
        By continuing, you agree to our
        <a href="#">Terms &amp; Privacy Policy</a>
    </div>
    """, unsafe_allow_html=True)
