import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from parser import extract_text
from analyzer import analyze_contract
from formatter import format_results, get_risk_label

import base64
from pathlib import Path

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dracu-Law | AI Contract Analyzer",
    page_icon="🧛",
    layout="wide"
)

# ── ENCODE LOGO AS BASE64 (place your logo.png in same folder) ────────────────
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

logo_b64 = get_base64_image("logo.png")  # <-- place your logo image as logo.png
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo" alt="Dracu-Law Logo">'
    if logo_b64
    else '<div class="nav-logo-fallback">🧛</div>'
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;900&family=Inter:wght@400;500;600&display=swap');

        /* ── GLOBAL BACKGROUND ── */
        .stApp {{
            background: #f4f1ee;
        }}

        /* ── NAVBAR ── */
        .dracu-navbar {{
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 28px;
            background: #1c1c1e;
            border-bottom: 3px solid #c0392b;
            border-radius: 0 0 10px 10px;
            margin-bottom: 0.5rem;
        }}

        .nav-logo {{
            height: 60px;
            width: 60px;
            object-fit: contain;
            border-radius: 8px;
            flex-shrink: 0;
        }}

        .nav-logo-fallback {{
            font-size: 2.8rem;
            line-height: 1;
        }}

        .nav-brand {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .nav-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.75rem;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 1px;
            line-height: 1.1;
        }}

        .nav-title span {{
            color: #e74c3c !important;
            -webkit-text-fill-color: #e74c3c !important;
        }}

        .nav-tagline {{
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: rgba(255,255,255,0.45);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 2px;
        }}

        /* ── HERO HEADING ── */
        .hero-section {{
            text-align: center;
            padding: 2.2rem 1rem 1.2rem;
        }}

        .hero-title {{
            font-family: 'Playfair Display', serif;
            font-size: 2.6rem;
            font-weight: 900;
            color: #1c1c1e;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        .hero-title span {{
            color: #c0392b;
        }}

        .hero-subtitle {{
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #666;
            letter-spacing: 0.2px;
        }}

        /* ── SIDEBAR ── */
        section[data-testid="stSidebar"] {{
            background: #1c1c1e !important;
            border-right: 1px solid #333 !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: rgba(255,255,255,0.75) !important;
            font-family: 'Inter', sans-serif !important;
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
            color: #e74c3c !important;
            font-family: 'Playfair Display', serif !important;
        }}

        /* ── BUTTONS ── */
        .stButton > button {{
            background: #c0392b !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            font-size: 0.95rem !important;
            box-shadow: 0 2px 8px rgba(192,57,43,0.35) !important;
            transition: all 0.2s ease !important;
        }}

        .stButton > button:hover {{
            background: #a93226 !important;
            box-shadow: 0 4px 14px rgba(192,57,43,0.45) !important;
            transform: translateY(-1px) !important;
        }}

        [data-testid="stDownloadButton"] > button {{
            background: #2c3e50 !important;
            color: #ffffff !important;
            border: none !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }}

        /* ── RISK BOX ── */
        .risk-box {{
            padding: 1.4rem;
            border-radius: 10px;
            text-align: center;
            font-size: 1.4rem;
            font-weight: 700;
            font-family: 'Playfair Display', serif;
            border: 2px solid;
        }}
        .risk-low  {{ background: #eafaf1; color: #1e8449; border-color: #a9dfbf; }}
        .risk-mid  {{ background: #fef9e7; color: #b7950b; border-color: #f9e79f; }}
        .risk-high {{ background: #fdedec; color: #c0392b; border-color: #f5b7b1; }}

        /* ── SECTION HEADERS ── */
        .section-header {{
            font-family: 'Playfair Display', serif;
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 1.4rem;
            margin-bottom: 0.4rem;
            color: #1c1c1e;
            letter-spacing: 0.5px;
            border-left: 3px solid #c0392b;
            padding-left: 10px;
        }}

        /* ── GENERAL TEXT ── */
        p, li {{
            font-family: 'Inter', sans-serif !important;
            color: #333 !important;
            font-size: 0.97rem !important;
        }}

        h1, h2, h3 {{
            font-family: 'Playfair Display', serif !important;
            color: #1c1c1e !important;
        }}

        /* Progress bar */
        .stProgress > div > div {{
            background: #c0392b !important;
        }}

        /* Placeholder */
        .placeholder-text h2 {{
            font-family: 'Playfair Display', serif !important;
            color: #999 !important;
            font-size: 1.5rem !important;
        }}

        .placeholder-text p {{
            color: #aaa !important;
            font-family: 'Inter', sans-serif !important;
        }}
    </style>
""", unsafe_allow_html=True)

# ── NAVBAR ────────────────────────────────────────────────────────────────────
st.markdown(f"""
    <div class="dracu-navbar">
        {logo_html}
        <div class="nav-brand">
            <div class="nav-title">Dracu<span>-Law</span></div>
            <div class="nav-tagline">We Sink Our Teeth Into Every Clause</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
    <div class="hero-section">
        <div class="hero-title">⚖ AI Contract <span>Analyzer</span></div>
        <div class="hero-subtitle">Upload any legal contract and receive an instant plain-English risk analysis — powered by AI.</div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ── SIDEBAR: SETTINGS ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    model_choice = st.selectbox(
        "Choose LLM Model",
        options=["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "openai/gpt-oss-20b","llama-3.1-8b-instant"],
        index=0,
        help="All models run via Groq for fast inference."
    )
    st.markdown("---")
    st.markdown("**📌 How it works:**")
    st.markdown("1. Upload a PDF contract")
    st.markdown("2. Click Analyze")
    st.markdown("3. Get risk score, red flags, plain-English summary & suggestions")
    st.markdown("---")
    st.caption("Powered by Groq + LLaMA")

# ── FILE UPLOAD ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📁 Upload your contract (PDF only)",
    type=["pdf"],
    help="Maximum recommended size: 10MB. Scanned PDFs may not work well."
)

if uploaded_file:
    st.success(f"✅ File uploaded: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)")

    if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):

        with st.spinner("📖 Reading your contract..."):
            try:
                contract_text = extract_text(uploaded_file)
            except ValueError as e:
                st.error(f"❌ Could not read PDF: {e}")
                st.stop()

        st.info(f"📃 Extracted **{len(contract_text.split())} words** from the document.")

        with st.spinner("🤖 AI is analyzing the contract..."):
            try:
                raw_result = analyze_contract(contract_text, model=model_choice)
            except (ValueError, ConnectionError) as e:
                st.error(f"❌ Analysis failed: {e}")
                st.stop()

        result = format_results(raw_result)

        st.divider()
        st.subheader("📊 Analysis Results")

        # ── RISK SCORE ────────────────────────────────────────────────────────
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            label, color = get_risk_label(result["risk_score"])
            risk_class = "risk-low" if color == "green" else ("risk-mid" if color == "orange" else "risk-high")
            st.markdown(
                f'<div class="risk-box {risk_class}">Risk Score: {result["risk_score"]} / 10<br>{label}</div>',
                unsafe_allow_html=True
            )
            st.progress(result["risk_score"] / 10)

        st.divider()

        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown('<div class="section-header">🚩 Red Flags</div>', unsafe_allow_html=True)
            if result["red_flags"]:
                for flag in result["red_flags"]:
                    st.warning(flag)
            else:
                st.success("No major red flags detected.")

        with right_col:
            st.markdown('<div class="section-header">💡 Suggestions</div>', unsafe_allow_html=True)
            if result["suggestions"]:
                for suggestion in result["suggestions"]:
                    st.info(suggestion)
            else:
                st.write("No specific suggestions.")

        st.markdown('<div class="section-header">📝 Plain English Summary</div>', unsafe_allow_html=True)
        st.write(result["explanation"])

        with st.expander("📄 View Extracted Contract Text"):
            st.text_area("Raw Text", contract_text, height=300)

        report = f"""DRACU-LAW — AI CONTRACT ANALYSIS REPORT
==========================================
File: {uploaded_file.name}
Model: {model_choice}

RISK SCORE: {result['risk_score']} / 10
{get_risk_label(result['risk_score'])[0]}

RED FLAGS:
{chr(10).join(f"- {flag}" for flag in result['red_flags']) if result['red_flags'] else "None found"}

PLAIN ENGLISH SUMMARY:
{result['explanation']}

SUGGESTIONS:
{chr(10).join(f"- {s}" for s in result['suggestions']) if result['suggestions'] else "None"}
"""
        st.download_button(
            label="⬇️ Download Report as .txt",
            data=report,
            file_name=f"dracula_analysis_{uploaded_file.name.replace('.pdf', '')}.txt",
            mime="text/plain",
            use_container_width=True
        )

else:
    st.markdown("""
    <div class="placeholder-text" style="text-align:center; padding: 3rem;">
        <h2>Upload a PDF contract above to get started</h2>
        <p>Supports employment contracts, NDAs, rental agreements, freelance contracts, and more.</p>
    </div>
    """, unsafe_allow_html=True)