# =============================================================================
# pages/3_Careers.py — Career Browser & Recommendations
# =============================================================================
#
# WHAT THIS PAGE DOES:
#   Phase 1: Browse all career paths, see required skills, view descriptions
#   Phase 2: "Recommended for You" tab using Jaccard similarity engine
# =============================================================================

import streamlit as st
import database as db
import recommendation as rec
import plotly.graph_objects as go
import plotly.express as px
import auth
import theme

st.set_page_config(
    page_title="Careers | CareerForge AI",
    page_icon="💼",
    layout="wide"
)

auth.require_login()
theme.inject_global_css()

st.markdown("""
<style>
.career-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.career-card:hover {
    border-color: rgba(124,58,237,0.35);
    box-shadow: 0 8px 28px rgba(124,58,237,0.12);
    transform: translateY(-3px);
}
.career-title { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.5rem; }
.career-desc  { font-size: 0.88rem; color: rgba(255,255,255,0.5); margin-bottom: 1rem; }
.skill-tag {
    display: inline-block;
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 0.78rem;
    color: #c4b5fd;
    margin: 2px;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("""
<div class="page-header">
    <h1>💼 Career Paths</h1>
    <p>Explore 10 engineering career paths and the skills required for each.
       Add your skills in the <strong>Skills</strong> page to unlock personalized recommendations.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# LOAD DATA
# =============================================================================
try:
    careers_df       = db.get_all_careers()
    career_skill_map = db.get_all_career_skill_map()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

# =============================================================================
# OVERVIEW METRICS
# =============================================================================
col1, col2, col3 = st.columns(3)
col1.metric("Available Careers", len(careers_df))
col2.metric("Total Skills Tracked", len(db.get_all_skills()))
col3.metric("Avg Skills per Career",
            f"{sum(len(v) for v in career_skill_map.values()) / max(len(career_skill_map), 1):.1f}")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# TABS
# =============================================================================
tab_recommend, tab_browse, tab_chart = st.tabs(["⭐ Recommended for You", "📋 Career Browser", "📊 Skills Heatmap"])

# --- Tab 0: Personalized Recommendations ---
with tab_recommend:
    st.markdown("### ⭐ Careers Recommended for You")
    st.markdown("""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
        Select your student profile to see careers ranked by how well your skills match.
        Score is computed using <strong>Jaccard Similarity</strong>.
    </p>
    """, unsafe_allow_html=True)

    students_df_rec = db.get_all_students()
    if students_df_rec.empty:
        st.warning("⚠️ No students registered yet. Please go to **Register** first.")
    else:
        student_options_rec = {
            f"ID {r['student_id']} — {r['name']}": r["student_id"]
            for _, r in students_df_rec.iterrows()
        }
        default_idx_rec = 0
        if "current_student_id" in st.session_state:
            for i, sid in enumerate(student_options_rec.values()):
                if sid == st.session_state["current_student_id"]:
                    default_idx_rec = i
                    break

        selected_label_rec = st.selectbox(
            "👤 Select Your Profile",
            list(student_options_rec.keys()),
            index=default_idx_rec,
            key="careers_student_select"
        )
        selected_id_rec = student_options_rec[selected_label_rec]
        st.session_state["current_student_id"] = selected_id_rec

        student_skills_rec = db.get_student_skills(selected_id_rec)

        if not student_skills_rec:
            st.warning("⚠️ No skills found for this student. Add skills in the **Skills** page first.")
        else:
            st.markdown(f"**Your skills ({len(student_skills_rec)}):** " +
                        ", ".join([f"`{s}`" for s in student_skills_rec[:8]]) +
                        (f" +{len(student_skills_rec)-8} more" if len(student_skills_rec) > 8 else ""))
            st.markdown("<br>", unsafe_allow_html=True)

            with st.spinner("Computing career matches..."):
                recs_df = rec.get_career_recommendations(selected_id_rec)

            if recs_df.empty:
                st.error("Could not compute recommendations. Check your skills.")
            else:
                career_icons = {
                    "Data Scientist": "📊", "Machine Learning Engineer": "🤖",
                    "Backend Developer": "⚙️", "Full Stack Developer": "🌐",
                    "Data Engineer": "🔧", "DevOps Engineer": "☁️",
                    "Cybersecurity Analyst": "🔒", "Embedded Systems Engineer": "🔌",
                    "AI Research Scientist": "🧬", "Cloud Architect": "🏗️",
                }

                for _, row in recs_df.iterrows():
                    icon      = career_icons.get(row["career_name"], "💼")
                    match_pct = row["match_percent"]
                    bar_color = "#22c55e" if match_pct >= 70 else ("#f59e0b" if match_pct >= 40 else "#ef4444")

                    matched_tags = " ".join(
                        [f'<span style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.35);'
                         f'border-radius:8px;padding:2px 8px;font-size:0.75rem;color:#86efac;">✓ {s}</span>'
                         for s in row["matched_skills"][:5]]
                    )
                    missing_tags = " ".join(
                        [f'<span style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);'
                         f'border-radius:8px;padding:2px 8px;font-size:0.75rem;color:#fca5a5;">✗ {s}</span>'
                         for s in row["missing_skills"][:5]]
                    )
                    more_missing = f" +{len(row['missing_skills'])-5} more" if len(row['missing_skills']) > 5 else ""

                    st.markdown(f"""
                    <div class="career-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div class="career-title">{icon} #{int(row['rank'])} {row['career_name']}</div>
                            <div style="text-align:right;">
                                <div style="font-size:1.4rem;font-weight:800;color:{bar_color};">{match_pct:.1f}%</div>
                                <div style="font-size:0.75rem;color:rgba(255,255,255,0.35);">
                                    {row['skills_matched']}/{row['total_required']} skills
                                </div>
                            </div>
                        </div>
                        <div style="background:rgba(255,255,255,0.07);border-radius:4px;height:5px;margin:0.5rem 0;">
                            <div style="width:{min(match_pct,100):.1f}%;height:100%;
                                        background:{bar_color};border-radius:4px;"></div>
                        </div>
                        <div style="margin-bottom:0.5rem;">{matched_tags}</div>
                        <div>{missing_tags}<span style='color:rgba(255,255,255,0.35);font-size:0.75rem;'>{more_missing}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

# --- Tab 1: Career Cards ---
with tab_browse:
    search_query = st.text_input(
        "🔍 Search careers or skills...",
        placeholder="e.g., Python, Data, Cloud..."
    )

    col1, col2 = st.columns(2)

    for idx, row in careers_df.iterrows():
        career_name  = row["career_name"]
        description  = row["description"]
        skills_needed = career_skill_map.get(career_name, [])

        if search_query:
            query = search_query.lower()
            matches = (
                query in career_name.lower() or
                any(query in s.lower() for s in skills_needed)
            )
            if not matches:
                continue

        target_col = col1 if idx % 2 == 0 else col2

        with target_col:
            icons = {
                "Data Scientist": "📊", "Machine Learning Engineer": "🤖",
                "Backend Developer": "⚙️", "Full Stack Developer": "🌐",
                "Data Engineer": "🔧", "DevOps Engineer": "☁️",
                "Cybersecurity Analyst": "🔒", "Embedded Systems Engineer": "🔌",
                "AI Research Scientist": "🧬", "Cloud Architect": "🏗️",
            }
            icon     = icons.get(career_name, "💼")
            tags_html = " ".join([f'<span class="skill-tag">{s}</span>' for s in skills_needed])

            st.markdown(f"""
            <div class="career-card">
                <div class="career-title">{icon} {career_name}</div>
                <div class="career-desc">{description}</div>
                <div style="margin-bottom:0.5rem;">
                    <strong style="color:rgba(255,255,255,0.6);font-size:0.82rem;">
                        Required Skills ({len(skills_needed)}):
                    </strong>
                </div>
                <div>{tags_html}</div>
            </div>
            """, unsafe_allow_html=True)

# --- Tab 2: Skills Heatmap ---
with tab_chart:
    st.markdown("### 🔥 Skills Required by Career (Comparison Chart)")
    st.markdown("""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
        Each bar shows how many skills a career requires.
    </p>
    """, unsafe_allow_html=True)

    chart_data = {
        "Career": list(career_skill_map.keys()),
        "Skills Required": [len(v) for v in career_skill_map.values()]
    }

    sorted_careers = sorted(
        zip(chart_data["Career"], chart_data["Skills Required"]),
        key=lambda x: x[1], reverse=True
    )
    careers_sorted, counts_sorted = zip(*sorted_careers) if sorted_careers else ([], [])

    fig = go.Figure(go.Bar(
        x=list(counts_sorted),
        y=list(careers_sorted),
        orientation='h',
        marker=dict(
            color=list(counts_sorted),
            colorscale="Purples",
            showscale=True,
            colorbar=dict(title="Skills", tickfont=dict(color="white"), title_font=dict(color="white"))
        ),
        text=list(counts_sorted),
        textposition='outside',
        textfont=dict(color="white"),
    ))

    fig.update_layout(
        title=dict(text="Number of Skills Required per Career Path", font=dict(color="#f1f5f9")),
        xaxis_title="Number of Skills",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.7)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        height=450,
        margin=dict(l=10, r=10, t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏆 Most In-Demand Skills Across All Careers")

    from collections import Counter
    all_skills_flat = [skill for skills in career_skill_map.values() for skill in skills]
    skill_counts = Counter(all_skills_flat).most_common(15)

    skill_names, skill_freqs = zip(*skill_counts) if skill_counts else ([], [])

    fig2 = px.bar(
        x=list(skill_names),
        y=list(skill_freqs),
        color=list(skill_freqs),
        color_continuous_scale="Purples",
        labels={"x": "Skill", "y": "Careers Requiring This Skill"},
        title="Top 15 Most In-Demand Skills",
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.7)"),
        title_font=dict(color="#f1f5f9"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        height=400,
        showlegend=False,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig2, use_container_width=True)
