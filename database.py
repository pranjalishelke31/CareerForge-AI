# =============================================================================
# database.py — The Database Brain of CareerForge AI
# =============================================================================
#
# WHAT THIS FILE DOES:
#   1. Connects Python to MySQL using credentials from .env
#   2. Creates all 5 tables if they don't already exist (safe to run many times)
#   3. Seeds the database with career paths and skills data
#   4. Provides helper functions for all database operations (CRUD)
#
# DESIGN PRINCIPLE:
#   All SQL lives here. No other file writes raw SQL queries.
#   This is called the "Repository Pattern" — one place for all data access.
#   If you change the DB schema, you only need to update THIS file.
#
# KEY CONCEPT — Connection Pooling:
#   Opening a new database connection for every query is slow.
#   A "connection pool" keeps a set of connections open and reuses them.
#   mysql.connector's pooling handles this automatically.
# =============================================================================

import os                          # Access environment variables
import mysql.connector             # MySQL driver for Python
from mysql.connector import pooling  # Connection pool manager
from dotenv import load_dotenv     # Load .env file into os.environ
import pandas as pd                # DataFrame — our main data structure
import streamlit as st             # For @st.cache_data

# ---------------------------------------------------------------------------
# Step 1: Load environment variables from .env file
# ---------------------------------------------------------------------------
# load_dotenv() reads the .env file line by line and sets each one as an
# environment variable accessible via os.getenv().
load_dotenv()

# ---------------------------------------------------------------------------
# Step 2: Build the database configuration dictionary
# ---------------------------------------------------------------------------
# We read each setting from the environment — NOT hardcoded.
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),  # Default: localhost
    "port":     int(os.getenv("DB_PORT", 3306)),    # Default: 3306
    "user":     os.getenv("DB_USER", "root"),        # Default: root
    "password": os.getenv("DB_PASSWORD", ""),        # No default for password
    "database": os.getenv("DB_NAME", "careerforge_ai"),
    "autocommit": True,  # Each query commits automatically (no manual commit needed)
}

# ---------------------------------------------------------------------------
# Step 3: Create the connection pool (runs once when this module is imported)
# ---------------------------------------------------------------------------
# pool_size=5 means up to 5 simultaneous connections.
# This is more than enough for a single-user Streamlit app.
# For production with 100+ users, you'd increase this.
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="careerforge_pool",
        pool_size=5,
        **DB_CONFIG
    )
    print("✅ Database connection pool created successfully.")
except mysql.connector.Error as e:
    print(f"❌ Failed to create connection pool: {e}")
    connection_pool = None


# ---------------------------------------------------------------------------
# Helper: Get a connection from the pool
# ---------------------------------------------------------------------------
def get_connection():
    """
    Returns a MySQL connection from the pool.
    Always use this inside a 'with' statement or call .close() when done.

    WHY POOL?
    Instead of:  connection = mysql.connector.connect(...)  [slow — new TCP connection]
    We do:       connection = get_connection()              [fast — reuse existing]
    """
    if connection_pool is None:
        raise ConnectionError("Database pool not initialized. Check your .env credentials.")
    return connection_pool.get_connection()


# =============================================================================
# SCHEMA CREATION — Run once to set up tables
# =============================================================================

def create_database_if_not_exists():
    """
    Creates the 'careerforge_ai' database if it doesn't exist.
    This runs BEFORE the pool (which needs the DB to exist first).
    """
    # Connect WITHOUT specifying a database name
    temp_config = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**temp_config)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS careerforge_ai")
    cursor.close()
    conn.close()
    print("✅ Database 'careerforge_ai' ready.")


def create_tables():
    """
    Creates all 5 tables using IF NOT EXISTS — safe to call multiple times.

    TABLE RELATIONSHIPS:
        students ←──── student_skills ────→ skills
        careers  ←──── career_skills  ────→ skills

    The 'student_skills' and 'career_skills' are JUNCTION TABLES.
    They represent Many-to-Many relationships:
    - One student can have many skills, one skill can belong to many students.
    - One career needs many skills, one skill can appear in many careers.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Table 1: students ---
    # Stores the student's academic profile.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   INT AUTO_INCREMENT PRIMARY KEY,
            name         VARCHAR(100)  NOT NULL,
            branch       VARCHAR(100)  NOT NULL,
            cgpa         DECIMAL(3,1)  NOT NULL,
            country      VARCHAR(100)  NOT NULL,
            career_goal  VARCHAR(255),
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Table 2: skills ---
    # Master list of all skills in the system.
    # UNIQUE on skill_name prevents duplicate entries.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id    INT AUTO_INCREMENT PRIMARY KEY,
            skill_name  VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    # --- Table 3: student_skills (Junction) ---
    # Links students to their skills.
    # Composite PRIMARY KEY (student_id, skill_id) prevents a student
    # from adding the same skill twice.
    # ON DELETE CASCADE: if a student is deleted, their skill mappings are too.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_skills (
            student_id  INT NOT NULL,
            skill_id    INT NOT NULL,
            PRIMARY KEY (student_id, skill_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id)   REFERENCES skills(skill_id)     ON DELETE CASCADE
        )
    """)

    # --- Table 4: careers ---
    # Master list of all career paths in the system.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS careers (
            career_id    INT AUTO_INCREMENT PRIMARY KEY,
            career_name  VARCHAR(100) NOT NULL UNIQUE,
            description  TEXT
        )
    """)

    # --- Table 5: career_skills (Junction) ---
    # Defines which skills each career requires.
    # This is the core data the recommendation engine reads.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_skills (
            career_id   INT NOT NULL,
            skill_id    INT NOT NULL,
            PRIMARY KEY (career_id, skill_id),
            FOREIGN KEY (career_id) REFERENCES careers(career_id)  ON DELETE CASCADE,
            FOREIGN KEY (skill_id)  REFERENCES skills(skill_id)    ON DELETE CASCADE
        )
    """)

    # --- Table 6: users (Phase 5 — Authentication) ---
    # Stores registered user accounts with bcrypt-hashed passwords.
    # This is SEPARATE from the students table:
    #   - 'users'    = login credentials (who you are)
    #   - 'students' = academic profile  (your career data)
    # One user account can be linked to one or more student profiles in future.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INT AUTO_INCREMENT PRIMARY KEY,
            username      VARCHAR(100)  NOT NULL,
            email         VARCHAR(150)  NOT NULL UNIQUE,
            password_hash VARCHAR(255)  NOT NULL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.close()
    conn.close()
    print("✅ All tables created successfully (including users table).")


# =============================================================================
# SEED DATA — Pre-populate careers and skills
# =============================================================================

def seed_data():
    """
    Seeds the database with career paths and skills for ALL engineering branches.
    Uses INSERT IGNORE to skip rows that already exist (idempotent — safe to run many times).

    BRANCHES COVERED:
      CS/IT, ENTC, Mechanical, Civil, Electrical, Chemical, Biomedical
    """
    conn = get_connection()
    cursor = conn.cursor()

    # =========================================================================
    # SKILLS MASTER LIST — 150+ skills across all engineering branches
    # =========================================================================
    skills = [
        # ── CS / IT ──────────────────────────────────────────────────────────
        # Programming Languages
        "Python", "Java", "C++", "JavaScript", "R", "Scala", "Go",
        # Data & ML
        "Machine Learning", "Deep Learning", "Data Analysis", "Statistics",
        "Natural Language Processing", "Computer Vision", "TensorFlow",
        "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Data Visualization",
        # Databases
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
        # Web & Backend
        "Django", "Flask", "FastAPI", "REST API", "GraphQL", "HTML", "CSS",
        # Cloud & DevOps
        "AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "CI/CD", "Git",
        # Networking & Security
        "Cybersecurity", "Networking", "Linux", "Ethical Hacking", "Cryptography",

        # ── ELECTRONICS & TELECOMMUNICATION (ENTC) ────────────────────────────
        # Digital Design & HDL
        "VLSI Design", "Verilog", "VHDL", "FPGA Programming", "Digital Electronics",
        # Embedded Systems
        "Embedded C", "Arduino", "Microcontrollers", "ARM Architecture", "RTOS",
        "Raspberry Pi", "ESP32", "IoT Development",
        # PCB & Hardware
        "PCB Design", "Altium Designer", "KiCad", "Soldering & Prototyping",
        # Signal Processing & Communication
        "Signal Processing", "Digital Communication", "Analog Electronics",
        "RF Design", "Antenna Design", "5G Technology", "Wireless Communication",
        # Simulation Tools
        "MATLAB", "Simulink", "LabVIEW",

        # ── MECHANICAL ENGINEERING ────────────────────────────────────────────
        # CAD / CAE Tools
        "SolidWorks", "AutoCAD", "CATIA", "ANSYS", "Fusion 360",
        "PTC Creo", "Siemens NX",
        # Simulation & Analysis
        "Finite Element Analysis (FEA)", "Computational Fluid Dynamics (CFD)",
        "Thermal Analysis", "Structural Analysis",
        # Manufacturing
        "CNC Programming", "Manufacturing Processes", "GD&T",
        "3D Printing / Additive Manufacturing", "Injection Molding",
        "Welding & Fabrication", "Sheet Metal Design",
        # Mechanical Engineering Fundamentals
        "Thermodynamics", "Fluid Mechanics", "Heat Transfer",
        "Machine Design", "Kinematics & Dynamics",
        # Industrial & Automation
        "Industrial Automation", "PLC Programming", "Robotics",
        "Hydraulics & Pneumatics", "Lean Manufacturing",

        # ── CIVIL ENGINEERING ─────────────────────────────────────────────────
        # Design Software
        "AutoCAD Civil 3D", "Revit (BIM)", "STAAD.Pro", "ETABS", "SAP2000",
        "Primavera P6", "MS Project",
        # Structural & Geotechnical
        "Structural Analysis", "Concrete Design", "Steel Design",
        "Geotechnical Engineering", "Foundation Design", "Soil Testing",
        # Surveying & GIS
        "Surveying", "GPS & GIS Mapping", "Remote Sensing", "Total Station",
        # Construction Management
        "Construction Management", "Estimation & Costing", "Project Scheduling",
        "Quality Control (Civil)", "Contract Management",
        # Environment & Water
        "Environmental Engineering", "Water Resources Engineering",
        "Waste Management", "Hydrology",

        # ── ELECTRICAL ENGINEERING ────────────────────────────────────────────
        "Power Systems Analysis", "Electrical Machines", "Power Electronics",
        "Control Systems", "PID Tuning", "Motor Drives",
        "SCADA Systems", "PLC & HMI", "Industrial Automation",
        "Renewable Energy Systems", "Solar PV Design", "Wind Energy",
        "ETAP", "PSCAD", "Electrical Design (AutoCAD Electrical)",
        "Protection & Relay Systems", "High Voltage Engineering",

        # ── CHEMICAL ENGINEERING ──────────────────────────────────────────────
        "Process Simulation (Aspen)", "Chemical Process Design",
        "Mass & Energy Balances", "Heat Exchanger Design",
        "Reactor Design", "Separation Processes", "Fluid Flow in Pipes",
        "HSE (Health, Safety & Environment)", "Piping & Instrumentation (P&ID)",
        "Quality Control (Chemical)", "Six Sigma",

        # ── BIOMEDICAL / BIOTECHNOLOGY ────────────────────────────────────────
        "Bioinformatics", "Medical Imaging", "Molecular Biology",
        "Cell Culture Techniques", "PCR & Gel Electrophoresis",
        "CRISPR Technology", "Drug Discovery", "Clinical Research",
        "Biomechanics", "Medical Device Design", "Regulatory Affairs (FDA/CE)",

        # ── CROSS-BRANCH / GENERAL ────────────────────────────────────────────
        "Microsoft Excel (Advanced)", "Technical Report Writing",
        "Project Management", "Research Methodology", "Literature Survey",
        "Python for Engineers", "Data Analysis with Excel",
        "Communication", "Problem Solving", "Team Collaboration",
        "Leadership", "Time Management", "Technical Presentation",
    ]

    cursor.executemany(
        "INSERT IGNORE INTO skills (skill_name) VALUES (%s)",
        [(s,) for s in skills]
    )

    # =========================================================================
    # CAREER PATHS — 30+ careers across all engineering branches
    # =========================================================================
    careers = [
        # ── CS / IT Careers (existing) ────────────────────────────────────────
        ("Data Scientist",
         "Analyzes complex datasets to extract insights and build predictive models. "
         "Works with Python, ML algorithms, and data visualization tools."),
        ("Machine Learning Engineer",
         "Builds, trains, and deploys machine learning models at scale. "
         "Bridges data science and software engineering."),
        ("Backend Developer",
         "Designs and builds server-side logic, APIs, and databases. "
         "Ensures applications are fast, scalable, and secure."),
        ("Full Stack Developer",
         "Develops both frontend (UI) and backend (server/DB) components. "
         "Versatile role requiring broad technical knowledge."),
        ("Data Engineer",
         "Builds data pipelines and infrastructure to collect, store, and process "
         "large-scale data for analytics teams."),
        ("DevOps Engineer",
         "Automates software delivery pipelines (CI/CD), manages cloud infrastructure, "
         "and ensures system reliability."),
        ("Cybersecurity Analyst",
         "Protects systems and networks from cyber threats. "
         "Performs vulnerability assessments, penetration testing, and incident response."),
        ("Embedded Systems Engineer",
         "Develops firmware and software for hardware devices like microcontrollers, "
         "IoT devices, and real-time systems."),
        ("AI Research Scientist",
         "Conducts cutting-edge research in artificial intelligence, publishes papers, "
         "and develops novel algorithms."),
        ("Cloud Architect",
         "Designs and manages cloud infrastructure on AWS, GCP, or Azure. "
         "Ensures scalability, availability, and cost efficiency."),

        # ── ENTC Careers ──────────────────────────────────────────────────────
        ("VLSI Design Engineer",
         "Designs integrated circuits (ICs) and chips at transistor level using "
         "HDL languages like Verilog and VHDL. Works in semiconductor companies."),
        ("RF / Antenna Engineer",
         "Designs and tests radio-frequency circuits and antenna systems for "
         "wireless devices, 5G infrastructure, and satellite communication."),
        ("Signal Processing Engineer",
         "Develops algorithms for processing audio, video, radar, and communication "
         "signals. Works in defense, telecom, and medical imaging."),
        ("IoT Developer",
         "Designs and builds Internet of Things solutions combining embedded hardware, "
         "firmware, and cloud connectivity."),
        ("Telecom Network Engineer",
         "Plans, deploys, and maintains telecommunication networks including 4G/5G, "
         "fiber optic systems, and switching infrastructure."),
        ("PCB Design Engineer",
         "Designs printed circuit boards for electronic products. "
         "Works with schematics, layout tools, and DFM principles."),

        # ── Mechanical Engineering Careers ────────────────────────────────────
        ("Mechanical Design Engineer",
         "Creates mechanical parts and assemblies using CAD tools like SolidWorks or CATIA. "
         "Works in automotive, aerospace, consumer products, and industrial machinery."),
        ("CAE / FEA Analyst",
         "Uses simulation software (ANSYS, Abaqus) to test structural integrity, "
         "thermal performance, and fluid behavior of components before manufacturing."),
        ("Manufacturing Engineer",
         "Optimizes production processes, reduces waste, and improves quality "
         "on the factory floor. Works with CNC machines and lean manufacturing."),
        ("Automotive Engineer",
         "Designs and develops vehicle systems including engines, chassis, "
         "powertrains, and EV drivetrains."),
        ("Robotics Engineer",
         "Designs robotic systems combining mechanical, electrical, and software "
         "elements for automation, surgery, and space exploration."),
        ("HVAC Engineer",
         "Designs heating, ventilation, and air conditioning systems for "
         "commercial and industrial buildings."),

        # ── Civil Engineering Careers ─────────────────────────────────────────
        ("Structural Engineer",
         "Designs safe and efficient structures including buildings, bridges, "
         "dams, and towers. Uses software like STAAD.Pro and ETABS."),
        ("Site / Construction Engineer",
         "Supervises construction activities on-site, ensures quality standards, "
         "manages contractors, and monitors project timelines."),
        ("Construction Project Manager",
         "Plans, coordinates, and oversees entire construction projects from "
         "inception to completion, managing budget, schedule, and teams."),
        ("GIS Analyst",
         "Uses geographic information systems to analyze spatial data for "
         "urban planning, infrastructure, environmental monitoring, and disaster response."),
        ("Environmental Engineer",
         "Develops solutions for environmental challenges — water treatment, "
         "pollution control, waste management, and sustainability planning."),
        ("Urban / Town Planner",
         "Develops plans and programs for land use, transportation, and "
         "community development in cities and regions."),

        # ── Electrical Engineering Careers ────────────────────────────────────
        ("Power Systems Engineer",
         "Designs and maintains electrical power generation, transmission, "
         "and distribution systems including smart grids."),
        ("Control Systems Engineer",
         "Designs automated control systems for industrial processes, robots, "
         "aircraft, and manufacturing equipment."),
        ("Renewable Energy Engineer",
         "Designs and implements solar, wind, hydro, and battery energy systems "
         "for sustainable power generation."),
        ("Electrical Design Engineer",
         "Creates electrical schematics, panel layouts, and wiring diagrams for "
         "industrial, commercial, and infrastructure projects."),
        ("Automation Engineer",
         "Programs and maintains PLC, SCADA, and HMI systems to automate "
         "industrial manufacturing processes."),

        # ── Chemical Engineering Careers ──────────────────────────────────────
        ("Process Engineer",
         "Designs and optimizes chemical manufacturing processes, troubleshoots "
         "production issues, and improves efficiency and safety."),
        ("Quality Assurance Engineer",
         "Develops and implements QA systems, conducts audits, and ensures "
         "products meet regulatory and quality standards."),

        # ── Cross-Branch / Research Careers ───────────────────────────────────
        ("Research & Development Engineer",
         "Conducts applied research to create new products, materials, or "
         "processes across engineering disciplines."),
        ("Systems Engineer",
         "Integrates complex engineered systems, ensuring all subsystems work "
         "together effectively. Common in defense, aerospace, and IT."),
    ]

    cursor.executemany(
        "INSERT IGNORE INTO careers (career_name, description) VALUES (%s, %s)",
        careers
    )

    # =========================================================================
    # CAREER → SKILLS MAPPINGS
    # =========================================================================
    career_skill_map = {
        # ── CS / IT (existing) ────────────────────────────────────────────────
        "Data Scientist": [
            "Python", "Machine Learning", "Statistics", "Data Analysis",
            "Pandas", "NumPy", "Scikit-learn", "SQL", "Data Visualization",
            "Deep Learning", "R"
        ],
        "Machine Learning Engineer": [
            "Python", "Machine Learning", "Deep Learning", "TensorFlow",
            "PyTorch", "Scikit-learn", "Docker", "REST API", "Git",
            "Pandas", "NumPy", "Kubernetes"
        ],
        "Backend Developer": [
            "Python", "Java", "SQL", "MySQL", "PostgreSQL", "Django",
            "Flask", "FastAPI", "REST API", "Git", "Docker", "Linux"
        ],
        "Full Stack Developer": [
            "JavaScript", "HTML", "CSS", "Python", "SQL", "Django",
            "REST API", "Git", "MongoDB", "Docker"
        ],
        "Data Engineer": [
            "Python", "SQL", "PostgreSQL", "MongoDB", "Scala",
            "AWS", "Google Cloud", "Docker", "Git", "Pandas",
            "REST API", "Linux"
        ],
        "DevOps Engineer": [
            "Linux", "Docker", "Kubernetes", "AWS", "Azure",
            "CI/CD", "Git", "Python", "Networking", "Google Cloud"
        ],
        "Cybersecurity Analyst": [
            "Cybersecurity", "Networking", "Linux", "Ethical Hacking",
            "Python", "Cryptography", "Problem Solving"
        ],
        "Embedded Systems Engineer": [
            "Embedded C", "C++", "Arduino", "RTOS", "VHDL",
            "PCB Design", "Linux", "Python", "Problem Solving",
            "Microcontrollers", "ARM Architecture"
        ],
        "AI Research Scientist": [
            "Python", "Machine Learning", "Deep Learning", "Natural Language Processing",
            "Computer Vision", "TensorFlow", "PyTorch", "Statistics",
            "R", "Communication"
        ],
        "Cloud Architect": [
            "AWS", "Google Cloud", "Azure", "Docker", "Kubernetes",
            "Linux", "Networking", "CI/CD", "Python", "Problem Solving"
        ],

        # ── ENTC Careers ──────────────────────────────────────────────────────
        "VLSI Design Engineer": [
            "VLSI Design", "Verilog", "VHDL", "FPGA Programming",
            "Digital Electronics", "C++", "Python", "MATLAB",
            "Signal Processing", "Problem Solving"
        ],
        "RF / Antenna Engineer": [
            "RF Design", "Antenna Design", "5G Technology", "Wireless Communication",
            "Digital Communication", "MATLAB", "Simulink", "Signal Processing",
            "Analog Electronics", "PCB Design"
        ],
        "Signal Processing Engineer": [
            "Signal Processing", "MATLAB", "Python", "Deep Learning",
            "Digital Communication", "Simulink", "NumPy", "Data Analysis",
            "C++", "Statistics"
        ],
        "IoT Developer": [
            "IoT Development", "Embedded C", "Arduino", "Raspberry Pi", "ESP32",
            "Python", "MQTT", "AWS", "PCB Design", "REST API",
            "Microcontrollers", "Linux"
        ],
        "Telecom Network Engineer": [
            "5G Technology", "Wireless Communication", "Networking", "Digital Communication",
            "RF Design", "Linux", "Python", "MATLAB"
        ],
        "PCB Design Engineer": [
            "PCB Design", "Altium Designer", "KiCad", "Embedded C",
            "Digital Electronics", "Analog Electronics", "Soldering & Prototyping",
            "VLSI Design", "Problem Solving"
        ],

        # ── Mechanical Engineering Careers ────────────────────────────────────
        "Mechanical Design Engineer": [
            "SolidWorks", "AutoCAD", "CATIA", "Fusion 360", "PTC Creo",
            "GD&T", "Machine Design", "Sheet Metal Design",
            "Structural Analysis", "Technical Report Writing", "Problem Solving"
        ],
        "CAE / FEA Analyst": [
            "ANSYS", "Finite Element Analysis (FEA)", "Computational Fluid Dynamics (CFD)",
            "Thermal Analysis", "Structural Analysis", "SolidWorks",
            "MATLAB", "Python for Engineers", "C++", "Technical Report Writing"
        ],
        "Manufacturing Engineer": [
            "CNC Programming", "Manufacturing Processes", "GD&T",
            "Lean Manufacturing", "AutoCAD", "SolidWorks",
            "3D Printing / Additive Manufacturing", "Quality Control (Civil)",
            "Problem Solving", "Team Collaboration"
        ],
        "Automotive Engineer": [
            "SolidWorks", "CATIA", "ANSYS", "Finite Element Analysis (FEA)",
            "Thermodynamics", "Fluid Mechanics", "Machine Design",
            "Manufacturing Processes", "MATLAB", "Python for Engineers"
        ],
        "Robotics Engineer": [
            "Robotics", "Python", "C++", "ROS", "MATLAB",
            "Embedded C", "Machine Design", "Control Systems",
            "SolidWorks", "Arduino", "Microcontrollers"
        ],
        "HVAC Engineer": [
            "Thermodynamics", "Fluid Mechanics", "Heat Transfer",
            "AutoCAD", "Hydraulics & Pneumatics", "MATLAB",
            "Structural Analysis", "Technical Report Writing"
        ],

        # ── Civil Engineering Careers ─────────────────────────────────────────
        "Structural Engineer": [
            "STAAD.Pro", "ETABS", "SAP2000", "Structural Analysis",
            "Concrete Design", "Steel Design", "AutoCAD Civil 3D",
            "Revit (BIM)", "Foundation Design", "Technical Report Writing"
        ],
        "Site / Construction Engineer": [
            "Construction Management", "AutoCAD Civil 3D", "Surveying",
            "Estimation & Costing", "Quality Control (Civil)", "MS Project",
            "Concrete Design", "Problem Solving", "Team Collaboration"
        ],
        "Construction Project Manager": [
            "Project Management", "Primavera P6", "MS Project",
            "Estimation & Costing", "Construction Management",
            "Contract Management", "Leadership", "Communication",
            "Time Management", "Quality Control (Civil)"
        ],
        "GIS Analyst": [
            "GPS & GIS Mapping", "Remote Sensing", "Surveying",
            "Python", "Data Analysis", "AutoCAD Civil 3D",
            "Environmental Engineering", "Technical Report Writing"
        ],
        "Environmental Engineer": [
            "Environmental Engineering", "Water Resources Engineering",
            "Hydrology", "Waste Management", "GD&T",
            "AutoCAD Civil 3D", "Python for Engineers", "Data Analysis",
            "Technical Report Writing", "Research Methodology"
        ],
        "Urban / Town Planner": [
            "GPS & GIS Mapping", "AutoCAD Civil 3D", "Revit (BIM)",
            "Project Management", "Communication", "Research Methodology",
            "Environmental Engineering", "Surveying"
        ],

        # ── Electrical Engineering Careers ────────────────────────────────────
        "Power Systems Engineer": [
            "Power Systems Analysis", "Electrical Machines", "ETAP", "PSCAD",
            "Control Systems", "MATLAB", "Simulink",
            "Protection & Relay Systems", "High Voltage Engineering",
            "Technical Report Writing"
        ],
        "Control Systems Engineer": [
            "Control Systems", "PID Tuning", "MATLAB", "Simulink",
            "PLC Programming", "Python", "C++", "Embedded C",
            "Industrial Automation", "Problem Solving"
        ],
        "Renewable Energy Engineer": [
            "Renewable Energy Systems", "Solar PV Design", "Wind Energy",
            "Power Electronics", "MATLAB", "Electrical Machines",
            "Power Systems Analysis", "Python for Engineers",
            "Technical Report Writing"
        ],
        "Electrical Design Engineer": [
            "Electrical Design (AutoCAD Electrical)", "AutoCAD",
            "Electrical Machines", "Power Electronics", "Protection & Relay Systems",
            "Estimation & Costing", "Technical Report Writing", "Problem Solving"
        ],
        "Automation Engineer": [
            "PLC & HMI", "SCADA Systems", "PLC Programming", "Industrial Automation",
            "Control Systems", "Python", "C++", "Motor Drives",
            "Networking", "Problem Solving"
        ],

        # ── Chemical Engineering Careers ──────────────────────────────────────
        "Process Engineer": [
            "Process Simulation (Aspen)", "Chemical Process Design",
            "Mass & Energy Balances", "Heat Exchanger Design",
            "Reactor Design", "Separation Processes", "Fluid Flow in Pipes",
            "HSE (Health, Safety & Environment)", "Piping & Instrumentation (P&ID)",
            "MATLAB", "Technical Report Writing"
        ],
        "Quality Assurance Engineer": [
            "Quality Control (Chemical)", "Six Sigma",
            "HSE (Health, Safety & Environment)", "Data Analysis",
            "Microsoft Excel (Advanced)", "Problem Solving",
            "Technical Report Writing", "Communication"
        ],

        # ── Cross-Branch Careers ───────────────────────────────────────────────
        "Research & Development Engineer": [
            "Research Methodology", "Literature Survey", "MATLAB",
            "Python", "Data Analysis", "Statistics",
            "Technical Report Writing", "Problem Solving", "Communication"
        ],
        "Systems Engineer": [
            "Systems Engineering", "Project Management", "MATLAB",
            "Python", "Problem Solving", "Technical Report Writing",
            "Team Collaboration", "Communication", "Leadership"
        ],
    }

    # Insert career → skill links
    for career_name, required_skills in career_skill_map.items():
        cursor.execute(
            "SELECT career_id FROM careers WHERE career_name = %s", (career_name,)
        )
        career_row = cursor.fetchone()
        if not career_row:
            continue
        career_id = career_row[0]

        for skill_name in required_skills:
            cursor.execute(
                "SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,)
            )
            skill_row = cursor.fetchone()
            if not skill_row:
                continue
            skill_id = skill_row[0]
            cursor.execute(
                "INSERT IGNORE INTO career_skills (career_id, skill_id) VALUES (%s, %s)",
                (career_id, skill_id)
            )

    cursor.close()
    conn.close()
    print("✅ Seed data inserted successfully (all branches covered).")


# =============================================================================
# CRUD FUNCTIONS — Students
# =============================================================================

def create_student(name: str, branch: str, cgpa: float,
                   country: str, career_goal: str) -> int:
    """
    Inserts a new student record and returns the auto-generated student_id.

    HOW AUTO_INCREMENT WORKS:
    MySQL assigns the next available integer as student_id automatically.
    cursor.lastrowid retrieves the ID that was just created.

    Returns:
        int: The new student's student_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO students (name, branch, cgpa, country, career_goal)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, branch, cgpa, country, career_goal)
    )
    new_id = cursor.lastrowid  # The AUTO_INCREMENT ID just created
    cursor.close()
    conn.close()
    return new_id


@st.cache_data(ttl=30)
def get_all_students() -> pd.DataFrame:
    """
    Returns all students as a Pandas DataFrame.
    Cached for 30 seconds to avoid repeated DB round-trips on every rerun.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM students ORDER BY student_id DESC", conn)
    conn.close()
    return df


@st.cache_data(ttl=30)
def get_student_by_id(student_id: int) -> dict | None:
    """
    Returns a single student record as a dictionary, or None if not found.
    Cached for 30 seconds to avoid repeated queries on every Skills page rerun.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM students WHERE student_id = %s", (student_id,)
    )
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return student


def update_student(student_id: int, name: str, branch: str, cgpa: float,
                   country: str, career_goal: str):
    """Updates an existing student's profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE students
        SET name=%s, branch=%s, cgpa=%s, country=%s, career_goal=%s
        WHERE student_id=%s
        """,
        (name, branch, cgpa, country, career_goal, student_id)
    )
    cursor.close()
    conn.close()


def delete_student(student_id: int):
    """
    Deletes a student. Related rows in student_skills are removed automatically
    because of the ON DELETE CASCADE foreign key constraint.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
    cursor.close()
    conn.close()


# =============================================================================
# CRUD FUNCTIONS — Skills
# =============================================================================

@st.cache_data(ttl=300)
def get_all_skills() -> pd.DataFrame:
    """Returns all skills from the master skills table. Cached for 5 minutes."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM skills ORDER BY skill_name", conn)
    conn.close()
    return df


@st.cache_data(ttl=30)
def get_student_skills(student_id: int) -> list[str]:
    """
    Returns a list of skill names that a specific student has. Cached for 30 seconds.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.skill_name
        FROM student_skills ss
        JOIN skills s ON ss.skill_id = s.skill_id
        WHERE ss.student_id = %s
        ORDER BY s.skill_name
        """,
        (student_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]  # Extract skill_name from each tuple


def add_student_skill(student_id: int, skill_name: str) -> bool:
    """
    Adds a skill to a student's profile.
    First looks up (or creates) the skill in the skills table,
    then creates the student_skills link.

    Returns:
        True if skill was added, False if it already existed.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Insert the skill into skills table if it doesn't exist.
    cursor.execute(
        "INSERT IGNORE INTO skills (skill_name) VALUES (%s)", (skill_name,)
    )

    # Step 2: Get the skill_id (whether we just created it or it already existed).
    cursor.execute(
        "SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,)
    )
    skill_id = cursor.fetchone()[0]

    # Step 3: Try to link the student to this skill.
    try:
        cursor.execute(
            "INSERT INTO student_skills (student_id, skill_id) VALUES (%s, %s)",
            (student_id, skill_id)
        )
        added = True
    except mysql.connector.IntegrityError:
        added = False

    cursor.close()
    conn.close()

    # Clear caches so next read reflects the new skill
    if added:
        get_student_skills.clear()
        get_all_skills.clear()
    return added


def remove_student_skill(student_id: int, skill_name: str):
    """Removes a specific skill from a student's profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE ss FROM student_skills ss
        JOIN skills s ON ss.skill_id = s.skill_id
        WHERE ss.student_id = %s AND s.skill_name = %s
        """,
        (student_id, skill_name)
    )
    cursor.close()
    conn.close()
    # Clear student skills cache so next read is fresh
    get_student_skills.clear()


# =============================================================================
# READ FUNCTIONS — Careers
# =============================================================================

@st.cache_data(ttl=300)
def get_all_careers() -> pd.DataFrame:
    """Returns all careers from the database. Cached for 5 minutes."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM careers ORDER BY career_name", conn)
    conn.close()
    return df


def get_career_skills(career_id: int) -> list[str]:
    """Returns the list of skill names required for a specific career."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.skill_name
        FROM career_skills cs
        JOIN skills s ON cs.skill_id = s.skill_id
        WHERE cs.career_id = %s
        ORDER BY s.skill_name
        """,
        (career_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]


@st.cache_data(ttl=300)
def get_all_career_skill_map() -> dict[str, list[str]]:
    """
    Returns a dictionary mapping every career name to its list of required skills.
    Cached for 5 minutes — this is the hottest read in the recommendation engine.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.career_name, s.skill_name
        FROM career_skills cs
        JOIN careers c  ON cs.career_id = c.career_id
        JOIN skills  s  ON cs.skill_id  = s.skill_id
        ORDER BY c.career_name, s.skill_name
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Build the dictionary from the flat list of (career, skill) pairs
    career_map: dict[str, list[str]] = {}
    for career_name, skill_name in rows:
        if career_name not in career_map:
            career_map[career_name] = []
        career_map[career_name].append(skill_name)
    return career_map


# =============================================================================
# USER AUTHENTICATION CRUD (Phase 5)
# =============================================================================

def create_user(username: str, email: str, password_hash: str) -> int | None:
    """
    Inserts a new user into the users table.
    Returns the new user_id on success, None on failure.

    NOTE: The password_hash is already bcrypt-hashed before this is called.
    We NEVER store plain-text passwords.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid
        return user_id
    except mysql.connector.IntegrityError:
        # UNIQUE constraint on email — account already exists
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """
    Looks up a user by their email address.
    Returns a dict with user fields, or None if not found.

    Used by auth.py to:
    1. Check for duplicate emails during signup
    2. Retrieve the password_hash during login for bcrypt verification
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Returns rows as dicts
    try:
        cursor.execute(
            "SELECT user_id, username, email, password_hash FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        return row  # None if not found
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# INITIALIZATION — Run this once to set everything up
# =============================================================================

def initialize_database():
    """
    Master setup function. Call this once at application startup.
    Skips seed_data() if data already exists to avoid slow startup on every rerun.
    """
    print("🚀 Initializing CareerForge AI database...")
    create_database_if_not_exists()
    create_tables()

    # Only seed if the careers table is empty — avoids running hundreds of
    # INSERT IGNORE queries on every cold start after the first run.
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM careers")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        if count == 0:
            seed_data()
            print("🌱 Database seeded with initial data.")
        else:
            print("✅ Database already seeded — skipping seed step.")
    except Exception:
        seed_data()  # Fallback: seed anyway if check fails

    print("🎉 Database initialization complete!")


# ---------------------------------------------------------------------------
# Direct execution: python database.py
# ---------------------------------------------------------------------------
# When you run this file directly (not imported), this block executes.
# This lets you test the DB setup independently of Streamlit.
if __name__ == "__main__":
    initialize_database()

