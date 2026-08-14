# =============================================================================
# pages/6_AIMentor.py — AI Career Mentor powered by Google Gemini
# =============================================================================
#
# ARCHITECTURE:
#   This file handles UI only. All Gemini logic lives in llm_service.py.
#   6_AIMentor.py  →  llm_service.py  →  Gemini API
#
# FEATURES:
#   - Personalized system context from student profile + skills
#   - Streaming AI responses with live markdown rendering
#   - Thinking/loading state while Gemini generates
#   - Friendly error cards (no raw API error text ever shown)
#   - Chat history maintained within session
#   - Quick-prompt buttons for common questions
# =============================================================================

import streamlit as st
import database as db
import auth
import theme
import llm_service

st.set_page_config(
    page_title="AI Mentor | CareerForge AI",
    page_icon="🤖",
    layout="wide"
)

auth.require_login()
theme.inject_global_css()

# =============================================================================
# PAGE-SPECIFIC PREMIUM CSS
# =============================================================================
st.markdown("""
<style>
/* ── Profile box ── */
.profile-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s ease;
}
.profile-box:hover {
    border-color: rgba(124,58,237,0.35);
}
.profile-name {
    font-weight: 700;
    color: #f1f5f9;
    font-size: 1rem;
    margin-bottom: 0.5rem;
}
.profile-detail {
    color: rgba(255,255,255,0.55);
    font-size: 0.84rem;
    line-height: 1.9;
}

/* ── Section divider ── */
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1rem 0;
}

/* ── Quick prompt buttons in profile column ── */
[data-testid="column"]:first-child .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.75) !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.55rem 0.9rem !important;
    transition: all 0.25s ease !important;
    margin-bottom: 2px !important;
}
[data-testid="column"]:first-child .stButton > button:hover {
    background: rgba(124,58,237,0.14) !important;
    border-color: rgba(124,58,237,0.4) !important;
    color: #f1f5f9 !important;
    transform: translateX(3px) !important;
}

/* ── Error cards ── */
.error-card {
    background: rgba(124,58,237,0.06);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
.error-card-quota {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
.error-card-key {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
.error-icon  { font-size: 3rem; margin-bottom: 0.75rem; }
.error-title { font-size: 1.3rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.5rem; }
.error-body  { color: rgba(255,255,255,0.55); font-size: 0.9rem; line-height: 1.7; margin-bottom: 1rem; }
.error-tip   {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 0.75rem 1rem;
    color: rgba(255,255,255,0.45); font-size: 0.82rem; text-align: left;
}

/* ── Pulse animation ── */
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50%       { transform: scale(1.08); opacity: 0.8; }
}
.pulse { animation: pulse 2s ease infinite; display: inline-block; }

/* ── Thinking animation dots ── */
@keyframes thinking-dot {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40%            { transform: scale(1); opacity: 1; }
}
.thinking-dots span {
    display: inline-block;
    width: 8px; height: 8px;
    margin: 0 3px;
    background: #a78bfa;
    border-radius: 50%;
    animation: thinking-dot 1.4s ease-in-out infinite;
}
.thinking-dots span:nth-child(1) { animation-delay: 0s; }
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
.thinking-card {
    background: rgba(124,58,237,0.06);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.5rem;
}
.thinking-text {
    color: #a78bfa;
    font-weight: 600;
    font-size: 0.92rem;
}

/* ── User chat bubble ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(124,58,237,0.10) !important;
    border: 1px solid rgba(124,58,237,0.22) !important;
    border-radius: 18px 18px 4px 18px !important;
    margin-left: 3rem !important;
    margin-bottom: 0.75rem !important;
    animation: slideInRight 0.3s ease;
}

/* ── AI response card ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(10,10,30,0.70) !important;
    border: 1px solid rgba(124,58,237,0.22) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 1.5rem 1.75rem !important;
    margin-right: 2rem !important;
    margin-bottom: 0.75rem !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    animation: slideInLeft 0.3s ease;
}

/* ── Text colors inside AI card ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
    color: #E5E7EB !important;
    line-height: 1.75 !important;
    margin-bottom: 0.85rem !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) h1,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) h2 {
    color: #a78bfa !important;
    font-weight: 700 !important;
    margin-top: 1.4rem !important;
    margin-bottom: 0.7rem !important;
    padding-bottom: 0.35rem !important;
    border-bottom: 1px solid rgba(167,139,250,0.18) !important;
    font-size: 1.15rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) h3,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) h4 {
    color: #818cf8 !important;
    font-weight: 600 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
    font-size: 1rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li {
    color: #E5E7EB !important;
    margin-bottom: 0.45rem !important;
    line-height: 1.65 !important;
    font-size: 0.93rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) strong {
    color: #c4b5fd !important;
    font-weight: 600 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) hr {
    border-color: rgba(124,58,237,0.2) !important;
    margin: 1.2rem 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) code {
    background: rgba(124,58,237,0.15) !important;
    color: #c4b5fd !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
    font-size: 0.88rem !important;
}

/* ── Text color in user bubble ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: #f1f5f9 !important;
    font-size: 0.95rem !important;
}

/* ── Slide animations ── */
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* ── Chat header ── */
.chat-section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.75rem 0 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.25rem;
}
.chat-section-header-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
}
.chat-section-header-badge {
    background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.3);
    color: #6ee7b7;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
}

/* ── Disclaimer ── */
.ai-disclaimer {
    text-align: center;
    color: rgba(255,255,255,0.25);
    font-size: 0.78rem;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("""
<div class="page-header">
    <h1>🤖 AI Career Mentor</h1>
    <p>Your personal AI career coach powered by <strong>Google Gemini 2.5 Flash</strong>.
       Ask anything about careers, skills, interviews, or your learning path.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# CHECK API CONFIGURATION UPFRONT
# =============================================================================
if not llm_service.is_configured():
    err = llm_service.get_error_info("not_configured")
    st.markdown(f"""
    <div class="error-card-key">
        <div class="error-icon">{err['icon']}</div>
        <div class="error-title">{err['title']}</div>
        <div class="error-body">{err['body']}</div>
        <div class="error-tip">💡 {err['tip']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    manual_key = st.text_input(
        "Or paste your Gemini API key here (temporary, not saved):",
        type="password",
        placeholder="AQ...."
    )
    if manual_key:
        import os
        os.environ["GEMINI_API_KEY"] = manual_key
        llm_service._model      = None
        llm_service._init_error = None
        st.rerun()
    else:
        st.stop()

# =============================================================================
# LAYOUT: Profile panel (left) | Chat (right)
# =============================================================================
col_profile, col_chat = st.columns([1, 2])

# ─────────────────────────────────────────────────────────────────────────────
# LEFT: Student Profile Panel
# ─────────────────────────────────────────────────────────────────────────────
with col_profile:
    st.markdown("### 👤 Your Profile")

    try:
        students_df = db.get_all_students()
    except Exception as e:
        st.error(f"DB error: {e}")
        students_df = None

    system_context = ""

    if students_df is not None and not students_df.empty:
        student_options = {
            f"ID {r['student_id']} — {r['name']}": r["student_id"]
            for _, r in students_df.iterrows()
        }

        default_idx = 0
        if "current_student_id" in st.session_state:
            for i, sid in enumerate(student_options.values()):
                if sid == st.session_state["current_student_id"]:
                    default_idx = i
                    break

        selected_label = st.selectbox("Select Profile", list(student_options.keys()), index=default_idx)
        selected_id    = student_options[selected_label]
        st.session_state["current_student_id"] = selected_id

        student = db.get_student_by_id(selected_id)
        skills  = db.get_student_skills(selected_id)

        if student:
            st.markdown(f"""
            <div class="profile-box">
                <div class="profile-name">{student['name']}</div>
                <div class="profile-detail">
                    🎓 {student['branch']}<br>
                    📊 CGPA: {student['cgpa']}<br>
                    🌍 {student['country']}<br>
                    🎯 {student['career_goal'] or 'Not set'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Skills ({len(skills)}):**")
            if skills:
                st.markdown(", ".join([f"`{s}`" for s in skills[:10]]) +
                            (f" +{len(skills)-10} more" if len(skills) > 10 else ""))
            else:
                st.info("No skills added yet.")

        # Build personalized system context for Gemini
        system_context = f"""STUDENT PROFILE:
Name: {student['name'] if student else 'Student'}
Engineering Branch: {student['branch'] if student else 'Unknown'}
CGPA: {student['cgpa'] if student else 'Unknown'}
Country: {student['country'] if student else 'Unknown'}
Career Goal: {student['career_goal'] if student else 'Not stated'}
Current Skills: {', '.join(skills) if skills else 'None added yet'}

PERSONALIZATION RULES:
- Address the student by name occasionally
- Tailor every answer specifically to their branch, CGPA, country, and career goal
- Reference their actual skills when giving advice (mention gaps)
- Recommend country-appropriate resources and job markets
- Be extra encouraging if their CGPA is below 7.0
"""
        st.session_state["system_context"] = system_context

    else:
        st.warning("No students registered. Using generic mode.")
        system_context = "No specific student profile loaded. Give general career advice for engineering students."
        st.session_state["system_context"] = system_context
        selected_id = None

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Quick prompt suggestions ──
    st.markdown("### 💡 Quick Questions")
    quick_prompts = [
        "What career suits my skills best?",
        "Which skills should I learn first?",
        "How do I prepare for Data Science interviews?",
        "What are the best free resources to learn ML?",
        "How do I build a portfolio with no experience?",
        "What is the salary range for my target career?",
    ]
    for qp in quick_prompts:
        if st.button(qp, key=f"quick_{qp}", use_container_width=True):
            st.session_state["pending_message"] = qp
            st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["chat_history"] = []
        st.session_state.pop("last_error_type", None)
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# RIGHT: Chat Interface
# ─────────────────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown("""
    <div class="chat-section-header">
        <span style="font-size:1.4rem;">💬</span>
        <span class="chat-section-header-title">Chat with Your AI Mentor</span>
        <span class="chat-section-header-badge">● Online</span>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # ── Display previous messages ──
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # ── Welcome message on first load ──
    if not st.session_state["chat_history"]:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("""
# Welcome to CareerForge AI Mentor! 🚀

I'm your **personal AI career coach**, powered by Google Gemini.

I have your full profile loaded — your branch, skills, CGPA, and career goals. Every answer I give will be **specifically tailored to you**.

## What I can help you with:

- 🎯 **Career path selection** — Which role fits your profile best
- 📚 **Skill roadmaps** — Exactly what to learn and in what order
- 💼 **Job hunting** — Resume, portfolio, and interview strategies
- 🎓 **Higher studies** — MS/MBA abroad, GRE prep, SOP writing
- 💰 **Salary insights** — Market rates for your target role

## Try asking me:
- *"What career suits my skills in Python and SQL?"*
- *"Give me a 6-month roadmap to become a Data Scientist"*
- *"How do I crack a product company interview with my CGPA?"*

**What's your first question?** 👇
""")

    # ── Handle pending message from quick prompts ──
    if "pending_message" in st.session_state:
        user_input = st.session_state.pop("pending_message")
    else:
        user_input = None

    # ── Chat input ──
    chat_input = st.chat_input("Ask your AI mentor anything about your career...")
    if chat_input:
        user_input = chat_input

    if user_input:
        # 1. Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # 2. Add to history
        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_input
        })

        # 3. Build history for LLM (exclude the message just added)
        history_for_llm = st.session_state["chat_history"][:-1]

        # 4. Get response with thinking state + streaming
        with st.chat_message("assistant", avatar="🤖"):
            # Show thinking animation
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("""
<div class="thinking-card">
    <div class="thinking-dots"><span></span><span></span><span></span></div>
    <span class="thinking-text">AI Mentor is analyzing your profile...</span>
</div>
""", unsafe_allow_html=True)

            try:
                response_placeholder = st.empty()
                accumulated = ""

                for chunk in llm_service.ask_mentor_stream(
                    prompt=user_input,
                    history=history_for_llm,
                    system_context=st.session_state.get("system_context", "")
                ):
                    accumulated += chunk
                    # Hide thinking, show streaming content
                    thinking_placeholder.empty()
                    response_placeholder.markdown(accumulated + "▌")

                # Final render without cursor
                thinking_placeholder.empty()
                response_placeholder.markdown(accumulated)
                response_text = accumulated

                # Clear any previous error state
                st.session_state.pop("last_error_type", None)

                # 5. Save to history
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": response_text
                })

            except llm_service.LLMError as e:
                thinking_placeholder.empty()
                error_type = e.error_type
                st.session_state["last_error_type"] = error_type
                err_info   = llm_service.get_error_info(error_type)

                card_class = (
                    "error-card-quota" if error_type in ("quota_exceeded", "quota_zero") else
                    "error-card-key"   if error_type in ("invalid_key", "not_configured") else
                    "error-card"
                )

                st.markdown(f"""
                <div class="{card_class}">
                    <div class="error-icon pulse">{err_info['icon']}</div>
                    <div class="error-title">{err_info['title']}</div>
                    <div class="error-body">{err_info['body']}</div>
                    <div class="error-tip">💡 {err_info['tip']}</div>
                </div>
                """, unsafe_allow_html=True)

                # Remove failed user message from history
                if (st.session_state["chat_history"] and
                        st.session_state["chat_history"][-1]["role"] == "user"):
                    st.session_state["chat_history"].pop()

    # ── Retry / Key override (shown on error) ──
    if st.session_state.get("last_error_type"):
        error_type = st.session_state.get("last_error_type")
        if error_type in ("quota_exceeded", "quota_zero", "invalid_key", "not_configured"):
            st.markdown("<br>", unsafe_allow_html=True)
            manual_key = st.text_input(
                "Paste a working Gemini API key to override (temporary, not saved):",
                type="password",
                placeholder="AQ....",
                key="chat_error_override_key"
            )
            if manual_key:
                import os
                os.environ["GEMINI_API_KEY"] = manual_key
                llm_service._model      = None
                llm_service._init_error = None
                st.session_state.pop("last_error_type", None)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_r1, col_r2 = st.columns([1, 2])
        with col_r1:
            if st.button("🔄 Retry", key="retry_btn", use_container_width=True):
                st.session_state.pop("last_error_type", None)
                llm_service._model      = None
                llm_service._init_error = None
                st.rerun()
        with col_r2:
            st.markdown("""
            <div style="padding:0.5rem 0;color:rgba(255,255,255,0.4);font-size:0.82rem;">
                or explore your <strong style="color:#a78bfa;">Roadmap</strong>
                and <strong style="color:#a78bfa;">Skill Gap</strong> pages while you wait.
            </div>
            """, unsafe_allow_html=True)

    # ── AI Disclaimer ──
    st.markdown("""
    <div class="ai-disclaimer">
        AI Mentor can make mistakes. Consider verifying important career information.
    </div>
    """, unsafe_allow_html=True)
