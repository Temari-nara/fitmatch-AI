"""
app.py — Main Streamlit application for FitMatch AI

Run with: streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv  # Reads .env file for API keys

from utils.resume_parser import extract_text_from_pdf, clean_text
from utils.analyzer import analyze_resume, rewrite_resume, analyze_ats_keywords
from utils.pdf_generator import generate_pdf

# Load environment variables from .env file (for local development)
load_dotenv()

# ─── Page config (must be the first Streamlit command) ───
st.set_page_config(page_title="FitMatch AI", page_icon="🎯", layout="wide")

# ─── App header ───
st.title("FitMatch AI 🎯")
st.markdown("**Smart Resume Analyzer & Job Fit Scorer** — Powered by Llama 3 on Groq")
st.markdown("---")

# ─── Initialize session state ───
# session_state lets us keep data when the user switches tabs
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "job_role" not in st.session_state:
    st.session_state.job_role = ""
if "results" not in st.session_state:
    st.session_state.results = None

# ─── Create the three tabs ───
tab1, tab2, tab3 = st.tabs(["📄 Resume", "💼 Job Target", "📊 Results"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — Resume Input
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    st.header("Upload or Paste Your Resume")

    # Two columns: one for upload, one for paste
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Option A: Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload your resume as a PDF file",
        )
        if uploaded_file is not None:
            # Extract text from the uploaded PDF
            extracted = extract_text_from_pdf(uploaded_file)
            st.session_state.resume_text = clean_text(extracted)
            st.success("PDF uploaded and text extracted!")

    with col2:
        st.subheader("Option B: Paste Text")
        pasted_text = st.text_area(
            "Paste your resume text here",
            height=300,
            placeholder="Copy and paste your resume content here...",
            value=st.session_state.resume_text,
        )
        # Update session state if user types/pastes something
        if pasted_text:
            st.session_state.resume_text = clean_text(pasted_text)

    # Show what we have so far
    if st.session_state.resume_text:
        with st.expander("👀 Preview extracted resume text", expanded=False):
            st.text(st.session_state.resume_text[:3000])  # Show first 3000 chars
        st.info(f"✅ Resume loaded — {len(st.session_state.resume_text)} characters")
    else:
        st.warning("No resume loaded yet. Upload a PDF or paste text above.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — Job Target Input
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.header("What Role Are You Targeting?")

    st.subheader("Option A: Paste a Job Description")
    jd_input = st.text_area(
        "Paste the full job description here",
        height=250,
        placeholder="Paste the job posting text here...",
        value=st.session_state.job_description,
    )
    st.session_state.job_description = jd_input

    st.markdown("**— OR —**")

    st.subheader("Option B: Just Enter a Job Title")
    role_input = st.text_input(
        "Type a job role (e.g. 'Data Analyst', 'Python Developer')",
        value=st.session_state.job_role,
        placeholder="e.g. Frontend Developer",
    )
    st.session_state.job_role = role_input

    # Quick status check
    if jd_input.strip():
        st.info("✅ Job description provided — this will be used for analysis.")
    elif role_input.strip():
        st.info("✅ Job role provided — the AI will generate a typical JD for this role.")
    else:
        st.warning("Please provide a job description or job role above.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — Analysis Results
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.header("Your Fit Analysis")

    # Check if we have both inputs
    has_resume = bool(st.session_state.resume_text.strip())
    has_job = bool(st.session_state.job_description.strip() or st.session_state.job_role.strip())

    if not has_resume:
        st.warning("⬅️ Go to the **Resume** tab and upload or paste your resume first.")
    elif not has_job:
        st.warning("⬅️ Go to the **Job Target** tab and enter a job description or role.")
    else:
        # Show the Analyze button only when both inputs are ready
        if st.button("🔍 Analyze Now", type="primary", use_container_width=True):
            with st.spinner("Analyzing your resume with AI... This takes a few seconds."):
                results = analyze_resume(
                    resume_text=st.session_state.resume_text,
                    job_description=st.session_state.job_description,
                    job_role=st.session_state.job_role,
                )
                st.session_state.results = results

    # ─── Display results if we have them ───
    if st.session_state.results:
        results = st.session_state.results

        # Check for errors
        if "error" in results:
            st.error(f"❌ {results['error']}")
            if "raw_response" in results:
                with st.expander("Show raw AI response (for debugging)"):
                    st.code(results["raw_response"])
        else:
            # ── Show Generated JD (if role-only mode was used) ──
            if "generated_jd" in results:
                with st.expander("📝 Generated Job Description (AI-created for this role)"):
                    st.write(results["generated_jd"])

            # ── Row 1: Fit Score ──
            score = results.get("fit_score", 0)

            # Pick color based on score
            if score >= 70:
                color = "🟢"
                bar_color = "#28a745"  # green
            elif score >= 50:
                color = "🟡"
                bar_color = "#ffc107"  # yellow
            else:
                color = "🔴"
                bar_color = "#dc3545"  # red

            # Big score display
            st.markdown(
                f"<h1 style='text-align:center;'>{color} Fit Score: {score}/100</h1>",
                unsafe_allow_html=True,
            )
            # Visual progress bar
            st.progress(score / 100)

            st.markdown("---")

            # ── Row 2: Matched vs Missing Skills (side by side) ──
            col_match, col_miss = st.columns(2)

            with col_match:
                st.subheader("✅ Matched Skills")
                matched = results.get("matched_skills", [])
                if matched:
                    for skill in matched:
                        st.markdown(f"- {skill}")
                else:
                    st.write("No matched skills found.")

            with col_miss:
                st.subheader("❌ Missing Skills")
                missing = results.get("missing_skills", [])
                if missing:
                    for skill in missing:
                        st.markdown(f"- {skill}")
                else:
                    st.write("No missing skills — great match!")

            st.markdown("---")

            # ── Row 3: Strengths & Suggestions (side by side) ──
            col_str, col_sug = st.columns(2)

            with col_str:
                st.subheader("💪 Resume Strengths")
                strengths = results.get("strengths", [])
                if strengths:
                    for item in strengths:
                        st.markdown(f"- {item}")
                else:
                    st.write("No strengths identified.")

            with col_sug:
                st.subheader("💡 Improvement Suggestions")
                suggestions = results.get("suggestions", [])
                if suggestions:
                    for item in suggestions:
                        st.markdown(f"- {item}")
                else:
                    st.write("No suggestions — your resume looks solid!")

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # SECTION: ATS Keyword Optimizer
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            st.divider()
            st.subheader("🔑 ATS Keyword Optimizer")
            st.write("See exactly which keywords from the job description are in your resume.")

            # We need a JD for keyword analysis — use provided or generated one
            jd_for_ats = st.session_state.job_description.strip()
            if not jd_for_ats and "generated_jd" in results:
                jd_for_ats = results["generated_jd"]

            if not jd_for_ats:
                st.info("ATS keyword analysis requires a job description. Enter one in the Job Target tab.")
            elif st.button("🔍 Run ATS Keyword Analysis", key="ats_btn"):
                with st.spinner("Scanning for ATS keywords..."):
                    ats_results = analyze_ats_keywords(
                        st.session_state.resume_text, jd_for_ats
                    )
                    st.session_state["ats_results"] = ats_results

            # Display ATS results if available
            if st.session_state.get("ats_results"):
                ats = st.session_state["ats_results"]

                if "error" in ats:
                    st.error(f"❌ {ats['error']}")
                else:
                    # Keyword score
                    ks = ats.get("keyword_score", 0)
                    st.markdown(f"**ATS Keyword Match: {ks}%**")
                    st.progress(ks / 100)

                    col_found, col_missing = st.columns(2)

                    with col_found:
                        st.markdown("**✅ Found in Resume:**")
                        for kw in ats.get("found_keywords", []):
                            st.markdown(f"- :green[{kw}]")

                    with col_missing:
                        st.markdown("**❌ Missing from Resume:**")
                        for kw in ats.get("missing_keywords", []):
                            st.markdown(f"- :red[{kw}]")

                    # Show insertion suggestions
                    insert_tips = ats.get("insert_suggestions", [])
                    if insert_tips:
                        with st.expander("💡 How to add missing keywords", expanded=True):
                            for tip in insert_tips:
                                if isinstance(tip, dict):
                                    st.markdown(
                                        f"- **{tip.get('keyword', '')}** → {tip.get('suggestion', '')}"
                                    )

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # SECTION: AI Resume Rewriter
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            st.divider()
            st.subheader("✨ AI Resume Rewriter")
            st.write("Want AI to update your resume based on the gaps found?")

            if st.button("📝 Rewrite My Resume", key="rewrite_btn"):
                with st.spinner("Rewriting your resume... This takes a few seconds."):
                    rewritten = rewrite_resume(
                        resume_text=st.session_state.resume_text,
                        missing_skills=results.get("missing_skills", []),
                        suggestions=results.get("suggestions", []),
                    )
                    st.session_state["rewritten_resume"] = rewritten

            # Display rewritten resume if available
            if st.session_state.get("rewritten_resume"):
                rewritten_text = st.session_state["rewritten_resume"]

                # Check if the rewriter returned an error
                if rewritten_text.startswith("[Error]"):
                    st.error(rewritten_text)
                else:
                    st.caption("⚠️ Always review the rewritten resume before using it. AI does not fabricate, but double-check!")
                    edited_resume = st.text_area(
                        "Your Updated Resume (editable — make final tweaks here)",
                        value=rewritten_text,
                        height=400,
                        key="editable_resume",
                    )

                    # Generate PDF and offer download
                    pdf_bytes = bytes(generate_pdf(edited_resume))
                    st.download_button(
                        label="📥 Download Updated Resume as PDF",
                        data=pdf_bytes,
                        file_name="updated_resume_fitmatch.pdf",
                        mime="application/pdf",
                    )

# ─── Footer ───
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>"
    "Built with Streamlit + Groq (Llama 3) | FitMatch AI Workshop Demo"
    "</p>",
    unsafe_allow_html=True,
)
