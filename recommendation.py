# =============================================================================
# recommendation.py — Career Recommendation Engine
# =============================================================================
#
# WHAT THIS FILE DOES:
#   Phase 2: Rule-based recommendations using Jaccard Similarity
#   Phase 3: ML-based recommendations using Cosine Similarity (TF-IDF vectors)
#
# =============================================================================
# ALGORITHM EXPLANATION — JACCARD SIMILARITY (Phase 2)
# =============================================================================
# Jaccard Similarity measures the overlap between two SETS.
#
#   Jaccard(A, B) = |A ∩ B| / |A ∪ B|
#
#   Where:
#       A = set of student's skills       e.g., {"Python", "SQL", "Pandas"}
#       B = set of career's required skills e.g., {"Python", "SQL", "TensorFlow", "Pandas", "ML"}
#       A ∩ B = skills in BOTH sets       e.g., {"Python", "SQL", "Pandas"} → 3 items
#       A ∪ B = skills in EITHER set      e.g., {"Python", "SQL", "Pandas", "TF", "ML"} → 5 items
#       Jaccard = 3/5 = 0.60 = 60% match
#
# Range: 0.0 (no overlap) to 1.0 (perfect match)
# Advantage: Simple, explainable, no training data needed
# Disadvantage: Doesn't consider skill importance or weighting
#
# =============================================================================
# ALGORITHM EXPLANATION — COSINE SIMILARITY (Phase 3)
# =============================================================================
# Cosine Similarity measures the angle between two vectors.
# We represent each skill set as a binary vector:
#   e.g., ["Python", "SQL", "TF"] → [1, 1, 0, 0, 1, 0, ...]
#
# Two vectors pointing in the same direction → similarity = 1.0
# Two vectors at 90° → similarity = 0.0
#
# More sophisticated than Jaccard because we use TF-IDF weighting,
# which gives rare/specific skills more importance than common ones.
# =============================================================================

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib   # For saving/loading the trained model
import os
import database as db


# =============================================================================
# PHASE 2: JACCARD SIMILARITY RECOMMENDATION
# =============================================================================

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Computes Jaccard Similarity between two sets.

    Args:
        set_a: Student's skills
        set_b: Career's required skills

    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    # Convert to lowercase sets for case-insensitive comparison
    a = {s.lower() for s in set_a}
    b = {s.lower() for s in set_b}

    intersection = len(a & b)  # Skills in BOTH sets (& is set intersection)
    union        = len(a | b)  # Skills in EITHER set (| is set union)

    if union == 0:
        return 0.0

    return intersection / union


def get_career_recommendations(student_id: int) -> pd.DataFrame:
    """
    Returns a DataFrame of careers sorted by Jaccard similarity to the student's skills.

    The recommendation engine works as follows:
    1. Fetch the student's skills from the DB
    2. Fetch all career → required skills mappings from the DB
    3. Compute Jaccard similarity for each career
    4. Sort by similarity score (descending)
    5. Return the ranked list

    Returns:
        pd.DataFrame with columns:
            career_name, description, match_score, matched_skills,
            missing_skills, total_required, match_percent
    """
    # Step 1: Get student's skills
    student_skills = set(db.get_student_skills(student_id))

    if not student_skills:
        # Return empty DataFrame if no skills added
        return pd.DataFrame()

    # Step 2: Get all career skill requirements
    career_skill_map = db.get_all_career_skill_map()
    careers_df = db.get_all_careers()

    # Step 3: Compute scores for each career
    results = []
    for _, career_row in careers_df.iterrows():
        career_name = career_row["career_name"]
        career_desc = career_row["description"]
        required_skills = set(career_skill_map.get(career_name, []))

        if not required_skills:
            continue

        # Compute Jaccard similarity
        score = jaccard_similarity(student_skills, required_skills)

        # Also compute absolute matches (for explanation)
        matched  = student_skills & required_skills     # Skills student has AND career needs
        missing  = required_skills - student_skills     # Skills career needs but student lacks

        results.append({
            "career_name":     career_name,
            "description":     career_desc,
            "match_score":     score,
            "match_percent":   round(score * 100, 1),
            "matched_skills":  sorted(matched),         # Sort for consistent display
            "missing_skills":  sorted(missing),
            "total_required":  len(required_skills),
            "skills_matched":  len(matched),
            "skills_missing":  len(missing),
        })

    # Step 4: Sort by match_score descending
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("match_score", ascending=False).reset_index(drop=True)
    results_df["rank"] = results_df.index + 1  # 1-based ranking

    return results_df


# =============================================================================
# PHASE 2: SKILL GAP ANALYSIS
# =============================================================================

def get_skill_gap(student_id: int, career_name: str) -> dict:
    """
    Analyzes the gap between a student's skills and a specific career's requirements.

    Returns a dictionary with:
        - matched_skills: skills the student already has
        - missing_skills: skills they need to acquire
        - match_percent: how complete they are for this career
        - priority_missing: top priority skills to learn next
    """
    student_skills   = set(db.get_student_skills(student_id))
    # Fetch once and reuse for both required_skills lookup AND priority scoring
    career_skill_map = db.get_all_career_skill_map()
    required_skills  = set(career_skill_map.get(career_name, []))

    matched  = student_skills & required_skills
    missing  = required_skills - student_skills
    extra    = student_skills - required_skills  # Skills student has that aren't required

    # Priority scoring: skills that appear in MORE careers are more valuable
    # Reuse career_skill_map — no second DB call needed
    skill_frequency = {}
    for skills_list in career_skill_map.values():
        for skill in skills_list:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1

    # Sort missing skills by how commonly they appear across all careers
    priority_missing = sorted(
        missing,
        key=lambda s: skill_frequency.get(s, 0),
        reverse=True  # Most common skills first
    )

    match_percent = (len(matched) / len(required_skills) * 100) if required_skills else 0

    return {
        "career_name":      career_name,
        "matched_skills":   sorted(matched),
        "missing_skills":   sorted(missing),
        "extra_skills":     sorted(extra),
        "priority_missing": priority_missing,
        "match_percent":    round(match_percent, 1),
        "total_required":   len(required_skills),
        "skills_matched":   len(matched),
        "skills_missing":   len(missing),
    }


# =============================================================================
# PHASE 3: ML-BASED RECOMMENDATION (Cosine Similarity with TF-IDF)
# =============================================================================

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "career_recommender.pkl")


def skills_to_text(skills: list[str]) -> str:
    """
    Converts a list of skills into a single space-separated string.
    This is the input format TF-IDF vectorizer expects.

    Example: ["Python", "SQL", "Machine Learning"] → "Python SQL Machine_Learning"
    """
    return " ".join(skill.replace(" ", "_") for skill in skills)


def get_ml_recommendations(student_id: int) -> pd.DataFrame:
    """
    Uses TF-IDF + Cosine Similarity to recommend careers.

    HOW IT WORKS:
    1. Build a "document" for each career: its skills as text
    2. Build a "query document" for the student: their skills as text
    3. TF-IDF vectorizer converts all documents to numeric vectors
    4. Cosine similarity finds which career vectors are closest to the student vector
    5. Sort by cosine similarity score

    WHY TF-IDF OVER JACCARD?
    - TF-IDF gives higher weight to RARE skills (e.g., "RTOS" is more
      discriminative than "Python" which everyone has)
    - Cosine similarity handles different-length skill lists better than Jaccard
    """
    student_skills = db.get_student_skills(student_id)
    career_skill_map = db.get_all_career_skill_map()
    careers_df = db.get_all_careers()

    if not student_skills:
        return pd.DataFrame()

    # Build corpus: one "document" per career + one for the student
    career_names = list(career_skill_map.keys())
    career_docs  = [skills_to_text(career_skill_map[c]) for c in career_names]
    student_doc  = skills_to_text(student_skills)

    # All documents together (student first, then careers)
    all_docs = [student_doc] + career_docs

    # TF-IDF Vectorizer
    # TF-IDF = Term Frequency × Inverse Document Frequency
    # - TF: how often a skill appears in this career's skill list
    # - IDF: log(total_careers / careers_that_need_this_skill)
    #   → Rare skills get higher IDF weight
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    # tfidf_matrix shape: (1 + num_careers, num_unique_skills)

    # Compute cosine similarity between student (row 0) and each career
    student_vector = tfidf_matrix[0]       # Row 0 = student
    career_vectors = tfidf_matrix[1:]      # Rows 1..N = careers

    # cosine_similarity returns a matrix; [0] gives us the 1D array of scores
    similarities = cosine_similarity(student_vector, career_vectors)[0]

    # Build results DataFrame
    results = []
    for idx, career_name in enumerate(career_names):
        required_skills = set(career_skill_map[career_name])
        student_set     = set(student_skills)
        matched  = student_set & required_skills
        missing  = required_skills - student_set

        career_row = careers_df[careers_df["career_name"] == career_name]
        desc = career_row["description"].values[0] if not career_row.empty else ""

        results.append({
            "career_name":    career_name,
            "description":    desc,
            "ml_score":       float(similarities[idx]),
            "match_percent":  round(float(similarities[idx]) * 100, 1),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "skills_matched": len(matched),
            "skills_missing": len(missing),
            "total_required": len(required_skills),
        })

    df = pd.DataFrame(results)
    df = df.sort_values("ml_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


# =============================================================================
# PHASE 3: PERSONALIZED LEARNING ROADMAP GENERATOR
# =============================================================================

def generate_roadmap(student_id: int, target_career: str) -> list[dict]:
    """
    Generates a step-by-step learning roadmap for a student targeting a specific career.

    ROADMAP LOGIC:
    1. Identify all missing skills for the target career
    2. Group skills into learning phases based on prerequisites
    3. Assign estimated learning time per skill
    4. Add resource suggestions for each skill

    Returns a list of phases, each with:
        - phase_number: 1, 2, 3, ...
        - phase_name: e.g., "Foundation", "Core Skills", "Advanced"
        - skills: list of skills to learn in this phase
        - duration_weeks: estimated weeks
        - resources: list of recommended resources
    """
    gap = get_skill_gap(student_id, target_career)
    missing = gap["priority_missing"]

    if not missing:
        return []  # Student is already ready for this career!

    # Skill → estimated learning time in weeks
    skill_durations = {
        "Python": 4,           "SQL": 3,             "Java": 6,
        "C++": 6,              "JavaScript": 4,       "R": 4,
        "Machine Learning": 8, "Deep Learning": 10,   "Data Analysis": 4,
        "Statistics": 5,       "TensorFlow": 6,       "PyTorch": 6,
        "Scikit-learn": 3,     "Pandas": 2,           "NumPy": 2,
        "Natural Language Processing": 8, "Computer Vision": 8,
        "Docker": 3,           "Kubernetes": 4,       "Git": 1,
        "AWS": 5,              "Google Cloud": 5,     "Azure": 5,
        "Linux": 3,            "MySQL": 2,            "PostgreSQL": 2,
        "MongoDB": 2,          "Django": 4,           "Flask": 3,
        "FastAPI": 3,          "REST API": 3,         "CI/CD": 3,
        "Cybersecurity": 8,    "Networking": 5,       "Ethical Hacking": 8,
        "Cryptography": 5,     "Embedded C": 6,       "Arduino": 4,
        "RTOS": 6,             "VHDL": 6,             "PCB Design": 6,
        "Data Visualization": 2,
    }

    # Skill → free learning resources
    skill_resources = {
        "Python":              ["Python.org Tutorial", "Automate the Boring Stuff (free book)", "freeCodeCamp Python Course"],
        "SQL":                 ["SQLZoo", "Mode Analytics SQL Tutorial", "W3Schools SQL"],
        "Machine Learning":    ["Andrew Ng's ML Course (Coursera)", "fast.ai", "Kaggle ML Course"],
        "Deep Learning":       ["Deep Learning Specialization (Coursera)", "fast.ai Practical DL"],
        "TensorFlow":          ["TensorFlow Official Tutorials", "Google's TF Developer Certificate"],
        "PyTorch":             ["PyTorch Official Tutorials", "fast.ai"],
        "Scikit-learn":        ["Scikit-learn Docs", "Kaggle Learn"],
        "Pandas":              ["Pandas Official Docs", "Kaggle Pandas Course"],
        "Docker":              ["Docker Official Getting Started", "Play with Docker"],
        "AWS":                 ["AWS Free Tier + Tutorials", "AWS Skill Builder"],
        "Git":                 ["Git SCM Book (free)", "GitHub Learning Lab"],
        "Linux":               ["Linux Journey", "The Linux Command Line (book)"],
        "Django":              ["Django Official Tutorial (polls app)", "Mozilla MDN Django"],
        "Flask":               ["Flask Official Docs", "CS50 Web (Flask section)"],
        "Cybersecurity":       ["TryHackMe", "Hack The Box", "CompTIA Security+ resources"],
        "Networking":          ["Professor Messer's CompTIA Network+", "Cisco NetAcad"],
        "Data Visualization":  ["Matplotlib Tutorials", "Plotly Docs", "Seaborn Gallery"],
        "Statistics":          ["Khan Academy Statistics", "StatQuest (YouTube)"],
    }

    # Skill → prerequisite skills (simplified)
    prerequisites = {
        "Machine Learning":    ["Python", "Statistics", "NumPy", "Pandas"],
        "Deep Learning":       ["Machine Learning", "TensorFlow"],
        "TensorFlow":          ["Python", "Machine Learning"],
        "PyTorch":             ["Python", "Machine Learning"],
        "Scikit-learn":        ["Python", "Statistics"],
        "Natural Language Processing": ["Python", "Machine Learning"],
        "Computer Vision":     ["Python", "Deep Learning"],
        "Django":              ["Python", "SQL"],
        "Flask":               ["Python"],
        "FastAPI":             ["Python"],
        "Kubernetes":          ["Docker"],
        "CI/CD":               ["Git", "Docker"],
        "Ethical Hacking":     ["Networking", "Linux", "Python"],
        "AWS":                 ["Linux", "Networking"],
    }

    # Sort missing skills into phases using topological ordering
    # Phase 1: Foundation (no prerequisites in missing list)
    # Phase 2: Core (prerequisites are in Phase 1 or already known)
    # Phase 3: Advanced (all others)

    student_skills = set(db.get_student_skills(student_id))
    missing_set = set(missing)

    phase1, phase2, phase3 = [], [], []

    for skill in missing:
        skill_prereqs = set(prerequisites.get(skill, []))
        unmet_prereqs = skill_prereqs & missing_set  # Prereqs that are ALSO missing

        if not unmet_prereqs:
            phase1.append(skill)  # No missing prerequisites → foundation skill
        elif unmet_prereqs.issubset(set(phase1)):
            phase2.append(skill)  # All prereqs are in phase 1 → core skill
        else:
            phase3.append(skill)  # Advanced

    roadmap = []

    if phase1:
        total_weeks = sum(skill_durations.get(s, 3) for s in phase1)
        roadmap.append({
            "phase_number":  1,
            "phase_name":    "🏗️ Foundation",
            "phase_desc":    "Build the foundational skills required for this career.",
            "skills":        phase1,
            "duration_weeks": total_weeks,
            "resources": [
                res
                for skill in phase1
                for res in skill_resources.get(skill, [f"Search '{skill} tutorial' on YouTube / Coursera"])[:2]
            ][:6]  # Max 6 resources
        })

    if phase2:
        total_weeks = sum(skill_durations.get(s, 3) for s in phase2)
        roadmap.append({
            "phase_number":  2,
            "phase_name":    "⚙️ Core Skills",
            "phase_desc":    "Build the core technical skills central to this career.",
            "skills":        phase2,
            "duration_weeks": total_weeks,
            "resources": [
                res
                for skill in phase2
                for res in skill_resources.get(skill, [f"Search '{skill} tutorial' on YouTube / Coursera"])[:2]
            ][:6]
        })

    if phase3:
        total_weeks = sum(skill_durations.get(s, 3) for s in phase3)
        roadmap.append({
            "phase_number":  3,
            "phase_name":    "🚀 Advanced",
            "phase_desc":    "Master advanced specialization skills to stand out.",
            "skills":        phase3,
            "duration_weeks": total_weeks,
            "resources": [
                res
                for skill in phase3
                for res in skill_resources.get(skill, [f"Search '{skill} tutorial' on YouTube / Coursera"])[:2]
            ][:6]
        })

    return roadmap
