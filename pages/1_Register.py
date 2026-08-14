# =============================================================================
# pages/1_Register.py — Student Registration & Profile Management
# =============================================================================
#
# WHY IS THIS IN "pages/" FOLDER?
#   Streamlit's multi-page feature automatically reads every .py file in a
#   "pages/" subfolder and adds it to the sidebar.
#   The "1_" prefix ensures this page appears first in the sidebar.
#
# WHAT THIS PAGE DOES:
#   - Create: Registration form to add a new student
#   - Read:   View all registered students in a table
#   - Update: Edit a student's profile
#   - Delete: Remove a student from the database
# =============================================================================

import streamlit as st
import database as db
import auth
import theme

st.set_page_config(
    page_title="Register | CareerForge AI",
    page_icon="📝",
    layout="wide"
)

auth.require_login()
theme.inject_global_css()

# Page-specific CSS
st.markdown("""
<style>
.form-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem;
}
.danger-zone {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 14px;
    padding: 1.2rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown("""
<div class="page-header">
    <h1>📝 Student Registration</h1>
    <p>Create your profile to get personalized career recommendations.</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# TABS — Registration Form | View Students | Edit/Delete
# =============================================================================
tab_register, tab_view, tab_edit = st.tabs(["➕ Register", "👥 All Students", "✏️ Edit / Delete"])

# ===========================================================================
# TAB 1: REGISTRATION FORM
# ===========================================================================
with tab_register:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown("### Create Your Profile")

    with st.form("registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="e.g., Alex Johnson",
                help="Enter your full name"
            )

            branch = st.selectbox(
                "Engineering Branch *",
                options=[
                    "Computer Science & Engineering",
                    "Information Technology",
                    "Electronics & Telecommunication Engineering",
                    "Mechanical Engineering",
                    "Civil Engineering",
                    "Electrical Engineering",
                    "Chemical Engineering",
                    "Aerospace Engineering",
                    "Biomedical / Biotechnology Engineering",
                    "Other Engineering"
                ],
                help="Select your primary engineering discipline"
            )

            cgpa = st.number_input(
                "CGPA *",
                min_value=0.0,
                max_value=10.0,
                value=7.5,
                step=0.1,
                format="%.1f",
                help="Your current CGPA out of 10"
            )

        with col2:
            country = st.text_input(
                "Country *",
                placeholder="e.g., India",
                value="India"
            )

            career_goal = st.text_area(
                "Career Goal",
                placeholder="e.g., I want to become a Data Scientist at a top tech company...",
                height=140,
                help="Describe what career you want to pursue and why."
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Register Now", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("❌ Please enter your full name.")
            elif not country.strip():
                st.error("❌ Please enter your country.")
            elif cgpa < 0 or cgpa > 10:
                st.error("❌ CGPA must be between 0 and 10.")
            else:
                try:
                    student_id = db.create_student(
                        name=name.strip(),
                        branch=branch,
                        cgpa=cgpa,
                        country=country.strip(),
                        career_goal=career_goal.strip()
                    )
                    st.success(f"🎉 Registration successful! Your Student ID is: **{student_id}**")
                    st.session_state["current_student_id"] = student_id
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# TAB 2: VIEW ALL STUDENTS
# ===========================================================================
with tab_view:
    st.markdown("### 👥 Registered Students")

    try:
        students_df = db.get_all_students()

        if students_df.empty:
            st.info("ℹ️ No students registered yet. Go to the Register tab to add one!")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Students", len(students_df))
            col2.metric("Avg CGPA", f"{students_df['cgpa'].mean():.2f}")
            col3.metric("Branches", students_df['branch'].nunique())

            st.markdown("<br>", unsafe_allow_html=True)

            st.dataframe(
                students_df[["student_id", "name", "branch", "cgpa", "country", "career_goal"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "student_id":  st.column_config.NumberColumn("ID", width="small"),
                    "name":        st.column_config.TextColumn("Name"),
                    "branch":      st.column_config.TextColumn("Branch"),
                    "cgpa":        st.column_config.NumberColumn("CGPA", format="%.1f"),
                    "country":     st.column_config.TextColumn("Country"),
                    "career_goal": st.column_config.TextColumn("Career Goal"),
                }
            )

    except Exception as e:
        st.error(f"Error loading students: {e}")

# ===========================================================================
# TAB 3: EDIT / DELETE
# ===========================================================================
with tab_edit:
    st.markdown("### ✏️ Edit or Delete a Student Profile")

    try:
        students_df = db.get_all_students()

        if students_df.empty:
            st.info("ℹ️ No students registered yet.")
        else:
            student_options = {
                f"ID {row['student_id']} — {row['name']}": row['student_id']
                for _, row in students_df.iterrows()
            }
            selected_label = st.selectbox("Select Student", list(student_options.keys()))
            selected_id = student_options[selected_label]

            student = db.get_student_by_id(selected_id)

            if student:
                col1, col2 = st.columns([3, 1])

                with col1:
                    with st.form("edit_form"):
                        st.markdown(f"**Editing: {student['name']}**")
                        new_name    = st.text_input("Name", value=student["name"])
                        new_branch  = st.selectbox(
                            "Engineering Branch",
                            options=[
                                "Computer Science & Engineering",
                                "Information Technology",
                                "Electronics & Telecommunication Engineering",
                                "Mechanical Engineering",
                                "Civil Engineering",
                                "Electrical Engineering",
                                "Chemical Engineering",
                                "Aerospace Engineering",
                                "Biomedical / Biotechnology Engineering",
                                "Other Engineering"
                            ],
                            index=[
                                "Computer Science & Engineering",
                                "Information Technology",
                                "Electronics & Telecommunication Engineering",
                                "Mechanical Engineering",
                                "Civil Engineering",
                                "Electrical Engineering",
                                "Chemical Engineering",
                                "Aerospace Engineering",
                                "Biomedical / Biotechnology Engineering",
                                "Other Engineering"
                            ].index(student["branch"]) if student["branch"] in [
                                "Computer Science & Engineering",
                                "Information Technology",
                                "Electronics & Telecommunication Engineering",
                                "Mechanical Engineering",
                                "Civil Engineering",
                                "Electrical Engineering",
                                "Chemical Engineering",
                                "Aerospace Engineering",
                                "Biomedical / Biotechnology Engineering",
                                "Other Engineering"
                            ] else 0
                        )
                        new_cgpa    = st.number_input("CGPA", value=float(student["cgpa"]),
                                                      min_value=0.0, max_value=10.0, step=0.1)
                        new_country = st.text_input("Country", value=student["country"])
                        new_goal    = st.text_area("Career Goal", value=student["career_goal"] or "")

                        update_btn = st.form_submit_button("💾 Save Changes")
                        if update_btn:
                            db.update_student(
                                student_id=selected_id,
                                name=new_name,
                                branch=new_branch,
                                cgpa=new_cgpa,
                                country=new_country,
                                career_goal=new_goal
                            )
                            st.success("✅ Profile updated successfully!")
                            st.rerun()

                with col2:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
                    st.markdown("**⚠️ Danger Zone**")
                    confirm = st.checkbox("I confirm I want to delete this student")
                    if st.button("🗑️ Delete Student", disabled=not confirm):
                        db.delete_student(selected_id)
                        st.success(f"✅ Student ID {selected_id} deleted.")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
