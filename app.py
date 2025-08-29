
import os
import streamlit as st
from utils import (
    detect_sections,
    extract_text_from_file,
    clean_text,
    top_keywords,
    suggest_missing_keywords,
    compute_similarity,
    check_ats_readability,
    detect_pdf_formatting_issues,
    create_ats_preview,
    extract_keywords_with_scores,
    smart_bullets_for_missing,
    get_keyword_coverage_explanation,
    select_most_relevant_keywords,
)
import io
from datetime import datetime

def render_keywords_block(jd_text, resume_text, display_k=30):
    """Render simplified keywords block with detailed score explanation."""
    
    # Extract keywords with scores
    ranked_keywords = extract_keywords_with_scores(jd_text, top_n=display_k)
    all_keywords = [kw for kw, score in ranked_keywords]
    
    # Select most relevant keywords for this specific JD
    relevant_keywords = select_most_relevant_keywords(ranked_keywords, jd_text, top_k=15)
    
    # Check coverage for all keywords
    resume_lower = resume_text.lower()
    present_keywords = []
    missing_keywords = []
    
    for keyword in all_keywords:
        if keyword.lower() in resume_lower:
            present_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Calculate coverage
    coverage_count = len(present_keywords)
    total_count = len(all_keywords)
    coverage_percent = (coverage_count / total_count * 100) if total_count > 0 else 0
    
    # Render the block
    st.markdown("---")
    st.subheader("🎯 Keyword Coverage")
    
    # Coverage progress
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Current Coverage: {coverage_count} of {total_count} keywords**")
        st.progress(coverage_percent / 100, text=f"{coverage_percent:.0f}%")
    with col2:
        if coverage_percent == 100:
            st.success("🎉 **100% Coverage!**")
        elif coverage_percent >= 80:
            st.warning(f"**{coverage_percent:.0f}%** - Almost there!")
        elif coverage_percent >= 60:
            st.info(f"**{coverage_percent:.0f}%** - Good start!")
        else:
            st.error(f"**{coverage_percent:.0f}%** - Needs work!")
    
    # Display all keywords as simple chips
    st.markdown("---")
    st.markdown("**📋 All JD Keywords (Top 30):**")
    
    # Create simple keyword chips
    chip_html = ""
    for keyword in all_keywords:
        if keyword in present_keywords:
            chip_class = "chip ok"
            chip_text = f"✅ {keyword}"
        else:
            chip_class = "chip miss"
            chip_text = f"❌ {keyword}"
        
        chip_html += f'<span class="{chip_class}">{chip_text}</span>'
    
    # Inject CSS and render chips
    st.markdown(f"""
    <style>
    .chip {{
        display: inline-block;
        padding: 4px 8px;
        margin: 2px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: normal;
    }}
    .chip.ok {{
        background-color: #d4edda;
        color: #155724;
    }}
    .chip.miss {{
        background-color: #f8d7da;
        color: #721c24;
    }}
    </style>
    <div style="margin: 10px 0;">
        {chip_html}
    </div>
    """, unsafe_allow_html=True)
    
    # Coverage breakdown
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Present in your resume:")
        if present_keywords:
            for keyword in present_keywords:
                st.markdown(f'<span style="background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin: 2px;">{keyword}</span>', unsafe_allow_html=True)
            st.caption(f"Great job! You're covering {len(present_keywords)} out of {total_count} top JD keywords.")
        else:
            st.warning("_None detected from top JD keywords._")
    
    with col2:
        st.markdown("### ❌ Missing / low-visibility keywords:")
        if missing_keywords:
            # Show only the most relevant missing keywords (top 8-10)
            relevant_missing = [kw for kw in relevant_keywords if kw in missing_keywords][:10]
            for keyword in relevant_missing:
                st.markdown(f'<span style="background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin: 2px;">{keyword}</span>', unsafe_allow_html=True)
            st.caption(f"Showing top {len(relevant_missing)} most relevant missing keywords. Add these to improve your coverage.")
        else:
            st.success("Perfect! You cover all JD terms.")
    
    # Smart bullet suggestions for most relevant missing keywords
    if missing_keywords:
        st.markdown("---")
        st.markdown("**💡 Smart Bullet Suggestions (add these to your resume):**")
        
        # Use most relevant missing keywords for bullet suggestions
        relevant_missing = [kw for kw in relevant_keywords if kw in missing_keywords][:8]
        smart_bullets = smart_bullets_for_missing(relevant_missing)
        for bullet in smart_bullets:
            st.markdown(bullet)
        
        st.caption("💡 **Tip:** Customize these bullets with your specific metrics and achievements.")
    
    return present_keywords, missing_keywords, coverage_percent

st.set_page_config(page_title="ATS Checker MVP", page_icon="✅", layout="centered")

st.title("ATS Checker — 1‑Day MVP")
st.caption("Upload your Resume (PDF/DOCX/TXT) + paste a Job Description. Get a match score and concrete keyword tips.")

with st.expander("How scoring works (simple & transparent):", expanded=False):
    st.markdown("""
- **Keyword coverage (70%)** — share of top JD keywords that appear in your resume (after simple normalization).
- **Cosine similarity (30%)** — TF‑IDF cosine similarity between JD and resume texts.
- We extract ~**30 top keywords** from the JD by frequency (stopwords removed).
- This is a lightweight heuristic, not a full ATS replacement. Great for quick iteration.
""")

colA, colB = st.columns(2)
with colA:
    resume_file = st.file_uploader("Upload Resume", type=["pdf","docx","txt"])
with colB:
    jd_source = st.radio("Job Description input", ["Paste text", "Upload file"])

if jd_source == "Paste text":
    jd_text = st.text_area("Paste Job Description here", height=220, placeholder="Paste the job description…")
else:
    jd_file = st.file_uploader("Upload JD file", type=["pdf","docx","txt"], key="jd_file")
    jd_text = ""
    if jd_file:
        jd_text = extract_text_from_file(jd_file)

# Initialize variables to prevent errors
final_score = 0
coverage_percent = 0.0
sim = 0.0
ats_check = {"score": 0, "status": "unknown", "ats_friendly": False, "issues": [], "recommendations": [], "metrics": {"total_chars": 0, "total_words": 0, "total_lines": 0, "special_char_ratio": 0.0}}
sections_found = set()
kw = []
present = []
missing = []

run = st.button("Run ATS check", type="primary", use_container_width=True)

if run:
    if not resume_file:
        st.error("Please upload a resume.")
        st.stop()
    if not jd_text or len(jd_text.strip()) < 40:
        st.error("Please provide a reasonably sized Job Description (≥ 40 chars).")
        st.stop()

    with st.spinner("Parsing files and computing scores…"):
        resume_text_raw = extract_text_from_file(resume_file)
        jd_text_raw = jd_text

        resume_text = clean_text(resume_text_raw)
        jd_text_clean = clean_text(jd_text_raw)

        # Check ATS readability
        ats_check = check_ats_readability(resume_text_raw, resume_file.name if resume_file.name else "")
        
        # Check for PDF formatting issues
        pdf_issues = detect_pdf_formatting_issues(resume_text_raw)
        


        # Section detection (resume hygiene tips)
        sections_found = detect_sections(resume_text_raw)
        
        # Create ATS preview
        ats_preview = create_ats_preview(resume_text_raw, sections_found)

        # Extract top JD keywords
        kw = top_keywords(jd_text_clean, top_n=30)
        
        # Compute scores
        sim = compute_similarity(jd_text_clean, resume_text)  # 0..1
        present, missing, _ = suggest_missing_keywords(jd_text_clean, resume_text, top_n=12)
        
        # Calculate coverage as decimal (0.0-1.0) for consistent calculations
        if len(kw) == 0:
            # No JD keywords found, use similarity score only
            coverage_decimal = 0.0
            coverage_percent = 0.0
            keyword_score = 0
        else:
            coverage_decimal = len(present) / max(1, len(present) + len(missing))
            coverage_percent = round(coverage_decimal * 100, 1)
            keyword_score = coverage_decimal * 100  # 0-100
        
        similarity_score = sim * 100  # 0-100
        
        # Final score: weighted combination of keyword coverage and cosine similarity
        final_score = int(round(keyword_score * 0.7 + similarity_score * 0.3))
        
        # Ensure final_score is within valid range for progress bar
        final_score = max(0, min(100, final_score))

    st.subheader("Your ATS Match Score")
    
    # Big score display with visual impact
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Large score display
        if final_score >= 80:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #28a745; font-size: 48px; margin: 0;">{final_score}/100</h1>
                <p style="color: #28a745; font-size: 18px; margin: 5px 0;">🎉 Excellent Match</p>
            </div>
            """, unsafe_allow_html=True)
        elif final_score >= 60:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #ffc107; font-size: 48px; margin: 0;">{final_score}/100</h1>
                <p style="color: #ffc107; font-size: 18px; margin: 5px 0;">⚠️ Good Match</p>
            </div>
            """, unsafe_allow_html=True)
        elif final_score >= 40:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #fd7e14; font-size: 48px; margin: 0;">{final_score}/100</h1>
                <p style="color: #fd7e14; font-size: 18px; margin: 5px 0;">🟠 Fair Match</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #dc3545; font-size: 48px; margin: 0;">{final_score}/100</h1>
                <p style="color: #dc3545; font-size: 18px; margin: 5px 0;">❌ Needs Work</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Progress bar below the score
    st.progress(final_score/100.0, text=f"Progress: {final_score}%")
    
    # Simple metrics in columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Text similarity", f"{int(round(sim*100))}%")
    with col2:
        st.metric("Overall score", f"{final_score}/100", help="70% keyword coverage + 30% cosine similarity")
    
    # Add detailed score explanation
    with st.expander("📊 How is my score calculated?", expanded=False):
        explanation = get_keyword_coverage_explanation(len(present), len(kw), sim)
        st.markdown(explanation)

    # Show PDF formatting issues prominently if detected
    if pdf_issues["has_issues"]:
        st.markdown("---")
        st.error("🚨 **CRITICAL: PDF Formatting Issues Detected**")
        st.warning("Your PDF has formatting problems that will prevent ATS systems from reading your resume properly!")
        
        for issue in pdf_issues["issues"]:
            st.markdown(issue)
        
        st.info("**💡 How to Fix This:**")
        for rec in pdf_issues["recommendations"]:
            st.markdown(rec)
        
        st.markdown("**⚠️ Impact:** Your resume will likely be rejected by ATS systems and job platforms like Glassdoor, LinkedIn, etc.")

    # Keyword Coverage Section - Simplified coverage block
    render_keywords_block(jd_text_clean, resume_text)

    # Advanced Analysis Section - Collapsible for detailed info
    st.markdown("---")
    with st.expander("🔬 Advanced Analysis", expanded=False):
        st.subheader("📊 Detailed Metrics & Analysis")
        
        # Cosine similarity and technical details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Cosine Similarity:**")
            st.metric("Text similarity", f"{int(round(sim*100))}%", help="TF-IDF similarity between JD and resume")
        with col2:
            st.markdown("**Keyword Analysis:**")
            st.metric("JD keywords found", f"{len(present)}/{len(kw)}", help="Keywords present in resume")
        
        # ATS Readability Check
        st.markdown("---")
        st.subheader("🔍 ATS Readability Check")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if ats_check["ats_friendly"]:
                st.success(f"✅ **ATS Compatible** - Score: {ats_check['score']}/100")
            else:
                st.error(f"❌ **ATS Issues Detected** - Score: {ats_check['score']}/100")
        
        with col2:
            status_colors = {
                "excellent": "🟢",
                "good": "🟡", 
                "fair": "🟠",
                "poor": "🔴",
                "critical": "⚫"
            }
            st.markdown(f"{status_colors.get(ats_check['status'], '❓')} **{ats_check['status'].title()}**")
        
        with col3:
            st.metric("Words extracted", ats_check["metrics"]["total_words"])
        
        # Show issues and recommendations
        if ats_check["issues"]:
            st.warning("**⚠️ Issues Found:**")
            for issue in ats_check["issues"]:
                st.markdown(f"• {issue}")
        
        if ats_check["recommendations"]:
            st.info("**💡 Recommendations:**")
            for rec in ats_check["recommendations"]:
                st.markdown(f"• {rec}")
        
        # Show detailed metrics (not nested in expander)
        st.markdown("---")
        st.subheader("📊 Detailed ATS Metrics")
        metrics = ats_check["metrics"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Characters", metrics["total_chars"])
        with col2:
            st.metric("Words", metrics["total_words"])
        with col3:
            st.metric("Lines", metrics["total_lines"])
        with col4:
            st.metric("Special chars", f"{metrics['special_char_ratio']*100:.1f}%")
        
        # File format specific advice
        if resume_file and resume_file.name.lower().endswith('.pdf'):
            if ats_check["score"] < 70:
                st.error("**PDF Compatibility Issues:**")
                st.markdown("""
                Your PDF appears to have ATS compatibility issues. This commonly happens with:
                • **Design tool exports** (Figma, Canva, Photoshop)
                • **Image-based PDFs** (scanned documents)
                • **Complex layouts** with graphics and custom fonts
                
                **Solutions:**
                • Export as 'text-based PDF' from your design tool
                • Save as Word document (.docx) for better compatibility
                • Use simple formatting and standard fonts
                • Test with online ATS checkers before applying
                """)
            else:
                st.success("**PDF appears to be ATS-friendly!** ✅")
        
        # Raw Document Content (full version)
        st.markdown("---")
        st.subheader("**🔍 Raw Document Content (What ATS Actually Reads):**")
        st.text(resume_text_raw)
        st.caption("*This is the exact text that ATS systems extract from your resume*")


st.markdown("---")
st.caption("MVP limitations: no ML magic, no synonyms/lemmatization, no PDF OCR. Meant for quick feedback loops.")
