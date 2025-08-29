
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

# Page configuration
st.set_page_config(
    page_title="ATS Resume Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for fixed sidebar and modern styling
st.markdown("""
<style>
    /* Main container layout */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Left sidebar styling - fixed height, non-scrollable */
    .left-panel {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 2rem;
        height: 100vh;
        overflow: hidden;
        position: sticky;
        top: 0;
    }
    
    /* Right panel styling - scrollable */
    .right-panel {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        height: 100vh;
        overflow-y: auto;
    }
    
    /* File upload styling */
    .upload-area {
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: white;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button[data-baseweb="button"] {
        background-color: #000;
        color: white;
    }
    
    .stButton > button[data-baseweb="button"]:hover {
        background-color: #333;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #28a745;
    }
    
    /* Keyword chips styling */
    .keyword-chip {
        display: inline-block;
        background: #e9ecef;
        color: #495057;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .keyword-chip.present {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .keyword-chip.missing {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Score display styling */
    .score-display {
        text-align: center;
        margin: 2rem 0;
    }
    
    .score-number {
        font-size: 3rem;
        font-weight: 700;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    
    .score-label {
        font-size: 1.25rem;
        color: #6c757d;
        margin-bottom: 1rem;
    }
    
    /* Metrics grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #495057;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    /* Hide scrollbars but keep functionality */
    .right-panel::-webkit-scrollbar {
        width: 6px;
    }
    
    .right-panel::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .right-panel::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    .right-panel::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("📄 ATS Resume Checker")
st.markdown("Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.")

# Create two columns with specific widths
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    
    # Upload Resume Section
    st.subheader("📁 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'doc', 'docx'],
        help="Upload your resume (PDF, DOC, or DOCX)"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
    
    # Job Description Section
    st.subheader("📝 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="Copy and paste the complete job description here..."
    )
    
    # Action Buttons
    col_button1, col_button2 = st.columns(2)
    
    with col_button1:
        if st.button("🔄 Start Over", use_container_width=True):
            st.rerun()
    
    with col_button2:
        analyze_button = st.button("🚀 Get My Score", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Right Panel - Results
with col2:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    
    if analyze_button and uploaded_file is not None and job_description:
        # Process the files
        resume_text = extract_text_from_file(uploaded_file)
        resume_text_clean = clean_text(resume_text)
        jd_text_clean = clean_text(job_description)
        
        if not resume_text_clean or not jd_text_clean:
            st.error("❌ Could not extract text from the uploaded file. Please try a different file format.")
        else:
            # Extract keywords and compute scores
            kw = extract_keywords_with_scores(jd_text_clean, top_n=30)
            sim = compute_similarity(jd_text_clean, resume_text_clean)
            present, missing, _ = suggest_missing_keywords(jd_text_clean, resume_text_clean)
            
            # Calculate coverage
            coverage = round(100.0 * len(present) / max(1, len(present) + len(missing)))
            
            # Final score calculation
            final_score = round(0.7 * coverage + 0.3 * (sim * 100))
            final_score = max(0, min(100, final_score))
            
            # Display ATS Match Score
            st.markdown('<div class="score-display">', unsafe_allow_html=True)
            st.markdown(f'<div class="score-number">{final_score}/100</div>', unsafe_allow_html=True)
            st.markdown('<div class="score-label">Your ATS Match Score</div>', unsafe_allow_html=True)
            st.progress(final_score / 100)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Key Metrics
            st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
            
    with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Text Similarity", f"{round(sim * 100)}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Keyword Coverage", f"{coverage}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Keyword Coverage Details
            st.subheader("🎯 Keyword Coverage")
            st.metric("Keywords Found", f"{len(present)}/{len(present) + len(missing)}", f"{coverage}%")
            st.progress(coverage / 100)
            
            # All JD Keywords
            st.subheader("📋 All JD Keywords (Top 30)")
            keywords_text = ", ".join([word for word, _ in kw])
            st.markdown(f'<div class="keyword-chip">{keywords_text}</div>', unsafe_allow_html=True)
            
            # Present vs Missing Keywords
            col_present, col_missing = st.columns(2)
            
            with col_present:
                st.subheader("✅ Present in your resume")
                for word in present:
                    st.markdown(f'<span class="keyword-chip present">{word}</span>', unsafe_allow_html=True)
                st.info(f"Great job! You're covering {len(present)} out of {len(present) + len(missing)} top JD keywords")
            
            with col_missing:
                st.subheader("❌ Missing / low-visibility keywords")
                # Show only top relevant missing keywords
                relevant_missing = select_most_relevant_keywords(
                    [(word, 0) for word in missing], jd_text_clean, top_k=8
                )
                for word in relevant_missing:
                    st.markdown(f'<span class="keyword-chip missing">{word}</span>', unsafe_allow_html=True)
                st.warning(f"Showing top {len(relevant_missing)} most relevant missing keywords. Add these to improve your coverage.")
            
            # Bullet Suggestions
            st.subheader("💡 Bullet Suggestions (add these to your resume)")
            smart_bullets = smart_bullets_for_missing(relevant_missing[:5])
            for bullet in smart_bullets:
                st.markdown(f"• {bullet}")
            
            st.info("💡 **Tip:** Customize these bullets with your specific metrics and achievements.")
            
            # Score Explanation
            with st.expander("📊 How is my score calculated?", expanded=False):
                explanation = get_keyword_coverage_explanation(len(present), len(present) + len(missing), sim)
                st.markdown(explanation)
            
            # Advanced Analysis
            with st.expander("🔍 Advanced Analysis", expanded=False):
                # ATS Readability Check
                ats_check = check_ats_readability(resume_text)
                st.subheader("🔍 ATS Readability Check")
                
                if ats_check["score"] >= 80:
                    st.success(f"✅ ATS Compatible - Score: {ats_check['score']}/100")
                elif ats_check["score"] >= 60:
                    st.warning(f"🟡 Good - Score: {ats_check['score']}/100")
                else:
                    st.error(f"❌ Needs Improvement - Score: {ats_check['score']}/100")
                
                st.metric("Words extracted", ats_check["word_count"])
                
                if ats_check["issues"]:
                    st.warning("⚠️ Issues Found:")
                    for issue in ats_check["issues"]:
                        st.markdown(f"• {issue}")
                
                # Raw Document Content
                st.subheader("📄 Raw Document Content (What ATS Actually Reads)")
                st.text_area("Full extracted text", resume_text_clean, height=300, disabled=True)
    
    elif analyze_button:
        if not uploaded_file:
            st.error("❌ Please upload a resume file first.")
        if not job_description:
            st.error("❌ Please paste a job description first.")
    
    st.markdown('</div>', unsafe_allow_html=True)
