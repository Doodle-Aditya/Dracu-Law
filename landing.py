import streamlit as st
import hashlib
import sqlite3

st.set_page_config(page_title="Dracu-Law", page_icon="⚖️", layout="wide")

# =========================================================
# DATABASE
# =========================================================
DB_FILE = "dracu_users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(name, email, password):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email.lower().strip(), hash_password(password))
        )
        conn.commit()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT name FROM users WHERE email = ? AND password = ?",
        (email.lower().strip(), hash_password(password))
    ).fetchone()
    conn.close()
    return (True, row[0]) if row else (False, "Invalid email or password.")

init_db()

# =========================================================
# SESSION DEFAULTS
# =========================================================
for k, v in {"logged_in": False, "username": "", "auth_mode": None}.items():
    st.session_state.setdefault(k, v)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,700;0,900;1,700;1,900&family=Manrope:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --red:    #c0392b;
    --red2:   #e74c3c;
    --bg:     #09090b;
    --border: #2a2a38;
    --muted:  #9a9aaa;
    --muted2: #8a8a9a;
    --serif:  'Fraunces', Georgia, serif;
    --sans:   'Manrope', sans-serif;
    --mono:   'IBM Plex Mono', monospace;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { visibility: hidden !important; display: none !important; }

/* Base */
html, body, .stApp {
    background: var(--bg) !important;
    color: #eae5dc !important;
    font-family: var(--sans) !important;
}

.block-container { max-width: 100% !important; padding-top: 0 !important; }

/* Subtle background glow */
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: radial-gradient(ellipse 55% 40% at 10% 5%, rgba(192,57,43,0.11) 0%, transparent 60%);
}

/* ── Typography classes ── */
.eyebrow {
    font-family: var(--mono); font-size: 10px;
    color: var(--red2); letter-spacing: 2.5px;
    text-transform: uppercase; display: block; margin-bottom: 16px;
}
.hero-title {
    font-family: var(--serif);
    font-size: clamp(42px, 5vw, 76px);
    font-weight: 900; line-height: 0.95;
    letter-spacing: -2px; color: #fff;
    margin: 0 0 24px 0; display: block;
}
.hero-title .acc { color: var(--red2); font-style: italic; }

/* FIX: was #3a3a48 — now readable */
.hero-title .dim { color: #b0a898; }

.hero-sub {
    font-size: 17px;
    color: #a0a0b0;
    line-height: 1.65;
    font-weight: 400;
    display: block; margin-bottom: 8px;
    max-width: 90%;
}

/* FIX: stat values — ensure full visibility */
.stat-val {
    font-family: var(--serif); font-size: 38px;
    font-weight: 900; color: #ffffff; line-height: 1;
    display: block; margin-bottom: 4px;
}
.stat-val span { color: var(--red2); }

/* FIX: stat key — was too dark, now clearly visible */
.stat-key {
    font-family: var(--mono); font-size: 9px;
    color: #9090a8;
    letter-spacing: 2px;
    text-transform: uppercase; margin-top: 4px; display: block;
}

/* FIX: right-label and nav-tag — readable grey */
.right-label {
    font-family: var(--mono); font-size: 9px;
    color: #9090a8;
    letter-spacing: 2.5px;
    text-transform: uppercase; display: block; margin-bottom: 8px;
}
.right-heading {
    font-family: var(--serif); font-size: 24px;
    font-weight: 900; color: #fff; line-height: 1.1;
    display: block; margin-bottom: 20px;
}
.auth-label {
    font-family: var(--mono); font-size: 9px;
    color: var(--red2); letter-spacing: 2.5px;
    text-transform: uppercase; display: block; margin-bottom: 8px;
}
.auth-heading {
    font-family: var(--serif); font-size: 30px;
    font-weight: 900; color: #fff; line-height: 1.05;
    display: block; margin-bottom: 6px;
}
.auth-sub {
    font-size: 14px;
    color: #9a9aaa;
    font-weight: 400;
    line-height: 1.6;
    display: block; margin-bottom: 20px;
}
.feat-name {
    font-size: 14px; font-weight: 600; color: #e0dbd2;
    display: block; margin-bottom: 4px;
}
.feat-desc {
    font-size: 14px;
    color: #9a9aaa;
    line-height: 1.65;
    font-weight: 400;
    display: block;
}
.nav-brand {
    font-family: var(--serif); font-size: 20px;
    font-weight: 900; color: #fff; display: block;
}
.nav-brand span { color: var(--red2); font-style: italic; }

/* FIX: nav-tag — was #3a3a48, now visible */
.nav-tag {
    font-family: var(--mono); font-size: 9px;
    color: #9090a8;
    letter-spacing: 2px;
    text-transform: uppercase; display: block;
}
.nav-user {
    font-family: var(--sans); font-size: 13px; color: #d06050;
    font-weight: 500; background: rgba(192,57,43,0.09);
    border: 1px solid rgba(192,57,43,0.22);
    border-radius: 6px; padding: 5px 14px; display: inline-block;
}
.status-dot {
    display: inline-block; width: 7px; height: 7px;
    border-radius: 50%; background: #2ecc71;
    box-shadow: 0 0 7px rgba(46,204,113,0.7); margin-right: 8px;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: #f2ede6 !important;
    border: 1.5px solid #cac4ba !important;
    border-radius: 8px !important; color: #111 !important;
    font-family: var(--sans) !important; font-size: 14px !important;
    padding: 12px 14px !important; transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--red) !important; background: #fff !important;
    box-shadow: 0 0 0 3px rgba(192,57,43,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: #b5ada4 !important; }

/* FIX: Password eye toggle — keep it inside the input box */
.stTextInput > div > div {
    position: relative !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
.stTextInput > div > div > div[data-testid="stInputRightElement"] {
    position: absolute !important;
    right: 10px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: auto !important;
    height: auto !important;
}
.stTextInput > div > div > div[data-testid="stInputRightElement"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #888 !important;
    padding: 4px !important;
    border-radius: 4px !important;
    transition: color 0.2s !important;
}
.stTextInput > div > div > div[data-testid="stInputRightElement"] button:hover {
    color: #444 !important;
    background: rgba(0,0,0,0.06) !important;
    box-shadow: none !important;
}
.stTextInput > div > div > div[data-testid="stInputRightElement"] button svg {
    width: 16px !important;
    height: 16px !important;
}
.stTextInput label {
    color: #908880 !important; font-size: 10px !important;
    font-weight: 600 !important; letter-spacing: 1.3px !important;
    text-transform: uppercase !important; font-family: var(--mono) !important;
}

/* ── Buttons ── */
.btn-primary .stButton > button {
    background: var(--red) !important; color: #fff !important;
    border: none !important; border-radius: 7px !important;
    font-family: var(--sans) !important; font-weight: 600 !important;
    font-size: 14px !important; padding: 11px 24px !important;
    width: 100% !important; transition: all 0.2s !important;
}
.btn-primary .stButton > button:hover {
    background: var(--red2) !important;
    box-shadow: 0 0 26px rgba(192,57,43,0.4) !important;
    transform: translateY(-1px) !important;
}
.btn-ghost .stButton > button {
    background: transparent !important; color: #b0b0c0 !important;
    border: 1px solid #3a3a50 !important; border-radius: 7px !important;
    font-family: var(--sans) !important; font-weight: 400 !important;
    font-size: 14px !important; padding: 11px 20px !important;
    width: 100% !important; transition: all 0.2s !important;
}
.btn-ghost .stButton > button:hover {
    border-color: #666 !important; color: #ddd !important;
    background: rgba(255,255,255,0.04) !important;
    box-shadow: none !important; transform: none !important;
}
.btn-full .stButton > button {
    background: var(--red) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-family: var(--sans) !important; font-weight: 600 !important;
    font-size: 14px !important; padding: 13px !important;
    width: 100% !important; transition: all 0.2s !important;
}
.btn-full .stButton > button:hover {
    background: var(--red2) !important;
    box-shadow: 0 0 26px rgba(192,57,43,0.4) !important;
    transform: translateY(-1px) !important;
}
.btn-link .stButton > button {
    background: transparent !important; color: #9a9aaa !important;
    border: none !important; font-size: 12px !important;
    font-weight: 400 !important; padding: 4px 0 !important;
    width: auto !important; text-decoration: underline !important;
    text-underline-offset: 3px !important; box-shadow: none !important;
}
.btn-link .stButton > button:hover {
    color: #ccc !important; background: transparent !important;
    box-shadow: none !important; transform: none !important;
}

/* Column gap */
[data-testid="stHorizontalBlock"] { gap: 0 !important; }

/* FIX: hr — was #1f1f28, now clearly visible */
hr { border-color: #3a3a50 !important; }

.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def logout():
    st.session_state.logged_in = False
    st.session_state.username  = ""
    st.session_state.auth_mode = None
    st.rerun()


# =========================================================
# NAVBAR
# =========================================================
def render_navbar():
    n1, _, n2 = st.columns([3, 3, 2])
    with n1:
        st.markdown("<div class='nav-brand'>Dracu<span>-Law</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='nav-tag'>AI Legal Intelligence</div>", unsafe_allow_html=True)
    with n2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.logged_in:
            st.markdown(f"<div class='nav-user'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='font-family:IBM Plex Mono,monospace;font-size:10px;"
                "color:#9090a8;"
                "letter-spacing:1.5px;text-transform:uppercase;'>"
                "<span class='status-dot'></span>Systems Operational</div>",
                unsafe_allow_html=True
            )
    st.markdown("---")


# =========================================================
# LEFT COLUMN — HERO
# =========================================================
def render_left():
    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.logged_in:
        first = st.session_state.username.split()[0]
        st.markdown(f"<span class='eyebrow'>⚡ Welcome back, {first}</span>", unsafe_allow_html=True)
        st.markdown("<span class='hero-title'>Ready to<br><span class='acc'>Analyze.</span></span>", unsafe_allow_html=True)
        st.markdown(
            "<span class='hero-sub'>Your AI legal engine is standing by. "
            "Upload a contract to get instant risk scoring, clause flagging, and smart rewrites.</span>",
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, _ = st.columns([2, 1.5, 2])
        with c1:
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.button("Open Analyzer →", key="hero_open"):
                st.switch_page("pages/app.py")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("Log Out", key="hero_logout"):
                logout()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("<span class='eyebrow'>⚖ AI Contract Intelligence</span>", unsafe_allow_html=True)
        st.markdown(
            "<span class='hero-title'>"
            "<span class='dim'>Read every</span><br>"
            "clause. <span class='acc'>Miss</span><br>"
            "<span class='acc'>nothing.</span>"
            "</span>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<span class='hero-sub'>"
            "Dracu-Law dissects contracts with surgical precision — surfacing "
            "<strong style='color:#c8c2b8;'>red flags</strong>, comparing versions, "
            "and rewriting dangerous clauses before you sign."
            "</span>",
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2, _ = st.columns([2, 1.6, 2])
        with c1:
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.button("Get Started →", key="hero_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("Sign In", key="hero_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Stats
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("<span class='stat-val'>98<span>%</span></span>", unsafe_allow_html=True)
            st.markdown("<span class='stat-key'>Clause Detection</span>", unsafe_allow_html=True)
        with s2:
            st.markdown("<span class='stat-val'>&lt;10<span>s</span></span>", unsafe_allow_html=True)
            st.markdown("<span class='stat-key'>Analysis Time</span>", unsafe_allow_html=True)
        with s3:
            st.markdown("<span class='stat-val'>3<span>x</span></span>", unsafe_allow_html=True)
            st.markdown("<span class='stat-key'>Faster Review</span>", unsafe_allow_html=True)


# =========================================================
# RIGHT COLUMN — Feature List
# =========================================================
def render_feature_list():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='right-label'>// What's inside</span>", unsafe_allow_html=True)
    st.markdown(
        "<span class='right-heading'>Everything you need<br>to sign with confidence.</span>",
        unsafe_allow_html=True
    )
    features = [
        ("🔬", "Deep Contract Analysis",
         "Instant risk score 1–10, flagged clauses, plain-English summary and actionable suggestions."),
        ("⚖️", "Side-by-Side Comparison",
         "Pit two contracts against each other. AI highlights differences and picks the better deal."),
        ("✍️", "Smart Clause Rewriting",
         "Select risky clauses, get AI rewrites in your favour, download a polished Word document."),
    ]
    for icon, name, desc in features:
        st.markdown("---")
        ic, tx = st.columns([1, 7])
        with ic:
            st.markdown(
                f"<div style='background:rgba(192,57,43,0.09);border:1px solid rgba(192,57,43,0.2);"
                f"border-radius:8px;width:38px;height:38px;display:flex;align-items:center;"
                f"justify-content:center;font-size:17px;'>{icon}</div>",
                unsafe_allow_html=True
            )
        with tx:
            st.markdown(f"<span class='feat-name'>{name}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='feat-desc'>{desc}</span>", unsafe_allow_html=True)


# =========================================================
# RIGHT COLUMN — Login Form
# =========================================================
def render_login_form():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='auth-label'>// Sign in</span>", unsafe_allow_html=True)
    st.markdown("<span class='auth-heading'>Welcome back.</span>", unsafe_allow_html=True)
    st.markdown("<span class='auth-sub'>Sign in to your Dracu-Law account to continue.</span>", unsafe_allow_html=True)

    email    = st.text_input("Email",    placeholder="you@example.com", key="login_email")
    password = st.text_input("Password", placeholder="Your password", type="password", key="login_pass")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="btn-full">', unsafe_allow_html=True)
    if st.button("Sign In →", key="do_login"):
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            ok, result = login_user(email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username  = result
                st.session_state.auth_mode = None
                st.rerun()
            else:
                st.error(f"❌ {result}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="btn-link">', unsafe_allow_html=True)
    if st.button("No account? Create one →", key="switch_signup"):
        st.session_state.auth_mode = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# RIGHT COLUMN — Signup Form
# =========================================================
def render_signup_form():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='auth-label'>// Create account</span>", unsafe_allow_html=True)
    st.markdown("<span class='auth-heading'>Start for free.</span>", unsafe_allow_html=True)
    st.markdown("<span class='auth-sub'>Analyze your first contract in under a minute.</span>", unsafe_allow_html=True)

    name     = st.text_input("Full Name", placeholder="Jane Smith",        key="signup_name")
    email    = st.text_input("Email",     placeholder="you@example.com",   key="signup_email")
    password = st.text_input("Password",  placeholder="Min. 6 characters", type="password", key="signup_pass")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="btn-full">', unsafe_allow_html=True)
    if st.button("Create Account →", key="do_signup"):
        if not name or not email or len(password) < 6:
            st.error("❌ Fill in all fields. Password must be at least 6 characters.")
        else:
            ok, msg = register_user(name, email, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username  = name
                st.session_state.auth_mode = None
                st.rerun()
            else:
                st.error(f"❌ {msg}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="btn-link">', unsafe_allow_html=True)
    if st.button("Already have an account? Sign in →", key="switch_login"):
        st.session_state.auth_mode = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
def render_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;padding:16px 0 24px;"
        "font-family:IBM Plex Mono,monospace;font-size:11px;"
        "color:#9090a8;letter-spacing:0.5px;'>"
        "⚖️ DRACU-LAW &nbsp;·&nbsp; POWERED BY GROQ &nbsp;·&nbsp; BUILT WITH STREAMLIT<br>"
        "<span style='font-size:10px;color:#7a7a9a;'>AI analysis is not a substitute for professional legal advice.</span>"
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# MAIN
# =========================================================
render_navbar()

left, right = st.columns([6, 4], gap="small")

with left:
    render_left()

with right:
    st.markdown(
        "<style>div[data-testid='stHorizontalBlock'] > div:nth-child(2) "
        "{ border-left: 1px solid #2a2a40 !important; padding-left: 2rem !important; }</style>",
        unsafe_allow_html=True
    )
    if st.session_state.auth_mode == "login":
        render_login_form()
    elif st.session_state.auth_mode == "signup":
        render_signup_form()
    else:
        render_feature_list()

render_footer()