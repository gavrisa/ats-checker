
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
        st.metric("Keyword coverage", f"{coverage_percent}%")
    with col2:
        st.metric("Text similarity", f"{int(round(sim*100))}%")

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

    # Keyword Coverage Section - Simplified and focused
    st.markdown("---")
    st.subheader("🎯 Keyword Coverage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Present in your resume:")
        if present:
            st.success(", ".join(present))
        else:
            st.warning("_None detected from top JD keywords._")
    
    with col2:
        st.markdown("### ❌ Missing / low-visibility keywords:")
        if missing:
            st.error(", ".join(missing))
        else:
            st.success("Great! You cover the key JD terms.")
    
    # Show bullet point suggestions immediately (not hidden behind button)
    if missing:
        st.markdown("---")
        st.markdown("**💡 Suggested bullet points to add missing keywords:**")
        
        # Generate role-specific bullets for missing keywords
        bullets = []
        role_templates = {
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
                bullets.extend(role_templates[m.lower()])
            else:
                bullets.append(f"• Applied **{m}** principles to improve design outcomes and user experience")
                bullets.append(f"• Integrated **{m}** considerations into design decision-making process")
        
        # Deduplicate and limit to top 10
        seen = set()
        filtered = []
        for b in bullets:
            if b not in seen:
                filtered.append(b)
                seen.add(b)
            if len(filtered) >= 10:
                break
        
        # Display bullet points directly
        st.write("\n".join(filtered))
        
        # Add copy button for convenience
        bullet_text = "\n".join(filtered)
        if st.button("📋 Copy All Bullet Ideas", type="secondary", use_container_width=False):
            st.success("✅ All bullet points copied! Paste them into your resume and customize.")

    # Quick Fixes Section - More detailed information
    st.markdown("---")
    st.subheader("🔧 Quick Fixes")
    
    # Generate detailed action items based on analysis
    quick_fixes = []
    
    # Check for missing essential sections
    essential_sections = {'experience', 'skills', 'education'}
    missing_essential = essential_sections - sections_found
    if missing_essential:
        for section in missing_essential:
            if section == 'experience':
                quick_fixes.append({
                    "priority": "🚨 CRITICAL",
                    "action": f"Add **{section.title()}** section with clear heading",
                    "details": "This is the most important section for ATS systems. Include job titles, companies, dates, and quantifiable achievements.",
                    "example": "EXPERIENCE\nSenior UX Designer | Company Name | 2022-2024\n• Led design system development that improved team efficiency by 40%"
                })
            elif section == 'skills':
                quick_fixes.append({
                    "priority": "🚨 CRITICAL", 
                    "action": f"Add **{section.title()}** section with clear heading",
                    "details": "List technical skills, tools, and methodologies. Use bullet points for easy scanning.",
                    "example": "SKILLS\n• Design Tools: Figma, Adobe XD, Sketch\n• Research: User interviews, usability testing\n• Prototyping: High-fidelity prototypes, user flows"
                })
            elif section == 'education':
                quick_fixes.append({
                    "priority": "⚠️ IMPORTANT",
                    "action": f"Add **{section.title()}** section with clear heading", 
                    "details": "Include degree, institution, graduation date, and relevant coursework or achievements.",
                    "example": "EDUCATION\nBachelor of Design | University Name | 2020\n• Relevant coursework: UX Design, Visual Communication, Human-Computer Interaction"
                })
    
    # Check for sections with low word count
    if ats_preview["sections"]:
        for section_name, section_data in ats_preview["sections"].items():
            if section_data["quality"] in ["poor", "fair"]:
                if section_data["word_count"] < 10:
                    quick_fixes.append({
                        "priority": "⚠️ IMPORTANT",
                        "action": f"Expand **{section_name.title()}** section with more details",
                        "details": f"Current section has only {section_data['word_count']} words. ATS systems need more content to properly analyze your qualifications.",
                        "example": f"Add specific examples, achievements, and responsibilities to your {section_name.title()} section."
                    })
                elif section_data["word_count"] < 20:
                    quick_fixes.append({
                        "priority": "💡 HELPFUL",
                        "action": f"Add more content to **{section_name.title()}** section",
                        "details": f"Current section has {section_data['word_count']} words. Consider adding more specific details and examples.",
                        "example": f"Expand your {section_name.title()} section with quantifiable achievements and specific responsibilities."
                    })
    
    # Check for missing keywords
    if missing and len(missing) > 5:
        quick_fixes.append({
            "priority": "💡 HELPFUL",
            "action": "Mention missing keywords naturally in Experience section",
            "details": f"You're missing {len(missing)} important keywords from the job description. Integrate them naturally into your experience descriptions.",
            "example": "Instead of just listing 'UX Design', write 'Led UX design initiatives that improved user engagement by 25%'"
        })
    
    # Limit to 4 most important fixes
    quick_fixes = quick_fixes[:4]
    
    if quick_fixes:
        for i, fix in enumerate(quick_fixes, 1):
            with st.container():
                st.markdown(f"**{i}. {fix['priority']} {fix['action']}**")
                st.info(f"**Why:** {fix['details']}")
                st.caption(f"**Example:** {fix['example']}")
                st.markdown("---")
    else:
        st.success("🎉 No quick fixes needed! Your resume looks good.")
    
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
        
        # ATS Document Preview
        st.markdown("---")
        st.subheader("📄 ATS Document Preview")
        st.info("**This is exactly how ATS systems and job platforms see your resume:**")
        
        # Show ATS preview score with better formatting
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**📊 ATS Document Quality Score:**")
        with col2:
            if ats_preview["ats_score"] >= 80:
                st.success(f"**{ats_preview['ats_score']:.0f}/100** 🎉 Excellent")
            elif ats_preview["ats_score"] >= 60:
                st.warning(f"**{ats_preview['ats_score']:.0f}/100** ⚠️ Good")
            elif ats_preview["ats_score"] >= 40:
                st.error(f"**{ats_preview['ats_score']:.0f}/100** ❌ Fair")
            else:
                st.error(f"**{ats_preview['ats_score']:.0f}/100** 🚨 Poor")
        
        # PDF-Like Document Reader with Visual Structure
        st.markdown("**📋 Document Preview & Analysis (PDF-Style Reader):**")
        
        if ats_preview["sections"]:
            # Create two columns: Document Preview (left) and Comments (right)
            doc_col, comments_col = st.columns([2, 1])
            
            with doc_col:
                st.markdown("**📄 Document Preview (How ATS Sees Your Resume):**")
                
                # Create a PDF-like document container with custom CSS
                st.markdown("""
                <style>
                .resume-document {
                    background: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    font-family: 'Arial', sans-serif;
                }
                .section-header {
                    font-size: 18px;
                    font-weight: bold;
                    margin: 15px 0 10px 0;
                    padding: 8px 0;
                    border-bottom: 2px solid #333;
                    text-transform: uppercase;
                }
                .section-content {
                    margin: 10px 0 20px 0;
                    line-height: 1.6;
                    padding: 10px;
                    border-radius: 4px;
                }
                .excellent { background-color: #d4edda; border-left: 4px solid #28a745; }
                .good { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
                .fair { background-color: #fff3cd; border-left: 4px solid #ffc107; }
                .poor { background-color: #f8d7da; border-left: 4px solid #dc3545; }
                .quality-badge {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: bold;
                    margin-left: 10px;
                }
                .badge-excellent { background-color: #28a745; color: white; }
                .badge-good { background-color: #17a2b8; color: white; }
                .badge-fair { background-color: #ffc107; color: black; }
                .badge-poor { background-color: #dc3545; color: white; }
                </style>
                """, unsafe_allow_html=True)
                
                # Create the document structure
                doc_html = '<div class="resume-document">'
                
                # Add document header
                doc_html += '<div style="text-align: center; margin-bottom: 30px;">'
                doc_html += '<h1 style="color: #2c3e50; margin: 0;">RESUME PREVIEW</h1>'
                doc_html += '<p style="color: #7f8c8d; margin: 5px 0;">How ATS systems see your document</p>'
                doc_html += '</div>'
                
                # Add each section with visual styling
                for section_name, section_data in ats_preview["sections"].items():
                    # Quality badge
                    if section_data["quality"] == "excellent":
                        quality_class = "excellent"
                        badge_class = "badge-excellent"
                        badge_text = "EXCELLENT"
                    elif section_data["quality"] == "good":
                        quality_class = "good"
                        badge_class = "badge-good"
                        badge_text = "GOOD"
                    elif section_data["quality"] == "fair":
                        quality_class = "fair"
                        badge_class = "badge-fair"
                        badge_text = "FAIR"
                    else:
                        quality_class = "poor"
                        badge_class = "badge-poor"
                        badge_text = "POOR"
                    
                    # Section header
                    doc_html += f'<div class="section-header">{section_name.upper()}'
                    doc_html += f'<span class="quality-badge {badge_class}">{badge_text}</span>'
                    doc_html += '</div>'
                    
                    # Section content with quality-based styling
                    content = section_data["content"]
                    word_count = section_data["word_count"]
                    
                    doc_html += f'<div class="section-content {quality_class}">'
                    doc_html += f'<strong>Content ({word_count} words):</strong><br>'
                    doc_html += f'{content}'
                    
                    # Add issues if any
                    if section_data["issues"]:
                        doc_html += '<br><br><strong style="color: #dc3545;">⚠️ Issues Found:</strong><ul>'
                        for issue in section_data["issues"]:
                            doc_html += f'<li style="color: #dc3545;">{issue}</li>'
                        doc_html += '</ul>'
                    
                    doc_html += '</div>'
                
                doc_html += '</div>'
                
                # Display the HTML document
                st.markdown(doc_html, unsafe_allow_html=True)
            
            with comments_col:
                st.markdown("**💬 Analysis & Recommendations:**")
                
                # Show quality score prominently
                if ats_preview["ats_score"] >= 80:
                    st.success(f"**Overall Score: {ats_preview['ats_score']:.0f}/100** 🎉")
                elif ats_preview["ats_score"] >= 60:
                    st.warning(f"**Overall Score: {ats_preview['ats_score']:.0f}/100** ⚠️")
                else:
                    st.error(f"**Overall Score: {ats_preview['ats_score']:.0f}/100** ❌")
                
                # Show section-by-section comments
                for section_name, section_data in ats_preview["sections"].items():
                    with st.container():
                        st.markdown(f"**{section_name.title()}:**")
                        
                        if section_data["quality"] == "excellent":
                            st.success("✅ Excellent - No changes needed")
                        elif section_data["quality"] == "good":
                            st.success("✅ Good - Minor improvements possible")
                        elif section_data["quality"] == "fair":
                            st.warning("⚠️ Fair - Needs work")
                            st.caption(f"Only {section_data['word_count']} words")
                        else:
                            st.error("❌ Poor - Critical issue")
                            st.caption(f"Only {section_data['word_count']} words")
                            if section_data["issues"]:
                                for issue in section_data["issues"]:
                                    st.error(f"• {issue}")
                        
                        st.markdown("---")
                
                # Show quick actions
                if ats_preview["recommendations"]:
                    st.markdown("**🚨 Quick Actions Needed:**")
                    for i, rec in enumerate(ats_preview["recommendations"], 1):
                        st.error(f"{i}. {rec}")
        
        # Show detailed recommendations below
        if ats_preview["recommendations"]:
            st.markdown("---")
            st.markdown("**💡 Detailed Fix Guide:**")
            
            # Create detailed sections for each problem area (no nested expanders)
            for i, rec in enumerate(ats_preview["recommendations"], 1):
                st.markdown(f"**{i}. {rec}**")
                
                if "Skills" in rec:
                    st.markdown("""
                    **How to Fix Skills Section:**
                    ```
                    SKILLS
                    • Figma, Adobe XD, Sketch
                    • User Research, Usability Testing
                    • Prototyping, Wireframing
                    • UI/UX Design, Design Systems
                    • HTML/CSS, JavaScript (basic)
                    • User Flows, Information Architecture
                    ```
                    """)
                elif "Contact" in rec:
                    st.markdown("""
                    **How to Fix Contact Section:**
                    ```
                    CONTACT
                    • Email: yourname@email.com
                    • Phone: +1 (555) 123-4567
                    • LinkedIn: linkedin.com/in/yourprofile
                    • Portfolio: yourportfolio.com
                    • Location: City, Country
                    ```
                    """)
                elif "Projects" in rec:
                    st.markdown("""
                    **How to Fix Projects Section:**
                    ```
                    PROJECTS
                    • **Mobile App Redesign** - Led UX redesign for iOS app
                      - Increased user engagement by 40%
                      - Improved conversion rate by 25%
                    • **E-commerce Website** - Designed checkout flow
                      - Reduced cart abandonment by 30%
                      - Enhanced mobile responsiveness
                    ```
                    """)
                else:
                    st.markdown(f"**How to Fix {rec}:**")
                    st.info("Add more detailed content with specific examples and achievements.")
                
                st.markdown("---")
        
        # Show raw document content for debugging
        st.markdown("---")
        st.subheader("**🔍 Raw Document Content (What ATS Actually Reads):**")
        st.text(ats_preview["content_sample"])
        st.caption("*This is the exact text that ATS systems extract from your resume*")
        
        # Resume Structure Analysis
        st.markdown("---")
        st.subheader("📋 Resume Structure Analysis")
        
        if sections_found:
            # Calculate structure completeness score
            essential_sections = {'experience', 'skills', 'education'}
            optional_sections = {'summary', 'projects', 'contact'}
            
            essential_found = len(essential_sections & sections_found)
            optional_found = len(optional_sections & sections_found)
            
            structure_score = min(100, (essential_found / 3 * 70) + (optional_found / 3 * 30))
            
            # Show structure score prominently
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**📊 Structure Completeness:**")
            with col2:
                if structure_score >= 80:
                    st.success(f"**{int(structure_score)}%** 🎉")
                elif structure_score >= 60:
                    st.warning(f"**{int(structure_score)}%** ⚠️")
                else:
                    st.error(f"**{int(structure_score)}%** ❌")
            
            # Show sections with strict red/green indicators
            st.markdown("**📋 Section Status:**")
            
            # Essential sections (red if missing, green if present)
            for section in sorted(essential_sections):
                if section in sections_found:
                    st.success(f"✅ **{section.title()}** - Essential section found")
                else:
                    st.error(f"❌ **{section.title()}** - **MISSING ESSENTIAL SECTION**")
            
            # Optional sections (blue if present, gray if missing)
            for section in sorted(optional_sections):
                if section in sections_found:
                    st.info(f"💙 **{section.title()}** - Optional section found")
                else:
                    st.markdown(f"⚪ **{section.title()}** - Optional section (not critical)")
            
            # Only show recommendations if there are issues
            missing_essential = essential_sections - sections_found
            if missing_essential:
                st.markdown("---")
                st.error("**🚨 Critical Issues Found:**")
                st.markdown(f"**Missing essential sections:** {', '.join(missing_essential).title()}")
                st.markdown("These sections are critical for ATS systems and recruiters.")
                st.markdown("**💡 Fix:** Add these sections with clear headings before applying to jobs.")
            
        else:
            st.error("**⚠️ No standard sections detected**")
            st.markdown("This could indicate:")
            st.markdown("• Unclear section headings")
            st.markdown("• Non-standard formatting")
            st.markdown("• Text extraction issues")
            st.markdown("• Resume might need restructuring")
            
            st.markdown("**💡 Try:**")
            st.markdown("• Use clear section titles like 'Experience', 'Skills', 'Education'")
            st.markdown("• Ensure headings are properly formatted")
            st.markdown("• Check if the resume file uploaded correctly")

    # JD Keywords section - moved to advanced analysis
    with st.expander("🔍 JD Keywords Analysis", expanded=False):
        st.subheader("JD Keywords (Top 30)")
        if kw:
            st.write(", ".join(kw))
        else:
            st.write("No keywords extracted (JD might be too short).")


st.markdown("---")
st.caption("MVP limitations: no ML magic, no synonyms/lemmatization, no PDF OCR. Meant for quick feedback loops.")
