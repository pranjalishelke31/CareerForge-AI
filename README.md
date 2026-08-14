# 🚀 CareerForge AI

<div align="center">

![CareerForge AI](https://img.shields.io/badge/CareerForge-AI%20Career%20Guidance-7c3aed?style=for-the-badge&logo=rocket&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**An AI-powered career guidance platform built for engineering students.**  
Match your skills to careers, identify skill gaps, get an ML-powered learning roadmap,  
and chat with a Google Gemini AI mentor — all in one app.

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Folder Structure](#-folder-structure)
- [🗄️ Database Schema](#️-database-schema)
- [⚡ Quick Start](#-quick-start)
- [🔑 Environment Variables](#-environment-variables)
- [📖 How Each File Works](#-how-each-file-works)
- [📚 Algorithms Explained](#-algorithms-explained)
- [🌐 Supported Engineering Branches](#-supported-engineering-branches)
- [📸 Pages Overview](#-pages-overview)
- [🤝 Contributing](#-contributing)

---

## ✨ Features

CareerForge AI is built in **5 progressive phases**, each adding more intelligence:

| Phase | Feature | Technology |
|-------|---------|------------|
| **Phase 1** | Student profile + skill management (full CRUD) | Streamlit + MySQL |
| **Phase 2** | Rule-based career matching + skill gap analysis | Jaccard Similarity |
| **Phase 3** | ML recommendations + personalized roadmap | TF-IDF + Cosine Similarity |
| **Phase 4** | Conversational AI career mentor with streaming | Google Gemini 2.5 Flash |
| **Phase 5** | User authentication with secure password hashing | bcrypt + Session State |

### 🎯 What it solves for engineering students:
- **"What career suits me?"** → AI matches your skills to 35+ engineering career paths
- **"What am I missing?"** → Visual radar chart showing your skill gap per career
- **"How do I get there?"** → Phase-by-phase roadmap with free resources + Gantt timeline
- **"Who do I ask?"** → Gemini AI mentor that knows your full academic profile

---

## 🏗️ Architecture

```
User (Browser)
     │
     ▼
┌──────────────────────────────────────┐
│         Streamlit Web UI             │
│   app.py + pages/  (8 pages)         │
│   Premium dark-glass design system   │
└─────────────────┬────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────────────┐
│  database.py  │   │   recommendation.py   │
│  MySQL CRUD   │   │  ├─ Jaccard (Phase 2) │
│  Connection   │   │  ├─ TF-IDF (Phase 3)  │
│  Pool + Cache │   │  └─ Roadmap Generator │
└───────┬───────┘   └───────────────────────┘
        ▼
┌───────────────┐   ┌───────────────────────┐
│  MySQL DB     │   │   Google Gemini API   │
│  6 Tables     │   │   AI Mentor Chat      │
│  150+ skills  │   │   (llm_service.py)    │
│  35+ careers  │   └───────────────────────┘
└───────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.35+ | Python-native web UI |
| **Styling** | Vanilla CSS (injected) | Dark navy theme, glassmorphism |
| **Backend** | Python 3.11+ | Core application logic |
| **Database** | MySQL 8.0+ | Relational storage with connection pooling |
| **Driver** | mysql-connector-python | Direct SQL (Repository Pattern) |
| **Data** | Pandas + NumPy | DataFrames and numerical computing |
| **ML** | Scikit-learn | TF-IDF vectorizer + Cosine Similarity |
| **AI / LLM** | Google Gemini 2.5 Flash | Conversational career mentor |
| **Charts** | Plotly | Radar charts, bar charts, Gantt timelines |
| **Auth** | bcrypt | Adaptive password hashing |
| **Config** | python-dotenv | Secret management via `.env` |

---

## 📁 Folder Structure

```
careerforge_ai/
│
├── app.py                  # 🏠 Main entry point — home dashboard
├── auth.py                 # 🔐 Authentication (login/signup/session)
├── database.py             # 🗄️  All MySQL CRUD (Repository Pattern)
├── recommendation.py       # 🤖 Jaccard, TF-IDF, roadmap generator
├── llm_service.py          # 💬 Google Gemini API integration
├── theme.py                # 🎨 Shared CSS design system + sidebar
│
├── pages/
│   ├── 0_Login.py          # 🔑 Login page
│   ├── 0_Signup.py         # 📝 New account registration
│   ├── 1_Register.py       # 👤 Student profile CRUD
│   ├── 2_Skills.py         # 🧠 Branch-aware skill catalog
│   ├── 3_Careers.py        # 💼 Career browser + recommendations
│   ├── 4_SkillGap.py       # 📊 Skill gap radar chart analysis
│   ├── 5_Roadmap.py        # 🗺️  ML roadmap + Gantt timeline
│   └── 6_AIMentor.py       # 🤖 Google Gemini AI chatbot
│
├── models/
│   └── .gitkeep            # ML model storage
│
├── .env                    # 🔒 Secrets — NOT committed to Git
├── .gitignore              # Excludes .env, venv/, __pycache__
├── requirements.txt        # All Python dependencies
└── README.md               # This file
```

---

## 🗄️ Database Schema

```sql
careerforge_ai
│
├── users          (user_id PK, username, email, password_hash, created_at)
├── students       (student_id PK, name, branch, cgpa, country, career_goal)
├── skills         (skill_id PK, skill_name UNIQUE)
├── student_skills (student_id FK, skill_id FK)   ← Many-to-Many
├── careers        (career_id PK, career_name UNIQUE, description)
└── career_skills  (career_id FK, skill_id FK)    ← Many-to-Many
```

**Key design decisions:**
- `users` (login credentials) is **separate** from `students` (academic profile)
- `ON DELETE CASCADE` — deleting a student removes all skill links automatically
- **Connection pooling** (`pool_size=5`) — reuses TCP connections instead of creating new ones per query
- **`@st.cache_data`** on all heavy reads — 30s–5min cache eliminates repeated DB round-trips
- Seed data runs **only once** — skipped automatically if data already exists

---

## ⚡ Quick Start

### Prerequisites
- Python **3.11+**
- MySQL **8.0+** running locally
- A free [Google Gemini API key](https://ai.google.dev/)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/careerforge-ai.git
cd careerforge-ai
```

### 2. Create & activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root folder:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=careerforge_ai
GEMINI_API_KEY=your_gemini_api_key_here
```

> 💡 **Free Gemini key:** [ai.google.dev](https://ai.google.dev/) → "Get API key in Google AI Studio" — no credit card needed.

### 5. Initialize the database
```bash
python database.py
```
Automatically creates the database, all 6 tables, and seeds **150+ skills** + **35+ career paths**.

### 6. Run the app
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser 🎉

---

## 🔑 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | `mypassword` |
| `DB_NAME` | Database name | `careerforge_ai` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |

> ⚠️ **Never commit your `.env` file.** It is already excluded in `.gitignore`.

---

## 📖 How Each File Works

### `database.py` — Data Layer
All SQL lives here (Repository Pattern). No raw queries in any other file.
- `initialize_database()` — creates DB + tables + seeds data (smart skip if exists)
- `get_all_students()` — DataFrame of all students (cached 30s)
- `get_student_skills(id)` — student's skill list (cached 30s, cleared on writes)
- `get_all_career_skill_map()` — `{career: [skills]}` dict (cached 5 min)

### `recommendation.py` — Intelligence Layer
- `jaccard_similarity(A, B)` → float — fast set overlap metric
- `get_career_recommendations(id)` → careers ranked by Jaccard score
- `get_skill_gap(id, career)` → matched, missing, and priority skills
- `get_ml_recommendations(id)` → careers ranked by TF-IDF cosine similarity
- `generate_roadmap(id, career)` → 3-phase plan with resources + time estimates

### `auth.py` — Security Layer
- `signup()` — bcrypt-hashes the password before storing
- `login()` — verifies bcrypt hash, saves user to `st.session_state`
- `require_login()` — redirects unauthenticated users to the login page
- `logout()` — clears session state

### `llm_service.py` — AI Layer
- Initializes Google Gemini client from `.env`
- Builds a **personalized system prompt** with the student's branch, CGPA, skills, and career goal
- Handles **streaming responses** for real-time chat feel

### `theme.py` — Design Layer
- `_GLOBAL_CSS` — 600+ lines of dark-glass premium CSS
- `inject_global_css()` — injects CSS + renders sidebar on every page
- `render_sidebar()` — user avatar, navigation, platform stats, logout button

---

## 📚 Algorithms Explained

### Jaccard Similarity (Phase 2 — Career Matching)
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|

Example:
  Student skills:         {Python, SQL, Pandas}
  Data Scientist needs:   {Python, SQL, TensorFlow, Pandas, ML}
  Intersection (∩):       {Python, SQL, Pandas}  → 3
  Union (∪):              {Python, SQL, TensorFlow, Pandas, ML} → 5
  Score:                  3/5 = 60%
```
✅ Simple, explainable, no training data needed

### TF-IDF + Cosine Similarity (Phase 3 — ML Recommendations)
```
TF-IDF weight = TF(skill) × log(N / DF(skill))
Cosine(A, B)  = (A · B) / (‖A‖ × ‖B‖)
```
✅ Weights rare/specific skills higher (e.g. "RTOS" > "Python" for ENTC roles)  
✅ Better personalization than Jaccard

### Roadmap Generator — Topological Skill Ordering
```
Phase 1 (Foundation): Skills with no missing prerequisites
Phase 2 (Core):       Skills whose prerequisites are in Phase 1
Phase 3 (Advanced):   All remaining advanced skills
```

---

## 🌐 Supported Engineering Branches

Branch-specific skill catalogs and career paths for:

| Branch | Sample Careers |
|--------|----------------|
| 💻 Computer Science & Engineering | Data Scientist, ML Engineer, DevOps |
| 🖥️ Information Technology | Backend Developer, Cloud Architect |
| 📡 Electronics & Telecommunication | VLSI Engineer, IoT Developer, RF Engineer |
| ⚙️ Mechanical Engineering | CAE Analyst, Mechanical Design, HVAC |
| 🏗️ Civil Engineering | Structural Engineer, GIS Analyst, Urban Planner |
| ⚡ Electrical Engineering | Power Systems, Automation, Renewable Energy |
| ⚗️ Chemical Engineering | Process Engineer, Quality Assurance |
| 🛩️ Aerospace Engineering | FEA Analyst, CFD Specialist |
| 🔬 Biomedical / Biotechnology | Bioinformatics, Medical Device Design |

---

## 📸 Pages Overview

| Page | What It Does |
|------|-------------|
| 🏠 **Home** | Welcome hero, quick stats, feature navigation tiles |
| 🔑 **Login / Signup** | Secure auth with bcrypt password hashing |
| 👤 **Register Profile** | Create, view, edit, delete student profiles |
| 🧠 **Skills** | Branch-aware catalog + custom skills + recommendations |
| 💼 **Careers** | Browse 35+ careers, Jaccard match %, skill tags, heatmap |
| 📊 **Skill Gap** | Radar chart, matched vs missing, priority learn list |
| 🗺️ **Roadmap** | ML career ranking + phased roadmap + Gantt timeline |
| 🤖 **AI Mentor** | Chat with Gemini AI using your full student profile |

---

## 🤝 Contributing

Contributions are welcome!

1. **Fork** this repository
2. **Create** your feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "✨ Add amazing feature"
   ```
4. **Push** and open a Pull Request
   ```bash
   git push origin feature/amazing-feature
   ```

### Ideas for future features
- [ ] Resume / CV PDF generator
- [ ] LinkedIn skills import integration
- [ ] More engineering branches (Marine, Mining, etc.)
- [ ] Job listings API (LinkedIn / Naukri)
- [ ] Email notifications for roadmap milestones

---

## 📄 License

MIT License — free to use for learning, personal projects, and portfolio showcasing.

---

<div align="center">

**⭐ If this project helped you, please give it a star on GitHub! ⭐**

*Built with ❤️ for engineering students — CareerForge AI*

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)
[![Gemini](https://img.shields.io/badge/Gemini%20AI-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)

</div>
