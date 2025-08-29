
import os
import streamlit as st
from utils import (
    detect_sections,
    extract_text_from_file,
    clean_text,
    top_keywords,
    suggest_missing_keywords,
    compute_similarity,
)
import io
from datetime import datetime

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

        # Section detection (resume hygiene tips)
        sections_found = detect_sections(resume_text_raw)

        # Extract top JD keywords
        kw = top_keywords(jd_text_clean, top_n=30)
        # Compute scores
        sim = compute_similarity(jd_text_clean, resume_text)  # 0..1
        present, missing, _ = suggest_missing_keywords(jd_text_clean, resume_text, top_n=12)
        
        # Calculate coverage as decimal (0.0-1.0) for consistent calculations
        coverage_decimal = len(present) / max(1, len(present) + len(missing))
        coverage_percent = round(coverage_decimal * 100, 1)
        
        # Final score: weighted combination of keyword coverage and cosine similarity
        # Keyword coverage is more important (70%) since it directly measures JD keyword matches
        # Cosine similarity provides additional context but shouldn't dominate
        keyword_score = coverage_decimal * 100  # 0-100
        similarity_score = sim * 100  # 0-100
        
        final_score = int(round(keyword_score * 0.7 + similarity_score * 0.3))
        
        # Ensure final_score is within valid range for progress bar
        final_score = max(0, min(100, final_score))

    st.subheader("Your ATS Match Score")
    st.progress(final_score/100.0, text=f"{final_score}/100")
    st.metric("Overall score", f"{final_score}/100", help="70% keyword coverage + 30% cosine similarity")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Keyword coverage", f"{coverage_percent}%")
    with col2:
        st.metric("Cosine similarity", f"{int(round(sim*100))}%")

    st.markdown("---")
    st.subheader("JD Keywords (Top 30)")
    if kw:
        st.write(", ".join(kw))
    else:
        st.write("No keywords extracted (JD might be too short).")

    st.markdown("### ✅ Present in your resume:")
    if present:
        st.write(", ".join(present))
    else:
        st.write("_None detected from top JD keywords._")

    st.markdown("### ❌ Missing / low-visibility keywords to add:")
    if missing:
        st.write(", ".join(missing))
        st.markdown("#### Suggested bullet ideas:")
        bullets = []
        
        # Role-specific bullet point templates
        role_templates = {
            # Product Design specific
            "design": [
                "• Led **design system** development and implementation across multiple products",
                "• Created high-fidelity **design** prototypes and user flows for complex features",
                "• Established **design** quality standards and best practices for the team"
            ],
            "ux": [
                "• Conducted user research to inform **UX** decisions and product strategy",
                "• Designed intuitive **UX** flows that improved user engagement by X%",
                "• Collaborated with product managers to define **UX** requirements and success metrics"
            ],
            "ui": [
                "• Designed pixel-perfect **UI** components that maintained brand consistency",
                "• Created responsive **UI** designs for web and mobile platforms",
                "• Developed **UI** guidelines that improved design team efficiency by X%"
            ],
            "prototype": [
                "• Built interactive **prototypes** to test user flows and gather stakeholder feedback",
                "• Created high-fidelity **prototypes** that accelerated development handoff",
                "• Used **prototyping** tools to iterate quickly on design solutions"
            ],
            "visual": [
                "• Established **visual** design standards that improved brand consistency",
                "• Created **visual** assets and design systems for multiple product lines",
                "• Led **visual** design reviews and provided constructive feedback to team members"
            ],
            "interaction": [
                "• Designed micro-**interactions** that enhanced user experience and engagement",
                "• Created **interaction** patterns that improved usability across products",
                "• Defined **interaction** guidelines for consistent user experience"
            ],
            "system": [
                "• Built and maintained **design system** components used across multiple products",
                "• Established **system** guidelines that improved design consistency by X%",
                "• Collaborated with engineering to implement **design system** components"
            ],
            "flow": [
                "• Designed user **flows** that simplified complex user journeys",
                "• Created **flow** diagrams that helped stakeholders understand user experience",
                "• Optimized user **flows** based on user research and analytics data"
            ],
            "product": [
                "• Contributed to **product** strategy and roadmap planning",
                "• Collaborated with **product** managers to define feature requirements",
                "• Led **product** design initiatives that improved user satisfaction"
            ],
            "quality": [
                "• Established **quality** standards for design deliverables",
                "• Implemented **quality** assurance processes for design handoffs",
                "• Led **quality** reviews that improved design team output"
            ]
        }
        
        # Generate role-specific bullets for each missing keyword
        for m in missing:
            if m.lower() in role_templates:
                # Use role-specific template
                bullets.extend(role_templates[m.lower()])
            else:
                # Fallback to generic but better template
                bullets.append(f"• Applied **{m}** principles to improve design outcomes and user experience")
                bullets.append(f"• Integrated **{m}** considerations into design decision-making process")
        
        # deduplicate and cap
        seen = set()
        filtered = []
        for b in bullets:
            if b not in seen:
                filtered.append(b)
                seen.add(b)
            if len(filtered) >= 10:  # Increased cap for better variety
                break
        st.write("\n".join(filtered))
    else:
        st.write("Great! You cover the key JD terms.")
        filtered = []  # Initialize filtered for the report

    st.markdown("---")
    st.subheader("Resume hygiene (sections found)")
    if sections_found:
        st.write(", ".join(sorted(sections_found)))
        # Quick recommendations
        expected = {"experience","work experience","skills","education","projects","about","summary","portfolio","links"}
        missing_sections = [s for s in ["Experience","Skills","Education","Projects","Summary"] 
                            if s.lower() not in sections_found]
        if missing_sections:
            st.info("Consider adding or clarifying: " + ", ".join(missing_sections))
    else:
        st.write("_Could not detect standard sections (make sure headings are clear)._")

    # Downloadable report
    st.markdown("---")
    st.subheader("Download report")
    report_md = f"""# ATS Checker Report

**Date:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

## Overall
- Score: **{final_score}/100**
- Keyword coverage: **{coverage_percent}%**
- Cosine similarity: **{int(round(sim*100))}%**

## JD Top Keywords
{", ".join(kw) if kw else "-"}

## Present in Resume
{", ".join(present) if present else "-"}

## Missing / Low-Visibility
{", ".join(missing) if missing else "-"}

### Suggested bullet ideas
{os.linesep.join(filtered) if missing else "You already cover the key terms."}  # pyright: ignore[reportUndefinedVariable]

## Sections Detected
{", ".join(sorted(sections_found)) if sections_found else "-"}
"""
    b = io.BytesIO(report_md.encode("utf-8"))
    st.download_button("⬇️ Download Markdown report", data=b, file_name="ats_report.md", mime="text/markdown")
    
st.markdown("---")
st.caption("MVP limitations: no ML magic, no synonyms/lemmatization, no PDF OCR. Meant for quick feedback loops.")
