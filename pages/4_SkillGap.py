# =============================================================================
# pages/4_SkillGap.py — Skill Gap Analysis
# =============================================================================
#
# WHAT THIS PAGE DOES:
#   - Shows a student how ready they are for each career
#   - Visualizes which skills they have vs. which are missing
#   - Prioritizes missing skills by career relevance
#   - Gives them a clear "next steps" action plan
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import database as db
import recommendation as rec
import auth
import theme

st.set_page_config(
    page_title="Skill Gap | CareerForge AI",
    page_icon="📊",
    layout="wide"
)

auth.require_login()
theme.inject_global_css()

st.markdown("""
<style>
.gap-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.skill-have {
    display: inline-block;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 12px; padding: 4px 12px; margin: 3px;
    font-size: 0.85rem; color: #6ee7b7; font-weight: 500;
}
.skill-missing {
    display: inline-block;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px; padding: 4px 12px; margin: 3px;
    font-size: 0.85rem; color: #fca5a5; font-weight: 500;
}
.priority-badge {
    display: inline-block;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 12px; padding: 4px 14px; margin: 3px;
    font-size: 0.85rem; color: #fcd34d; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("""
<div class="page-header">
    <h1>📊 Skill Gap Analysis</h1>
    <p>Compare your skills against career requirements. Find exactly what you're missing
       and get a prioritized action plan.</p>
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
    st.warning("⚠️ No students found. Please go to **Register** first.")
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

col_sel, col_car = st.columns(2)

with col_sel:
    selected_label = st.selectbox("👤 Select Student", list(student_options.keys()), index=default_idx)
    selected_id    = student_options[selected_label]
    st.session_state["current_student_id"] = selected_id

with col_car:
    careers_df  = db.get_all_careers()
    career_names = careers_df["career_name"].tolist()
    target_career = st.selectbox("🎯 Target Career", career_names)

# =============================================================================
# LOAD DATA
# =============================================================================
student_skills = db.get_student_skills(selected_id)

if not student_skills:
    st.warning("⚠️ This student has no skills yet. Go to **Skills** page to add some!")
    st.stop()

gap = rec.get_skill_gap(selected_id, target_career)

# =============================================================================
# MATCH SCORE OVERVIEW
# =============================================================================
st.markdown("---")
st.markdown(f"### 🎯 Match Analysis: **{target_career}**")

match_pct = gap["match_percent"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Match Score",    f"{match_pct}%",         help="Percentage of required skills you already have")
col2.metric("Skills You Have", gap["skills_matched"],  help="Required skills already in your profile")
col3.metric("Skills Missing",  gap["skills_missing"],  help="Skills you need to acquire")
col4.metric("Total Required",  gap["total_required"])

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"**Readiness: {match_pct}%**")
st.progress(match_pct / 100)

if match_pct == 100:
    st.success("🎉 You're fully qualified for this career! Start applying now.")
elif match_pct >= 70:
    st.info("💪 You're almost there! Focus on the missing skills below.")
elif match_pct >= 40:
    st.warning("📚 Good foundation. A few months of study will get you there.")
else:
    st.warning("🚀 Significant skill gap. Follow the roadmap to build systematically.")

# =============================================================================
# RADAR CHART
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📡 Skill Coverage Radar Chart")

career_skill_map = db.get_all_career_skill_map()
required_skills  = career_skill_map.get(target_career, [])

if required_skills:
    student_set  = set(student_skills)
    values       = [1 if skill in student_set else 0 for skill in required_skills]
    categories   = required_skills + [required_skills[0]]
    values_plot  = values + [values[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values_plot,
        theta=categories,
        fill='toself',
        name="Your Skills",
        fillcolor='rgba(124,58,237,0.25)',
        line=dict(color='#a78bfa', width=2)
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[1] * len(categories),
        theta=categories,
        fill='toself',
        name="Required Skills",
        fillcolor='rgba(79,70,229,0.08)',
        line=dict(color='#818cf8', width=1, dash='dot')
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(color="rgba(255,255,255,0.5)")
        ),
        showlegend=True,
        legend=dict(font=dict(color="rgba(255,255,255,0.7)")),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.7)"),
        height=450,
        title=dict(text=f"Skill Radar: {target_career}", font=dict(color="#f1f5f9"))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# =============================================================================
# SKILLS BREAKDOWN
# =============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Skills You Already Have")
    if gap["matched_skills"]:
        badges = " ".join([f'<span class="skill-have">✓ {s}</span>' for s in gap["matched_skills"]])
        st.markdown(f'<div class="gap-card">{badges}</div>', unsafe_allow_html=True)
    else:
        st.info("None of the required skills are in your profile yet.")

with col2:
    st.markdown("### ❌ Skills You're Missing")
    if gap["missing_skills"]:
        badges = " ".join([f'<span class="skill-missing">✗ {s}</span>' for s in gap["missing_skills"]])
        st.markdown(f'<div class="gap-card">{badges}</div>', unsafe_allow_html=True)
    else:
        st.success("🎉 You have all required skills!")

# =============================================================================
# PRIORITY LEARNING LIST
# =============================================================================
if gap["priority_missing"]:
    st.markdown("### 🌟 Priority Skills to Learn Next")
    st.markdown("""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
        These missing skills are ranked by how frequently they appear across ALL career paths.
        Learning high-priority skills gives you the most career flexibility.
    </p>
    """, unsafe_allow_html=True)

    for i, skill in enumerate(gap["priority_missing"][:8], 1):
        st.markdown(f"""
        <div class="gap-card" style="display:flex;align-items:center;padding:1rem;gap:1rem;">
            <span style="font-size:1.3rem;color:#fbbf24;font-weight:800;">#{i}</span>
            <span class="priority-badge">⭐ {skill}</span>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# OVERVIEW TABLE — All Careers Ranked
# =============================================================================
st.markdown("---")
st.markdown("### 📋 Your Match Score Across ALL Careers")

all_recs = rec.get_career_recommendations(selected_id)
if not all_recs.empty:
    display_df = all_recs[[
        "rank", "career_name", "match_percent", "skills_matched", "skills_missing", "total_required"
    ]].copy()
    display_df.columns = ["Rank", "Career", "Match %", "Have", "Missing", "Required"]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank":     st.column_config.NumberColumn("Rank", width="small"),
            "Career":   st.column_config.TextColumn("Career Path"),
            "Match %":  st.column_config.ProgressColumn("Match %", min_value=0, max_value=100, format="%.1f%%"),
            "Have":     st.column_config.NumberColumn("✅ Have", width="small"),
            "Missing":  st.column_config.NumberColumn("❌ Missing", width="small"),
            "Required": st.column_config.NumberColumn("📋 Required", width="small"),
        }
    )
