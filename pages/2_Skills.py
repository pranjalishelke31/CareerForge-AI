# =============================================================================
# pages/2_Skills.py — Branch-Aware Student Skill Management
# =============================================================================
#
# WHAT THIS PAGE DOES:
#   - Lets a student select their profile (by ID)
#   - Shows branch-specific skill categories (MECH gets SolidWorks, not Kubernetes)
#   - View all skills currently on their profile
#   - Add new skills (from branch-filtered catalog OR custom text input)
#   - Remove individual skills
#
# BRANCH MAPPING:
#   Detects the student's registered branch and shows the most relevant skill
#   categories first. All students can also see General/Cross-Branch skills.
# =============================================================================

import streamlit as st
import database as db
import auth
import theme

st.set_page_config(
    page_title="Skills | CareerForge AI",
    page_icon="🧠",
    layout="wide"
)

auth.require_login()
theme.inject_global_css()

st.markdown("""
<style>
.skill-grid {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.5rem;
}
.info-box {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.branch-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(79,70,229,0.2));
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #c4b5fd;
    margin-left: 8px;
}
.recommended-box {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(124,58,237,0.06));
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
}
.recommended-title {
    font-weight: 700;
    color: #6ee7b7;
    font-size: 0.9rem;
    margin-bottom: 0.6rem;
}
.cat-header {
    font-size: 0.95rem;
    font-weight: 700;
    color: #a78bfa;
    padding: 0.4rem 0 0.2rem;
    border-bottom: 1px solid rgba(167,139,250,0.12);
    margin-bottom: 0.5rem;
    margin-top: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("""
<div class="page-header">
    <h1>🧠 Skill Management</h1>
    <p>Add and manage your technical skills. Skill catalog is personalized to your engineering branch.</p>
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
    st.warning("⚠️ No students registered yet. Please go to **Register** first.")
    st.stop()

student_options = {
    f"ID {row['student_id']} — {row['name']} ({row['branch']})": row["student_id"]
    for _, row in students_df.iterrows()
}

col_select, col_info = st.columns([2, 1])

with col_select:
    selected_label = st.selectbox(
        "👤 Select Your Student Profile",
        list(student_options.keys()),
        help="Choose your student profile to manage skills"
    )
    selected_id = student_options[selected_label]

st.session_state["current_student_id"] = selected_id
current_skills = db.get_student_skills(selected_id)
student_data   = db.get_student_by_id(selected_id)
branch         = student_data["branch"] if student_data else "Other Engineering"

with col_info:
    if student_data:
        st.markdown(f"""
        <div class="info-box">
            <strong style='color:#f1f5f9;'>{student_data['name']}</strong><br>
            <span style='color:rgba(255,255,255,0.5);'>🎓 {student_data['branch']}</span><br>
            <span style='color:rgba(255,255,255,0.5);'>📊 CGPA: {student_data['cgpa']}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# BRANCH-AWARE SKILL CATALOG — Categories per branch
# =============================================================================

# ─── General skills shown to everyone ───────────────────────────────────────
GENERAL_SKILLS = {
    "🌐 General / Cross-Branch": [
        "Python for Engineers", "MATLAB", "Microsoft Excel (Advanced)",
        "Technical Report Writing", "Research Methodology", "Literature Survey",
        "Project Management", "Communication", "Problem Solving",
        "Team Collaboration", "Leadership", "Time Management",
        "Technical Presentation", "Data Analysis with Excel", "Git",
    ],
    "💻 Programming for Engineers": [
        "Python", "C++", "Java", "MATLAB", "R",
    ],
}

# ─── Branch-specific catalogs ─────────────────────────────────────────────
BRANCH_SKILLS = {
    # CS / IT
    "Computer Science & Engineering": {
        "🐍 Programming Languages":    ["Python", "Java", "C++", "JavaScript", "R", "Scala", "Go"],
        "🤖 AI & Machine Learning":    ["Machine Learning", "Deep Learning", "Natural Language Processing",
                                         "Computer Vision", "TensorFlow", "PyTorch", "Scikit-learn"],
        "📊 Data Science":             ["Data Analysis", "Statistics", "Pandas", "NumPy", "Data Visualization"],
        "🗄️ Databases":               ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis"],
        "🌐 Web & Backend":            ["Django", "Flask", "FastAPI", "REST API", "GraphQL", "HTML", "CSS"],
        "☁️ Cloud & DevOps":           ["AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "CI/CD", "Git"],
        "🔒 Security & Networking":    ["Cybersecurity", "Networking", "Linux", "Ethical Hacking", "Cryptography"],
        "⚙️ Embedded & Hardware":      ["Embedded C", "Arduino", "RTOS", "VHDL", "PCB Design"],
    },
    "Information Technology": {
        "🐍 Programming Languages":    ["Python", "Java", "JavaScript", "C++", "Go"],
        "🤖 AI & Machine Learning":    ["Machine Learning", "Deep Learning", "Natural Language Processing",
                                         "TensorFlow", "Scikit-learn"],
        "📊 Data Science":             ["Data Analysis", "Statistics", "Pandas", "NumPy", "Data Visualization", "SQL"],
        "🌐 Web & Backend":            ["Django", "Flask", "FastAPI", "REST API", "HTML", "CSS", "GraphQL"],
        "🗄️ Databases":               ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis"],
        "☁️ Cloud & DevOps":           ["AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "CI/CD", "Git"],
        "🔒 Cybersecurity":            ["Cybersecurity", "Networking", "Linux", "Ethical Hacking", "Cryptography"],
    },

    # ENTC
    "Electronics & Telecommunication Engineering": {
        "🔬 VLSI & Digital Design":    ["VLSI Design", "Verilog", "VHDL", "FPGA Programming", "Digital Electronics"],
        "⚡ Embedded Systems":         ["Embedded C", "Microcontrollers", "ARM Architecture", "Arduino",
                                         "RTOS", "Raspberry Pi", "ESP32", "IoT Development"],
        "📡 Communication Systems":    ["Digital Communication", "Wireless Communication", "Signal Processing",
                                         "RF Design", "Antenna Design", "5G Technology"],
        "🔧 PCB & Hardware":           ["PCB Design", "Altium Designer", "KiCad", "Soldering & Prototyping",
                                         "Analog Electronics"],
        "📐 Simulation & Analysis":    ["MATLAB", "Simulink", "LabVIEW"],
    },

    # Mechanical Engineering
    "Mechanical Engineering": {
        "🖥️ CAD / Design Tools":       ["SolidWorks", "AutoCAD", "CATIA", "Fusion 360", "PTC Creo", "Siemens NX"],
        "🔩 Simulation & Analysis":    ["ANSYS", "Finite Element Analysis (FEA)", "Computational Fluid Dynamics (CFD)",
                                         "Thermal Analysis", "Structural Analysis", "MATLAB", "Simulink"],
        "🏭 Manufacturing":            ["CNC Programming", "Manufacturing Processes", "GD&T",
                                         "3D Printing / Additive Manufacturing", "Welding & Fabrication",
                                         "Sheet Metal Design", "Injection Molding", "Lean Manufacturing"],
        "⚙️ Mechanical Fundamentals":  ["Thermodynamics", "Fluid Mechanics", "Heat Transfer",
                                         "Machine Design", "Kinematics & Dynamics", "Hydraulics & Pneumatics"],
        "🤖 Industrial & Automation":  ["Industrial Automation", "PLC Programming", "Robotics"],
    },

    # Civil Engineering
    "Civil Engineering": {
        "🏗️ Structural Design":        ["STAAD.Pro", "ETABS", "SAP2000", "Structural Analysis",
                                         "Concrete Design", "Steel Design", "Foundation Design"],
        "✏️ CAD & BIM Tools":          ["AutoCAD Civil 3D", "Revit (BIM)", "AutoCAD"],
        "🌍 Surveying & GIS":          ["Surveying", "GPS & GIS Mapping", "Remote Sensing", "Total Station"],
        "🏢 Construction Management":  ["Construction Management", "Estimation & Costing", "Project Scheduling",
                                         "Quality Control (Civil)", "Contract Management",
                                         "Primavera P6", "MS Project"],
        "💧 Environmental & Water":    ["Environmental Engineering", "Water Resources Engineering",
                                         "Waste Management", "Hydrology", "Geotechnical Engineering", "Soil Testing"],
    },

    # Electrical Engineering
    "Electrical Engineering": {
        "⚡ Power Systems":            ["Power Systems Analysis", "Electrical Machines", "Power Electronics",
                                         "ETAP", "PSCAD", "High Voltage Engineering",
                                         "Protection & Relay Systems"],
        "🔄 Control & Automation":     ["Control Systems", "PID Tuning", "Industrial Automation",
                                         "PLC Programming", "PLC & HMI", "SCADA Systems", "Motor Drives"],
        "☀️ Renewable Energy":         ["Renewable Energy Systems", "Solar PV Design", "Wind Energy"],
        "🔌 Electrical Design":        ["Electrical Design (AutoCAD Electrical)", "AutoCAD"],
        "📐 Simulation Tools":         ["MATLAB", "Simulink"],
    },

    # Chemical Engineering
    "Chemical Engineering": {
        "⚗️ Process & Design":         ["Process Simulation (Aspen)", "Chemical Process Design",
                                         "Mass & Energy Balances", "Heat Exchanger Design",
                                         "Reactor Design", "Separation Processes", "Fluid Flow in Pipes"],
        "🏭 Instrumentation":          ["Piping & Instrumentation (P&ID)", "HSE (Health, Safety & Environment)"],
        "📊 Quality & Compliance":     ["Quality Control (Chemical)", "Six Sigma"],
    },

    # Aerospace
    "Aerospace Engineering": {
        "🛩️ Design Tools":             ["CATIA", "SolidWorks", "ANSYS", "AutoCAD"],
        "🚀 Analysis":                 ["Finite Element Analysis (FEA)", "Computational Fluid Dynamics (CFD)",
                                         "Structural Analysis", "Thermodynamics", "Fluid Mechanics"],
        "⚙️ Simulation":               ["MATLAB", "Simulink"],
        "🏭 Manufacturing":            ["Manufacturing Processes", "Lean Manufacturing", "GD&T"],
    },

    # Biomedical
    "Biomedical / Biotechnology Engineering": {
        "🔬 Biology & Lab":            ["Molecular Biology", "Cell Culture Techniques",
                                         "PCR & Gel Electrophoresis", "CRISPR Technology"],
        "💊 Clinical & Regulatory":    ["Drug Discovery", "Clinical Research",
                                         "Regulatory Affairs (FDA/CE)", "Bioinformatics"],
        "🏥 Medical Devices":          ["Medical Imaging", "Biomechanics", "Medical Device Design"],
        "📐 Engineering Tools":        ["MATLAB", "Python for Engineers", "Data Analysis"],
    },
}

# Alias for IT — same categories as CS
BRANCH_SKILLS["Information Technology"] = BRANCH_SKILLS.get(
    "Information Technology", BRANCH_SKILLS["Computer Science & Engineering"]
)

# Get the branch-specific categories
def get_branch_categories(branch_name: str) -> dict:
    """Return skill categories for the given branch, with general skills appended."""
    # Try exact match first
    branch_cats = BRANCH_SKILLS.get(branch_name, {})
    # Merge with general skills
    merged = {**branch_cats, **GENERAL_SKILLS}
    return merged

# Recommend top skills based on branch (skills that a student in this branch should learn first)
BRANCH_RECOMMENDATIONS = {
    "Computer Science & Engineering":              ["Python", "SQL", "Machine Learning", "Git", "Docker", "Data Structures"],
    "Information Technology":                      ["Python", "SQL", "Django", "Git", "Docker", "Networking"],
    "Electronics & Telecommunication Engineering": ["Embedded C", "MATLAB", "VLSI Design", "PCB Design", "Arduino", "Signal Processing"],
    "Mechanical Engineering":                      ["SolidWorks", "AutoCAD", "ANSYS", "Finite Element Analysis (FEA)", "MATLAB", "GD&T"],
    "Civil Engineering":                           ["AutoCAD Civil 3D", "STAAD.Pro", "Revit (BIM)", "Structural Analysis", "MS Project", "Surveying"],
    "Electrical Engineering":                      ["MATLAB", "Power Systems Analysis", "Control Systems", "PLC Programming", "AutoCAD", "ETAP"],
    "Chemical Engineering":                        ["Process Simulation (Aspen)", "MATLAB", "Mass & Energy Balances", "HSE (Health, Safety & Environment)", "Six Sigma", "Chemical Process Design"],
    "Aerospace Engineering":                       ["CATIA", "ANSYS", "Finite Element Analysis (FEA)", "Computational Fluid Dynamics (CFD)", "MATLAB", "SolidWorks"],
    "Biomedical / Biotechnology Engineering":      ["Bioinformatics", "Python for Engineers", "Molecular Biology", "MATLAB", "Medical Imaging", "Clinical Research"],
    "Other Engineering":                           ["Python for Engineers", "MATLAB", "Microsoft Excel (Advanced)", "Technical Report Writing", "Project Management", "Problem Solving"],
}

# =============================================================================
# CURRENT SKILLS DISPLAY
# =============================================================================
st.markdown("### 💼 Current Skills")

if current_skills:
    col_metrics = st.columns(3)
    col_metrics[0].metric("Skills Added", len(current_skills))

    badges_html = " ".join(
        [f'<span class="skill-badge">✅ {skill}</span>' for skill in current_skills]
    )
    st.markdown(f'<div class="skill-grid">{badges_html}</div>', unsafe_allow_html=True)
else:
    st.info("ℹ️ No skills added yet. Use the section below to add your skills.")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# RECOMMENDED SKILLS FOR YOUR BRANCH
# =============================================================================
recommended = BRANCH_RECOMMENDATIONS.get(branch, BRANCH_RECOMMENDATIONS["Other Engineering"])
missing_recommended = [s for s in recommended if s not in current_skills]

if missing_recommended:
    rec_badges = " ".join([
        f'<span class="skill-badge" style="background:rgba(16,185,129,0.12);border-color:rgba(16,185,129,0.3);color:#6ee7b7;">⭐ {s}</span>'
        for s in missing_recommended
    ])
    st.markdown(f"""
    <div class="recommended-box">
        <div class="recommended-title">⭐ Recommended for {branch}</div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.82rem;margin-bottom:0.6rem;">
            Top skills students in your branch should have:
        </div>
        {rec_badges}
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ADD SKILLS SECTION
# =============================================================================
st.markdown("### ➕ Add Skills")

tab_catalog, tab_custom = st.tabs(["📚 From Catalog", "✍️ Custom Skill"])

with tab_catalog:
    st.markdown(f"""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
        Skill catalog filtered for <strong style='color:#c4b5fd;'>{branch}</strong>.
        General skills are always shown at the bottom.
    </p>
    """, unsafe_allow_html=True)

    all_skills_df    = db.get_all_skills()
    all_skill_names  = all_skills_df["skill_name"].tolist()
    available_skills = [s for s in all_skill_names if s not in current_skills]

    if not available_skills:
        st.success("🎉 You've added all available catalog skills!")
    else:
        branch_categories = get_branch_categories(branch)

        selected_skills = []
        for category, skills_in_cat in branch_categories.items():
            available_in_cat = [s for s in skills_in_cat if s in available_skills]
            if available_in_cat:
                st.markdown(f'<div class="cat-header">{category}</div>', unsafe_allow_html=True)
                chosen = st.multiselect(
                    label=category,
                    options=available_in_cat,
                    label_visibility="collapsed",
                    key=f"cat_{category}"
                )
                selected_skills.extend(chosen)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Selected Skills", use_container_width=True, key="add_catalog"):
            if not selected_skills:
                st.warning("⚠️ Please select at least one skill.")
            else:
                added_count = 0
                for skill in selected_skills:
                    if db.add_student_skill(selected_id, skill):
                        added_count += 1
                if added_count > 0:
                    st.success(f"✅ Added {added_count} skill(s) successfully!")
                    st.rerun()

with tab_custom:
    st.markdown("""
    <p style='color:rgba(255,255,255,0.5);font-size:0.9rem;'>
        Don't see your skill in the catalog? Add it here. Custom skills are also stored in the system.
    </p>
    """, unsafe_allow_html=True)

    with st.form("custom_skill_form"):
        custom_skill = st.text_input(
            "Skill Name",
            placeholder="e.g., Hadoop, Spark, ETAP, SAFE Design, MATLAB Toolbox..."
        )
        add_custom_btn = st.form_submit_button("➕ Add Custom Skill", use_container_width=True)

        if add_custom_btn:
            if not custom_skill.strip():
                st.error("❌ Please enter a skill name.")
            else:
                added = db.add_student_skill(selected_id, custom_skill.strip().title())
                if added:
                    st.success(f"✅ '{custom_skill.strip().title()}' added to your profile!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ You already have '{custom_skill.strip().title()}' in your profile.")

# =============================================================================
# REMOVE SKILLS SECTION
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🗑️ Remove Skills")

if not current_skills:
    st.info("ℹ️ No skills to remove yet.")
else:
    col1, col2 = st.columns([2, 1])
    with col1:
        skill_to_remove = st.selectbox("Select skill to remove", options=current_skills)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Remove Skill", key="remove_skill"):
            db.remove_student_skill(selected_id, skill_to_remove)
            st.success(f"✅ Removed '{skill_to_remove}' from your profile.")
            st.rerun()
