# =============================================================================
# pages/5_Roadmap.py — ML-Powered Personalized Learning Roadmap
# =============================================================================
#
# WHAT THIS PAGE DOES:
#   - Uses the ML recommendation engine (TF-IDF + Cosine Similarity) to rank careers
#   - Generates a structured, phase-by-phase learning roadmap for the chosen career
#   - Shows estimated time, skill priorities, and free learning resources
#   - Displays an interactive Gantt-style timeline chart
# =============================================================================

import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import database as db
import recommendation as rec
from datetime import datetime, timedelta
import auth
import theme

st.set_page_config(
    page_title="Roadmap | CareerForge AI",
    page_icon="🗺️",
    layout="wide"
)

auth.require_login()
theme.inject_global_css()

st.markdown("""
<style>
.phase-card {
    border-radius: 18px; padding: 1.5rem;
    margin-bottom: 1.5rem; border: 1px solid;
    transition: all 0.3s ease;
}
.phase-card:hover { transform: translateY(-2px); }

.phase-1 {
    background: rgba(59,130,246,0.06);
    border-color: rgba(59,130,246,0.2);
}
.phase-2 {
    background: rgba(124,58,237,0.06);
    border-color: rgba(124,58,237,0.2);
}
.phase-3 {
    background: rgba(236,72,153,0.06);
    border-color: rgba(236,72,153,0.2);
}

.phase-header { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.4rem; }
.phase-meta   { color: rgba(255,255,255,0.45); font-size: 0.88rem; margin-bottom: 0.8rem; }
.phase-desc   { color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 0.75rem; }

.resource-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 6px 12px;
    margin: 4px 0; color: rgba(255,255,255,0.6);
    font-size: 0.84rem;
}

.skill-pill {
    display: inline-block;
    border-radius: 20px; padding: 5px 14px; margin: 3px;
    font-size: 0.84rem; font-weight: 600;
}
.pill-1 { background: rgba(59,130,246,0.15); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }
.pill-2 { background: rgba(124,58,237,0.15); color: #c4b5fd; border: 1px solid rgba(124,58,237,0.3); }
.pill-3 { background: rgba(236,72,153,0.15); color: #f9a8d4; border: 1px solid rgba(236,72,153,0.3); }

.career-rec-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 1rem; margin-bottom: 0.75rem;
    display: flex; justify-content: space-between; align-items: center;
    transition: all 0.3s ease;
}
.career-rec-card:hover {
    border-color: rgba(124,58,237,0.35);
    box-shadow: 0 4px 20px rgba(124,58,237,0.1);
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("""
<div class="page-header">
    <h1>🗺️ Personalized Learning Roadmap</h1>
    <p>ML-powered recommendations + structured learning path to reach your target career.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# STUDENT SELECTOR
# =============================================================================
try:
    students_df = db.get_all_students()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if students_df.empty:
    st.warning("⚠️ No students registered. Please go to **Register** first.")
    st.stop()

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

selected_label = st.selectbox("👤 Select Student", list(student_options.keys()), index=default_idx)
selected_id    = student_options[selected_label]
st.session_state["current_student_id"] = selected_id

student_skills = db.get_student_skills(selected_id)
student_data   = db.get_student_by_id(selected_id)

if not student_skills:
    st.warning("⚠️ No skills found. Please add skills in the **Skills** page first.")
    st.stop()

# =============================================================================
# ML RECOMMENDATIONS
# =============================================================================
st.markdown("---")
st.markdown("### 🤖 ML-Powered Career Recommendations")
st.markdown("""
<p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
    Powered by <strong>TF-IDF + Cosine Similarity</strong>.
    Unlike basic matching, this model weights rare skills higher,
    giving you more personalized recommendations.
</p>
""", unsafe_allow_html=True)

with st.spinner("Running ML recommendation engine..."):
    ml_recs = rec.get_ml_recommendations(selected_id)

if ml_recs.empty:
    st.error("Could not generate recommendations. Please add skills first.")
    st.stop()

top5 = ml_recs.head(5)

career_icons = {
    "Data Scientist": "📊", "Machine Learning Engineer": "🤖",
    "Backend Developer": "⚙️", "Full Stack Developer": "🌐",
    "Data Engineer": "🔧", "DevOps Engineer": "☁️",
    "Cybersecurity Analyst": "🔒", "Embedded Systems Engineer": "🔌",
    "AI Research Scientist": "🧬", "Cloud Architect": "🏗️",
}

for _, row in top5.iterrows():
    icon      = career_icons.get(row["career_name"], "💼")
    bar_width = min(int(row["match_percent"]), 100)
    st.markdown(f"""
    <div class="career-rec-card">
        <div>
            <span style="font-size:1.2rem;margin-right:0.5rem;">{icon}</span>
            <strong style="color:#f1f5f9;">{row['career_name']}</strong>
            <span style="color:rgba(255,255,255,0.35);font-size:0.82rem;margin-left:0.5rem;">
                #{int(row['rank'])} Match
            </span>
        </div>
        <div style="text-align:right;">
            <div style="color:#a78bfa;font-weight:700;font-size:1.1rem;">{row['match_percent']:.1f}%</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.35);">
                {row['skills_matched']} / {row['total_required']} skills
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ROADMAP GENERATOR
# =============================================================================
st.markdown("---")
st.markdown("### 🗺️ Generate Your Learning Roadmap")

default_career_idx = 0
career_list  = db.get_all_careers()["career_name"].tolist()
top_career   = ml_recs.iloc[0]["career_name"] if not ml_recs.empty else career_list[0]
if top_career in career_list:
    default_career_idx = career_list.index(top_career)

col1, col2 = st.columns([3, 1])
with col1:
    target_career = st.selectbox(
        "🎯 Select Target Career for Roadmap",
        options=career_list,
        index=default_career_idx
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("⚡ Generate Roadmap", use_container_width=True)

if "roadmap_data" not in st.session_state or generate_btn or \
   st.session_state.get("roadmap_career") != target_career or \
   st.session_state.get("roadmap_student") != selected_id:

    with st.spinner("🧠 Building your personalized roadmap..."):
        roadmap = rec.generate_roadmap(selected_id, target_career)
        st.session_state["roadmap_data"]    = roadmap
        st.session_state["roadmap_career"]  = target_career
        st.session_state["roadmap_student"] = selected_id
else:
    roadmap = st.session_state["roadmap_data"]

# =============================================================================
# DISPLAY ROADMAP
# =============================================================================
if not roadmap:
    gap = rec.get_skill_gap(selected_id, target_career)
    if gap["match_percent"] == 100:
        st.success(f"🎉 You already have ALL required skills for **{target_career}**! You're ready to apply!")
    else:
        st.info("No roadmap data available. Try adding more skills.")
else:
    total_weeks  = sum(phase["duration_weeks"] for phase in roadmap)
    total_skills = sum(len(phase["skills"]) for phase in roadmap)

    col1, col2, col3 = st.columns(3)
    col1.metric("Phases",          len(roadmap))
    col2.metric("Skills to Learn", total_skills)
    col3.metric("Est. Duration",   f"{total_weeks} weeks")

    st.markdown(f"""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;margin-top:0.5rem;'>
        Your personalized roadmap to become a
        <strong style='color:#a78bfa;'>{target_career}</strong>.
        Follow the phases in order — each phase builds on the previous.
    </p>
    """, unsafe_allow_html=True)

    pill_classes      = ["pill-1", "pill-2", "pill-3"]
    phase_card_classes = ["phase-1", "phase-2", "phase-3"]

    for phase in roadmap:
        pn         = phase["phase_number"] - 1
        card_class = phase_card_classes[min(pn, 2)]
        pill_class = pill_classes[min(pn, 2)]

        skill_pills   = " ".join([f'<span class="skill-pill {pill_class}">{s}</span>' for s in phase["skills"]])
        resources_html = "".join([f'<div class="resource-item">📖 {r}</div>' for r in phase["resources"]])

        st.markdown(f"""
        <div class="phase-card {card_class}">
            <div class="phase-header">{phase['phase_name']}</div>
            <div class="phase-meta">
                📅 Estimated Duration: ~{phase['duration_weeks']} weeks &nbsp;|&nbsp;
                📚 {len(phase['skills'])} skill(s) to learn
            </div>
            <div class="phase-desc">{phase['phase_desc']}</div>
            <div style='margin-bottom:1rem;'>{skill_pills}</div>
            <div>
                <strong style='color:rgba(255,255,255,0.6);font-size:0.82rem;'>
                    📚 Free Learning Resources:
                </strong>
                {resources_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── GANTT TIMELINE ──
    st.markdown("### 📅 Learning Timeline")
    st.markdown("""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
        Phases are arranged sequentially. Complete Phase 1 before starting Phase 2.
    </p>
    """, unsafe_allow_html=True)

    gantt_data   = []
    start_date   = datetime.now()
    colors_map   = {}
    phase_colors = ["#3b82f6", "#8b5cf6", "#ec4899"]

    for phase in roadmap:
        duration = timedelta(weeks=phase["duration_weeks"])
        end_date  = start_date + duration
        pn        = phase["phase_number"] - 1
        color     = phase_colors[min(pn, 2)]

        for skill in phase["skills"]:
            gantt_data.append(dict(
                Task=skill,
                Start=start_date.strftime("%Y-%m-%d"),
                Finish=end_date.strftime("%Y-%m-%d"),
                Resource=phase["phase_name"]
            ))
            colors_map[phase["phase_name"]] = color

        start_date = end_date

    if gantt_data:
        fig_gantt = ff.create_gantt(
            gantt_data,
            colors=colors_map,
            index_col='Resource',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True,
            title=f"Learning Timeline: {target_career}"
        )
        fig_gantt.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)"),
            title_font=dict(color="#f1f5f9"),
            height=max(300, len(gantt_data) * 30 + 100),
        )
        st.plotly_chart(fig_gantt, use_container_width=True)
