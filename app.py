
import streamlit as st
from utils import extract_text_from_file, clean_text, top_keywords, compute_similarity, suggest_missing_keywords, detect_sections
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

        # Section detection (for quick hygiene tips)
        sections_found = detect_sections(resume_text_raw)

        # Extract top JD keywords
        kw = top_keywords(jd_text_clean, top_n=30)
        # Compute scores
        sim = compute_similarity(jd_text_clean, resume_text)  # 0..1
        present, missing, coverage = suggest_missing_keywords(kw, resume_text, top_k_show=12)

        # Final score
        final_score = int(round((coverage * 0.7 + sim * 0.3) * 100))

    st.subheader("Your ATS Match Score")
    st.progress(final_score/100.0, text=f"{final_score}/100")
    st.metric("Overall score", f"{final_score}/100", help="70% keyword coverage + 30% cosine similarity")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Keyword coverage", f"{int(round(coverage*100))}%")
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
        for m in missing:
            bullets.append(f"• Implemented **{m}** in a real project; measured impact with clear metrics.")
            bullets.append(f"• Collaborated with cross‑functional team to drive **{m}** adoption.")
            bullets.append(f"• Used **{m}** to improve outcomes (e.g., conversion, retention, speed).")
        # deduplicate and cap
        seen = set()
        filtered = []
        for b in bullets:
            if b not in seen:
                filtered.append(b)
                seen.add(b)
            if len(filtered) >= 8:
                break
        st.write("\n".join(filtered))
    else:
        st.write("Great! You cover the key JD terms.")

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
- Keyword coverage: **{int(round(coverage*100))}%**
- Cosine similarity: **{int(round(sim*100))}%**

## JD Top Keywords
{", ".join(kw) if kw else "-"}

## Present in Resume
{", ".join(present) if present else "-"}

## Missing / Low-Visibility
{", ".join(missing) if missing else "-"}

### Suggested bullet ideas
{os.linesep.join(filtered) if missing else "You already cover the key terms."}

## Sections Detected
{", ".join(sorted(sections_found)) if sections_found else "-"}
"""
    b = io.BytesIO(report_md.encode("utf-8"))
    st.download_button("⬇️ Download Markdown report", data=b, file_name="ats_report.md", mime="text/markdown")
    
st.markdown("---")
st.caption("MVP limitations: no ML magic, no synonyms/lemmatization, no PDF OCR. Meant for quick feedback loops.")
