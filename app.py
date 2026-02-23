import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from parser import extract_text
from analyzer import analyze_contract
from formatter import format_results, get_risk_label

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Contract Simplifier",
    page_icon="📄",
    layout="wide"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1a1a2e;
        }
        .risk-box {
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .risk-low  { background-color: #d4edda; color: #155724; }
        .risk-mid  { background-color: #fff3cd; color: #856404; }
        .risk-high { background-color: #f8d7da; color: #721c24; }
        .section-header {
            font-size: 1.2rem;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📄 AI Contract Simplifier</div>', unsafe_allow_html=True)
st.markdown("Upload any legal contract PDF and get an instant plain-English risk analysis powered by AI.")
st.divider()

# ── SIDEBAR: SETTINGS ────────────────────────────────────────────────────────
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
    st.caption("Built for Hackathon 🚀 | Powered by Groq + LLaMA")

# ── FILE UPLOAD ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📁 Upload your contract (PDF only)",
    type=["pdf"],
    help="Maximum recommended size: 10MB. Scanned PDFs may not work well."
)

if uploaded_file:
    st.success(f"✅ File uploaded: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)")

    # ── ANALYZE BUTTON ────────────────────────────────────────────────────────
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

        # ── TWO COLUMN LAYOUT ─────────────────────────────────────────────────
        left_col, right_col = st.columns(2)

        with left_col:
            # Red Flags
            st.markdown('<div class="section-header">🚩 Red Flags</div>', unsafe_allow_html=True)
            if result["red_flags"]:
                for flag in result["red_flags"]:
                    st.warning(flag)
            else:
                st.success("No major red flags detected.")

        with right_col:
            # Suggestions
            st.markdown('<div class="section-header">💡 Suggestions</div>', unsafe_allow_html=True)
            if result["suggestions"]:
                for suggestion in result["suggestions"]:
                    st.info(suggestion)
            else:
                st.write("No specific suggestions.")

        # ── PLAIN ENGLISH EXPLANATION ─────────────────────────────────────────
        st.markdown('<div class="section-header">📝 Plain English Summary</div>', unsafe_allow_html=True)
        st.write(result["explanation"])

        # ── EXPANDABLE: RAW CONTRACT TEXT ─────────────────────────────────────
        with st.expander("📄 View Extracted Contract Text"):
            st.text_area("Raw Text", contract_text, height=300)

        # ── DOWNLOAD REPORT ───────────────────────────────────────────────────
        report = f"""AI CONTRACT ANALYSIS REPORT
==============================
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
            file_name=f"contract_analysis_{uploaded_file.name.replace('.pdf', '')}.txt",
            mime="text/plain",
            use_container_width=True
        )

else:
    # ── PLACEHOLDER WHEN NO FILE UPLOADED ─────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 3rem; color: #888;">
        <h2>👆 Upload a PDF contract above to get started</h2>
        <p>Supports employment contracts, NDAs, rental agreements, freelance contracts, and more.</p>
    </div>
    """, unsafe_allow_html=True)