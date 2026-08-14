# =============================================================================
# auth.py — Authentication Module for CareerForge AI
# =============================================================================
#
# WHAT THIS FILE DOES:
#   1. Password hashing via bcrypt (never store plain-text passwords)
#   2. User creation and lookup (calls database.py functions)
#   3. Session management via st.session_state
#   4. require_login() guard — call at the top of every protected page
#
# HOW BCRYPT WORKS:
#   bcrypt.hashpw(password_bytes, salt) → hash string
#   The hash INCLUDES the salt, so we don't store it separately.
#   bcrypt.checkpw(password_bytes, hash) → True/False
#   Even if two users have the same password, their hashes are different
#   because each hash uses a unique random salt.
# =============================================================================

import bcrypt
import streamlit as st
import database as db


# =============================================================================
# PASSWORD UTILITIES
# =============================================================================

def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Returns a string (decoded from bytes) suitable for storing in MySQL VARCHAR.

    bcrypt.gensalt() creates a random 16-byte salt with work factor 12.
    Work factor 12 means 2^12 iterations — slow enough to resist brute-force.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")   # Store as string in DB


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare a plain-text password against a stored bcrypt hash.
    Returns True if they match, False otherwise.

    bcrypt.checkpw() handles the salt automatically — it's embedded in the hash.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# =============================================================================
# USER MANAGEMENT
# =============================================================================

def create_user(username: str, email: str, plain_password: str) -> dict:
    """
    Create a new user account.
    Returns {'success': True, 'user_id': ...} or {'success': False, 'error': '...'}
    """
    # Validate inputs
    if not username.strip():
        return {"success": False, "error": "Username cannot be empty."}
    if not email.strip() or "@" not in email:
        return {"success": False, "error": "Please enter a valid email address."}
    if len(plain_password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}

    # Check if email already exists
    existing = db.get_user_by_email(email.strip().lower())
    if existing:
        return {"success": False, "error": "An account with this email already exists."}

    # Hash + store
    password_hash = hash_password(plain_password)
    user_id = db.create_user(
        username=username.strip(),
        email=email.strip().lower(),
        password_hash=password_hash
    )
    if user_id:
        return {"success": True, "user_id": user_id}
    return {"success": False, "error": "Database error. Please try again."}


def authenticate_user(email: str, plain_password: str) -> dict | None:
    """
    Verify credentials.
    Returns user dict on success, None on failure.
    """
    user = db.get_user_by_email(email.strip().lower())
    if user is None:
        return None
    if verify_password(plain_password, user["password_hash"]):
        return user
    return None


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

def login_user(user: dict):
    """Store the logged-in user in session state."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = {
        "user_id":  user["user_id"],
        "username": user["username"],
        "email":    user["email"],
    }


def logout():
    """Clear all auth-related session state and redirect to login."""
    for key in ["authenticated", "user"]:
        if key in st.session_state:
            del st.session_state[key]
    st.switch_page("pages/0_Login.py")


def is_authenticated() -> bool:
    """Returns True if the user is currently logged in."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict | None:
    """Returns the current user dict or None if not logged in."""
    return st.session_state.get("user", None)


def require_login():
    """
    Call at the TOP of every protected page (after set_page_config).
    If the user is not logged in, redirects them to the login page immediately.

    USAGE:
        from auth import require_login
        require_login()   # ← place before any page content
    """
    if not is_authenticated():
        st.switch_page("pages/0_Login.py")
