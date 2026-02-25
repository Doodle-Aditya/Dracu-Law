import streamlit as st
import hashlib
import sqlite3
import os

st.set_page_config(page_title="Dracu-Law", page_icon="⚖️", layout="wide")

# ---------- SQLITE AUTH ----------
DB_FILE = "dracu_users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute(
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
    c = conn.cursor()
    c.execute(
        "SELECT name FROM users WHERE email = ? AND password = ?",
        (email.lower().strip(), hash_password(password))
    )
    row = c.fetchone()
    conn.close()
    if row:
        return True, row[0]
    return False, "Invalid email or password."

init_db()

# ---------- SESSION DEFAULTS ----------
if "logged_in"  not in st.session_state: st.session_state.logged_in  = False
if "username"   not in st.session_state: st.session_state.username   = ""
if "auth_mode"  not in st.session_state: st.session_state.auth_mode  = None

# ---------- GLOBAL CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500;600&family=Courier+Prime&display=swap');

#MainMenu, footer, header, [data-testid="stToolbar"], .stDeployButton { visibility: hidden !important; display: none !important; }

body, .stApp {
    background: #0a0a0b !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; height: 500px;
    background: radial-gradient(ellipse 80% 55% at 50% 0%, rgba(192,57,43,0.2) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}

/* ── NAVBAR ── */
.dracu-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 52px;
    background: rgba(10,10,11,0.96);
    border-bottom: 1px solid #2a2a2e;
    position: sticky; top: 0; z-index: 99;
    backdrop-filter: blur(18px);
}
.dracu-brand {
    font-family: 'Playfair Display', serif;
    font-size: 26px; font-weight: 900;
    color: #fff; letter-spacing: -0.5px;
}
.dracu-brand span { color: #e74c3c; }
.nav-tagline { font-size: 11px; color: #666; letter-spacing: 1.4px; text-transform: uppercase; margin-top: 2px; }
.nav-user-badge {
    background: rgba(192,57,43,0.14);
    border: 1px solid rgba(192,57,43,0.35);
    border-radius: 100px; padding: 6px 16px;
    font-size: 13px; color: #f07a6a; font-weight: 600;
}

/* ── HERO ── */
.hero-wrap { text-align: center; padding: 96px 24px 56px; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 20px;
    background: rgba(192,57,43,0.1); border: 1px solid rgba(192,57,43,0.3);
    border-radius: 100px; font-size: 11px; color: #e74c3c;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 30px;
    font-family: 'Courier Prime', monospace;
}
.hero-dot { width: 6px; height: 6px; border-radius: 50%; background: #e74c3c; display: inline-block; animation: blink 2s infinite; }
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(50px, 7vw, 96px);
    font-weight: 900; line-height: 0.95;
    letter-spacing: -3px; color: #ffffff;
    margin-bottom: 26px;
}
.hero-title em { color: #e74c3c; font-style: italic; display: block; }
.hero-sub {
    font-size: 19px; color: #aaa; max-width: 560px;
    margin: 0 auto 48px; line-height: 1.75; font-weight: 300;
}

/* ── STATS ── */
.stats-row { display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; margin-top: 52px; padding-top: 44px; border-top: 1px solid #222; }
.stat-box { text-align: center; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 46px; font-weight: 900; color: #fff; line-height: 1; }
.stat-num span { color: #e74c3c; }
.stat-label { font-size: 11px; color: #666; letter-spacing: 1.3px; text-transform: uppercase; margin-top: 6px; }

/* ── SECTION HEADERS ── */
.section-label { font-size: 11px; color: #e74c3c; letter-spacing: 2.5px; text-transform: uppercase; font-family: 'Courier Prime', monospace; margin-bottom: 12px; }
.section-title { font-family: 'Playfair Display', serif; font-size: clamp(32px, 4vw, 52px); font-weight: 900; color: #ffffff; letter-spacing: -1.5px; line-height: 1.08; margin-bottom: 40px; }

/* ── FEATURE CARDS ── */
.feat-card {
    background: #16161a; border: 1px solid #272729;
    border-radius: 14px; padding: 36px 30px; height: 100%;
    transition: border-color 0.25s, transform 0.25s;
}
.feat-card:hover { border-color: rgba(192,57,43,0.45); transform: translateY(-3px); }
.feat-icon { font-size: 30px; margin-bottom: 18px; display: block; }
.feat-title { font-family: 'Playfair Display', serif; font-size: 21px; font-weight: 700; color: #f5f0e8; margin-bottom: 10px; }
.feat-desc { font-size: 15px; color: #888; line-height: 1.8; }

/* ── AUTH CARD ── */
.auth-card {
    background: #15151a; border: 1px solid #2a2a2e;
    border-radius: 18px; padding: 40px 38px 24px;
    max-width: 460px; margin: 0 auto;
}
.auth-title { font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 900; color: #fff; margin-bottom: 4px; }
.auth-sub { font-size: 15px; color: #888; margin-bottom: 4px; }

/* ── INPUT FIELDS — cream background, BLACK text ── */
.stTextInput > div > div > input {
    background: #f4f1eb !important;
    border: 1.5px solid #ccc8c0 !important;
    border-radius: 9px !important;
    color: #111111 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 12px 16px !important;
    caret-color: #c0392b !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c0392b !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(192,57,43,0.12) !important;
    color: #111111 !important;
}
.stTextInput > div > div > input::placeholder {
    color: #b0a898 !important;
    font-weight: 400 !important;
}
.stTextInput label {
    color: #b0a898 !important; font-size: 12px !important;
    font-weight: 600 !important; letter-spacing: 0.9px !important;
    text-transform: uppercase !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #b03020, #e74c3c) !important;
    color: #fff !important; border: none !important;
    border-radius: 9px !important; font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important; width: 100% !important;
    padding: 13px !important; letter-spacing: 0.2px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    box-shadow: 0 0 28px rgba(231,76,60,0.45) !important;
    transform: translateY(-1px) !important;
}
.ghost-btn .stButton > button {
    background: transparent !important;
    border: 1px solid #303030 !important;
    color: #999 !important;
    font-size: 13px !important;
    padding: 10px !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(255,255,255,0.04) !important;
    box-shadow: none !important; color: #ddd !important;
    border-color: #555 !important;
}

/* ── ALERTS ── */
.stAlert { border-radius: 9px !important; }

/* ── HOW IT WORKS ── */
.step-num { font-family: 'Playfair Display', serif; font-size: 60px; font-weight: 900; color: #e74c3c; line-height: 1; margin-bottom: 14px; }
.step-title { font-size: 16px; font-weight: 600; color: #e0dbd2; margin-bottom: 8px; }
.step-desc { font-size: 14px; color: #777; line-height: 1.8; }

/* ── FOOTER ── */
.dracu-footer { text-align: center; padding: 34px; border-top: 1px solid #1e1e22; color: White; font-size: 13px; margin-top: 40px; }
.dracu-footer strong { color: White; }

hr { border-color: #1e1e22 !important; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVBAR
# =========================================================
def render_navbar():
    right = f'<span class="nav-user-badge">👤 {st.session_state.username}</span>' if st.session_state.logged_in else ""
    st.markdown(f"""
    <div class="dracu-nav">
        <div>
            <div class="dracu-brand">Dracu<span>-Law</span></div>
            <div class="nav-tagline">AI Legal Intelligence Engine</div>
        </div>
        <div>{right}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================
def render_hero():
    if st.session_state.logged_in:
        first = st.session_state.username.split()[0]
        st.markdown(f"""
        <div class="hero-wrap">
            <div class="hero-eyebrow"><span class="hero-dot"></span> Welcome back, {first}</div>
            <div class="hero-title">Ready to<em>Analyze.</em></div>
            <div class="hero-sub">Your AI legal engine is standing by. Upload a contract and get instant risk scoring, clause flagging, and smart rewrites.</div>
        </div>
        """, unsafe_allow_html=True)

        # CHANGE 1: Analyzer + Logout buttons side-by-side in one row
        _, c2, _ = st.columns([1, 1.4, 1])
        with c2:
            btn_col1, btn_col2 = st.columns(2, gap="small")
            with btn_col1:
                if st.button("Open Analyzer", key="hero_analyze"):
                    st.switch_page("pages/app.py")
            with btn_col2:
                st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                if st.button("Log Out", key="hero_logout"):
                    st.session_state.logged_in = False
                    st.session_state.username  = ""
                    st.session_state.auth_mode = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="stats-row">
            <div class="stat-box"><div class="stat-num">98<span>%</span></div><div class="stat-label">Clause Detection</div></div>
            <div class="stat-box"><div class="stat-num">5<span>s</span></div><div class="stat-label">Avg Analysis Time</div></div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="hero-wrap">
            <div class="hero-eyebrow"><span class="hero-dot"></span> AI Legal Intelligence Engine</div>
            <div class="hero-title">Read Every Clause.<br><em>Miss Nothing.</em></div>
            <div class="hero-sub">Dracu-Law dissects contracts with surgical precision — surfacing red flags, comparing versions, and rewriting dangerous clauses before you sign.</div>
        </div>
        """, unsafe_allow_html=True)

        _, c2, _ = st.columns([1.6, 1, 1.6])
        with c2:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Get Started", key="hero_signup"):
                    st.session_state.auth_mode = "signup"
                    st.rerun()
            with b2:
                # CHANGE 2: Sign In scrolls to auth section via JS anchor
                if st.button("Sign In", key="hero_login"):
                    st.session_state.auth_mode = "login"
                    st.rerun()
                    # JS scroll is handled below after rerun renders the anchor

        st.markdown("""
        <div class="stats-row">
            <div class="stat-box"><div class="stat-num">98<span>%</span></div><div class="stat-label">Clause Detection</div></div>
            <div class="stat-box"><div class="stat-num">5<span>s</span></div><div class="stat-label">Avg Analysis Time</div></div>
        </div>
        """, unsafe_allow_html=True)

        # After rerun, if auth_mode is set, inject scroll JS
        if st.session_state.auth_mode in ("login", "signup"):
            st.markdown("""
            <script>
                window.addEventListener('load', function() {
                    var el = document.getElementById('auth-section');
                    if (el) { el.scrollIntoView({behavior: 'smooth'}); }
                });
            </script>
            """, unsafe_allow_html=True)


# =========================================================
# AUTH FORMS
# =========================================================
def render_auth():
    # CHANGE 2: Anchor div so Sign In button can scroll here
    st.markdown('<div id="auth-section"></div>', unsafe_allow_html=True)
    # Also inject scroll JS here so it fires after the DOM is ready
    st.markdown("""
    <script>
        (function() {
            function scrollToAuth() {
                var el = document.getElementById('auth-section');
                if (el) { el.scrollIntoView({behavior: 'smooth'}); }
                else { setTimeout(scrollToAuth, 100); }
            }
            scrollToAuth();
        })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()

    _, c2, _ = st.columns([1, 1.5, 1])
    with c2:
        if st.session_state.auth_mode == "login":
            st.markdown("""
            <div class="auth-card">
                <div class="auth-title">Welcome back.</div>
                <div class="auth-sub">Sign in to your Dracu-Law account to continue.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            email    = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", placeholder="Your password", type="password", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In →", key="do_login"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, result = login_user(email, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username  = result
                        st.session_state.auth_mode = None
                        st.success(f"Welcome back, {result.split()[0]}! 👋")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("No account yet? Sign up →", key="switch_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.auth_mode == "signup":
            st.markdown("""
            <div class="auth-card">
                <div class="auth-title">Create account.</div>
                <div class="auth-sub">Start analyzing contracts in seconds — it's free.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            name     = st.text_input("Full Name", placeholder="Jane Smith", key="signup_name")
            email    = st.text_input("Email", placeholder="you@example.com", key="signup_email")
            password = st.text_input("Password", placeholder="Min. 6 characters", type="password", key="signup_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account →", key="do_signup"):
                if not name or not email or len(password) < 6:
                    st.error("❌ Please fill in all fields. Password must be at least 6 characters.")
                else:
                    ok, msg = register_user(name, email, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username  = name
                        st.session_state.auth_mode = None
                        st.success(f"Account created! Welcome, {name.split()[0]} ⚡")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Already have an account? Sign in →", key="switch_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# FEATURES
# =========================================================
def render_features():
    st.divider()
    st.markdown("""
    <div style="padding: 60px 0 0;">
        <div class="section-label">// What we do</div>
        <div class="section-title">Three tools.<br>Total clarity.</div>
    </div>
    """, unsafe_allow_html=True)

    cards = [
        ("🔬", "Deep Analysis",
         "Upload any PDF contract and get an instant risk score from 1–10, flagged clauses, a plain-English summary, and actionable suggestions — all in seconds."),
        ("⚖️", "Contract Comparison",
         "Pit two contracts against each other. The AI highlights key differences and declares a clear winner for the signer's best interests."),
        ("✍️", "Smart Rewriting",
         "Select the clauses that concern you. Dracu-Law rewrites them in your favour and exports a polished Word document ready to negotiate with."),
    ]
    for col, (icon, title, desc) in zip(st.columns(3, gap="medium"), cards):
        with col:
            st.markdown(f"""
            <div class="feat-card">
                <span class="feat-icon">{icon}</span>
                <div class="feat-title">{title}</div>
                <div class="feat-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# HOW IT WORKS
# =========================================================
def render_how():
    st.divider()
    st.markdown("""
    <div style="padding: 40px 0 0;">
        <div class="section-label">// How it works</div>
        <div class="section-title">Four steps to confidence.</div>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Upload Your Contract",  "Drop any PDF — NDAs, employment agreements, leases, service contracts — into the analyzer."),
        ("02", "AI Scans Every Clause", "Our LLM engine reads every sentence, scores risk 1–10, and maps problem areas with precision."),
        ("03", "Review Findings",       "A color-coded dashboard surfaces red flags and suggestions. Compare two contracts side-by-side if needed."),
        ("04", "Export Improved Draft", "Choose which clauses to fix and download a rewritten contract as a polished Word document."),
    ]
    for col, (num, title, desc) in zip(st.columns(4, gap="large"), steps):
        with col:
            st.markdown(f"""
            <div style="padding: 16px 4px;">
                <div class="step-num">{num}</div>
                <div class="step-title">{title}</div>
                <div class="step-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
def render_footer():
    st.divider()
    st.markdown("""
    <div class="dracu-footer">
        ⚖️ <strong>Dracu-Law</strong> &nbsp;·&nbsp; Powered by <strong>Groq LLMs</strong> &nbsp;·&nbsp; Built with <strong>Streamlit</strong><br>
        <span style="font-size:11px;color:White;">AI-generated analysis is not a substitute for professional legal advice.</span>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN
# =========================================================
render_navbar()
render_hero()

if not st.session_state.logged_in and st.session_state.auth_mode in ("login", "signup"):
    render_auth()
elif not st.session_state.logged_in:
    render_features()
    render_how()

render_footer()