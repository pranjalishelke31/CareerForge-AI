# 🚀 CareerForge AI

> **An AI-powered career guidance platform for engineering students.**  
> Analyze your academic profile, discover career paths, identify skill gaps, and get a personalized learning roadmap — powered by Python, MySQL, Scikit-learn, and Google Gemini.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Folder Structure](#folder-structure)
- [Database Schema](#database-schema)
- [Setup Instructions](#setup-instructions)
- [Features by Phase](#features-by-phase)
- [How Each File Works](#how-each-file-works)
- [API Keys](#api-keys)

---

## 🎯 Project Overview

CareerForge AI helps engineering students answer three critical questions:

1. **What career suits me?** → Skill-based career matching using ML
2. **What am I missing?** → Skill gap analysis with visual charts
3. **How do I get there?** → Phase-by-phase personalized learning roadmap

---

## 🏗️ Architecture

```
User (Browser)
     │
     ▼
┌─────────────────────┐
│   Streamlit UI      │  app.py + pages/*.py
│   (Web Frontend)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Python Backend    │  database.py + recommendation.py
│   (Business Logic)  │
└─────────┬───────────┘
          │
     ┌────┴────┐
     ▼         ▼
┌─────────┐ ┌──────────────────────┐
│  MySQL  │ │  Recommendation      │
│  DB     │ │  Engine              │
│         │ │  ├─ Jaccard (Phase 2)│
└─────────┘ │  ├─ TF-IDF (Phase 3) │
            │  └─ Gemini (Phase 4) │
            └──────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Streamlit | Rapid Python-native web UI |
| Backend | Python 3.11+ | Core language |
| Database | MySQL | Relational data, SQL skills |
| Data | Pandas + NumPy | DataFrames, numerical ops |
| ML | Scikit-learn | TF-IDF, cosine similarity |
| Visualization | Plotly | Interactive charts |
| AI | Google Gemini | LLM chatbot |
| Config | python-dotenv | Secret management |

---

## 📁 Folder Structure

```
careerforge_ai/
│
├── app.py                 # Streamlit entry point, DB init, home page
├── database.py            # All MySQL operations (CRUD functions)
├── recommendation.py      # Recommendation algorithms (Jaccard, TF-IDF, roadmap)
│
├── pages/
│   ├── 1_Register.py      # Student registration & profile management
│   ├── 2_Skills.py        # Skill management (add/remove)
│   ├── 3_Careers.py       # Career browser with charts
│   ├── 4_SkillGap.py      # Skill gap analysis & radar chart
│   ├── 5_Roadmap.py       # ML recommendations + learning roadmap
│   └── 6_AIMentor.py      # Gemini AI career chatbot
│
├── models/
│   └── .gitkeep           # Trained ML models stored here (Phase 3)
│
├── .env                   # 🔒 Secret config (NOT committed to git)
├── .gitignore             # Excludes .env, __pycache__, venv/
├── requirements.txt       # All Python dependencies
└── README.md              # This file
```

---

## 🗄️ Database Schema

```sql
careerforge_ai
│
├── students           (student_id PK, name, branch, cgpa, country, career_goal)
├── skills             (skill_id PK, skill_name UNIQUE)
├── student_skills     (student_id FK, skill_id FK)  ← Many-to-many
├── careers            (career_id PK, career_name, description)
└── career_skills      (career_id FK, skill_id FK)   ← Many-to-many
```

---

## ⚡ Setup Instructions

### Prerequisites
- Python 3.11+
- MySQL 8.0+ installed and running
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/careerforge_ai.git
cd careerforge_ai
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Edit `.env` with your MySQL credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=careerforge_ai
GEMINI_API_KEY=your_gemini_key_here
```

### Step 5: Initialize the Database
```bash
python database.py
```
This creates all tables and seeds career + skill data automatically.

### Step 6: Run the App
```bash
streamlit run app.py
```
Open your browser at: `http://localhost:8501`

---

## 📦 Features by Phase

### ✅ Phase 1 — Foundation
- Student registration form (Create, Read, Update, Delete)
- Skill management (add from catalog or custom)
- Career browser with descriptions and skill tags
- Interactive charts (skills heatmap, most in-demand skills)

### ✅ Phase 2 — Rule-Based Recommendations
- Jaccard similarity career matching
- Ranked career recommendations with match scores
- Skill gap analysis with radar chart visualization
- Priority missing skills list

### ✅ Phase 3 — Machine Learning
- TF-IDF + Cosine Similarity recommendations
- Personalized 3-phase learning roadmap
- Gantt-style timeline visualization
- Free resource recommendations per skill

### ✅ Phase 4 — AI Career Mentor
- Conversational AI using Google Gemini
- System prompt personalized with student profile
- Streaming responses
- Quick question prompts
- Full conversation history

---

## 📖 How Each File Works

### `database.py`
The data access layer. Contains every SQL query in the project.
- `initialize_database()` — Creates DB, tables, seeds data
- `create_student()` — INSERT a new student
- `get_all_students()` → Pandas DataFrame
- `add_student_skill()` — Adds skill to student (handles duplicates)
- `get_all_career_skill_map()` → `{career: [skills]}` dict

### `recommendation.py`
The intelligence layer. Contains all recommendation algorithms.
- `jaccard_similarity(A, B)` → float [0-1]
- `get_career_recommendations(student_id)` → ranked DataFrame
- `get_skill_gap(student_id, career)` → gap analysis dict
- `get_ml_recommendations(student_id)` → TF-IDF ranked DataFrame
- `generate_roadmap(student_id, career)` → phased roadmap list

### `app.py`
The Streamlit entry point and home page.
- Sets global page config and CSS
- Initializes DB via `@st.cache_resource`
- Renders hero, features, and architecture overview

### `pages/1_Register.py`
Full CRUD for student profiles using Streamlit tabs.

### `pages/2_Skills.py`
Skill management — categorized catalog + custom skill entry.

### `pages/3_Careers.py`
Career browser with Plotly bar charts.

### `pages/4_SkillGap.py`
Gap analysis with Plotly radar chart and priority skill list.

### `pages/5_Roadmap.py`
ML recommendations + phased roadmap + Gantt timeline.

### `pages/6_AIMentor.py`
Gemini-powered conversational career mentor with streaming.

---

## 🔑 API Keys

### Google Gemini (Free)
1. Visit [https://ai.google.dev/](https://ai.google.dev/)
2. Click "Get API key in Google AI Studio"
3. No credit card required — generous free tier
4. Add to `.env`: `GEMINI_API_KEY=your_key_here`

---

## 📚 Algorithms Used

### Jaccard Similarity (Phase 2)
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```
Simple set overlap metric. Explainable and fast. No training needed.

### TF-IDF + Cosine Similarity (Phase 3)
```
TF-IDF weight = TF(skill) × log(N / DF(skill))
Cosine(A, B) = (A · B) / (|A| × |B|)
```
Weights rare skills higher. Better personalization than Jaccard.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use for learning and personal projects.

---

*Built with ❤️ for engineering students. CareerForge AI — Flagship AI/Data Science Project*
