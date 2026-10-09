"""
Automated Curriculum Design Using LLMs
Streamlit Web Application (Team 32)
Department of CSE (AI&ML), Vardhaman College of Engineering
Guide: Mr. N.S.S.S. Girish Kumar
"""

import os
import json
import streamlit as st
import pandas as pd

# Import backend model engines
from models.curriculum_generator import generate_curriculum
from models.job_fetcher import fetch_jobs
from models.skill_extractor import extract_skills, build_demand_report
from models.gartner_fetcher import get_gartner_tech_trends

# Page Configuration
st.set_page_config(
    page_title="Automated Curriculum Design using LLMs",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .badge-m1 {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-m2 {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-m3 {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .skill-pill {
        display: inline-block;
        background-color: #EEF2FF;
        color: #3730A3;
        padding: 3px 8px;
        border-radius: 6px;
        margin: 2px;
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Preset AI Subject Templates
AI_SUBJECT_PRESETS = {
    "Machine Learning": {
        "title": "Introduction to Machine Learning",
        "objectives": "Understand core ML concepts, build simple predictive models, evaluate performance metrics, and deploy basic pipelines.",
        "student_notes": "Students have completed basic Python programming; no prior statistics background.",
        "search_queries": "machine learning engineer, data scientist"
    },
    "Natural Language Processing (NLP)": {
        "title": "Natural Language Processing & Text Analytics",
        "objectives": "Master text preprocessing, tokenization, embeddings, transformer architectures (BERT, GPT), sentiment analysis, and topic modeling.",
        "student_notes": "Students know fundamental Python and basic linear algebra.",
        "search_queries": "nlp engineer, natural language processing specialist"
    },
    "Computer Vision": {
        "title": "Computer Vision & Deep Learning for Image Analysis",
        "objectives": "Explore image filtering, convolutional neural networks (CNNs), object detection (YOLO), segmentation, and OpenCV in Python.",
        "student_notes": "Students have basic knowledge of Python and array operations (NumPy).",
        "search_queries": "computer vision engineer, image processing engineer"
    },
    "Generative AI & LLMs": {
        "title": "Generative AI, Prompt Engineering & RAG Architecture",
        "objectives": "Build applications using Large Language Models, prompt engineering, vector databases (Pinecone, Chroma), RAG pipelines, and agentic workflows.",
        "student_notes": "Students know Python web development basics (FastAPI/Flask) and basic API usage.",
        "search_queries": "generative ai engineer, llm engineer, ai developer"
    },
    "Deep Learning & Neural Networks": {
        "title": "Deep Learning with PyTorch & TensorFlow",
        "objectives": "Master multi-layer perceptrons, backpropagation, CNNs, RNNs, LSTMs, transformers, and model optimization techniques.",
        "student_notes": "Students have completed introductory Machine Learning.",
        "search_queries": "deep learning engineer, ai researcher"
    },
    "MLOps & AI Engineering": {
        "title": "MLOps: Machine Learning Operations & Model Deployment",
        "objectives": "Learn model version control, CI/CD for machine learning, Docker containerization, REST API serving, and MLflow tracking.",
        "student_notes": "Students know basic ML model training and Git version control.",
        "search_queries": "mlops engineer, ai platform engineer"
    },
    "AI Ethics, Governance & Security": {
        "title": "AI Ethics, Governance, Safety & Compliance",
        "objectives": "Examine algorithmic bias, model explainability (SHAP/LIME), AI privacy, regulatory frameworks, and guardrails for generative models.",
        "student_notes": "Open to all students interested in responsible AI and compliance.",
        "search_queries": "ai governance specialist, ai ethics researcher"
    },
    "Custom / User Defined": {
        "title": "",
        "objectives": "",
        "student_notes": "",
        "search_queries": "ai engineer, data scientist"
    }
}


def load_industry_skills():
    """Loads stored multi-source industry skill demand data."""
    demand_file = "industry_skill_demand.json"
    if os.path.exists(demand_file):
        with open(demand_file, "r") as f:
            return json.load(f)
    return None


def convert_curriculum_to_markdown(data):
    """Converts generated JSON curriculum into a formatted Markdown syllabus."""
    if not data:
        return ""
    md = f"# {data.get('course_title', 'Course Syllabus')}\n\n"
    md += f"**Academic Level:** {data.get('level', 'N/A')}  \n"
    md += f"**Duration:** {data.get('duration_weeks', 'N/A')} Weeks  \n\n"

    md += "## Course Outcomes\n"
    for co in data.get("course_outcomes", []):
        md += f"- {co}\n"

    md += "\n## Weekly Modules\n\n"
    for m in data.get("modules", []):
        md += f"### Week {m.get('week', '')}: {m.get('module_title', '')}\n"
        md += "**Topics Covered:**\n"
        for t in m.get("topics", []):
            md += f"- {t}\n"
        md += "\n**Learning Outcomes:**\n"
        for lo in m.get("learning_outcomes", []):
            md += f"- {lo}\n"
        if m.get("skills_covered"):
            md += f"\n**Skills Addressed:** {', '.join(m.get('skills_covered', []))}\n"
        if m.get("suggested_resources"):
            md += "\n**Suggested Resources:**\n"
            for r in m.get("suggested_resources", []):
                md += f"- {r}\n"
        md += "\n---\n\n"

    if data.get("project_ideas"):
        md += "## Capstone Project Ideas\n"
        for p in data.get("project_ideas", []):
            md += f"- {p}\n"

    align = data.get("industry_skill_alignment")
    if align:
        md += "\n## Industry Skill Alignment\n"
        md += f"**Integrated Skills:** {', '.join(align.get('skills_integrated', []))}  \n"
        md += f"**Summary:** {align.get('alignment_summary', '')}\n"

    return md


# --- MAIN APP HEADER ---
st.markdown('<div class="main-header">Automated Curriculum Design Using LLMs</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Team 32 — Vardhaman College of Engineering (Department of CSE AI&ML)</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("System Control Panel")

st.sidebar.markdown("### System Component Status")
st.sidebar.markdown('<span class="badge-m1">Learner Proficiency Profile</span>', unsafe_allow_html=True)
st.sidebar.caption("Knowledge tracing on pause — user configures target learner level directly.")

st.sidebar.markdown('<span class="badge-m2">Curriculum Synthesis Engine</span>', unsafe_allow_html=True)
st.sidebar.caption("Active — Groq synthesis engine generating structured curricula.")

st.sidebar.markdown('<span class="badge-m3">Industry Skill Intelligence</span>', unsafe_allow_html=True)
st.sidebar.caption("Active — Multi-source fusion of Adzuna job market & Gartner strategic trends.")

st.sidebar.divider()

st.sidebar.markdown("### Team Details")
st.sidebar.markdown("""
- **B. Hansika Reddy** (23881A6671)
- **P. Shravani Mudhiraj** (23881A66A3)
- **Tashifa Nooreen** (23881A66B8)
- **Guide:** Mr. N.S.S.S. Girish Kumar, Assistant Professor
""")

# Load or Initialize Industry Skill Data
if "m3_live_data" not in st.session_state:
    st.session_state["m3_live_data"] = load_industry_skills()

industry_skill_data = st.session_state["m3_live_data"]

# --- TABS LAYOUT ---
tab_generator, tab_skill_intel, tab_overview, tab_export = st.tabs([
    "Curriculum Generator",
    "Industry Skill Intelligence",
    "Overview & Architecture",
    "Export & Download",
])

# ==========================================
# TAB 1 (PRIMARY): CURRICULUM GENERATOR
# ==========================================
with tab_generator:
    st.subheader("Curriculum Generator")
    st.write("Select any AI Subject domain or enter custom course parameters to synthesize an AI-generated curriculum.")

    # AI Subject Selector
    selected_subject = st.selectbox(
        "Select AI Subject / Specialization Domain:",
        options=list(AI_SUBJECT_PRESETS.keys()),
        index=0
    )

    preset_data = AI_SUBJECT_PRESETS[selected_subject]

    with st.form("curriculum_form"):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            course_title = st.text_input("Course Title", preset_data["title"] if preset_data["title"] else "Advanced Artificial Intelligence")
            level = st.selectbox("Academic Level", [
                "Undergraduate - Beginner",
                "Undergraduate - Intermediate",
                "Postgraduate - Advanced",
                "Diploma / Professional Certification",
            ])
            duration_weeks = st.slider("Course Duration (Weeks)", 2, 12, 6)

        with col_f2:
            objectives = st.text_area(
                "Course Objectives",
                preset_data["objectives"] if preset_data["objectives"] else "Master core principles and practical implementations in AI."
            )
            student_notes = st.text_input(
                "Learner Profile / Prior Knowledge",
                preset_data["student_notes"] if preset_data["student_notes"] else "Students have completed basic programming and math prerequisites."
            )

        st.markdown("#### Integrate Industry Skill Demand")
        if industry_skill_data and industry_skill_data.get("skills_ranked"):
            top_extracted = [s["skill_name"] for s in industry_skill_data["skills_ranked"][:25]]
            selected_skills = st.multiselect(
                "Select In-Demand Industry Skills to embed in Curriculum:",
                options=top_extracted,
                default=top_extracted[:6] if len(top_extracted) >= 6 else top_extracted
            )
        else:
            selected_skills = st.text_input("Enter comma-separated skills", "Python, SQL, Scikit-Learn, MLOps, RAG Architecture")
            selected_skills = [s.strip() for s in selected_skills.split(",")]

        submit_btn = st.form_submit_button("Generate Curriculum with Groq LLM", type="primary", use_container_width=True)

    if submit_btn:
        if not os.getenv("GROQ_API_KEY"):
            st.error("GROQ_API_KEY missing from .env file. Please check API key configuration.")
        else:
            with st.spinner("Groq API is synthesizing your industry-aligned curriculum..."):
                try:
                    curriculum_output = generate_curriculum(
                        course_title=course_title,
                        level=level,
                        duration_weeks=duration_weeks,
                        objectives=objectives,
                        industry_skills=selected_skills,
                        student_proficiency_notes=student_notes,
                    )
                    if curriculum_output:
                        st.session_state["generated_curriculum"] = curriculum_output
                        st.success("Curriculum generated successfully using Groq API.")
                    else:
                        st.error("Failed to parse LLM output. Please try again.")
                except Exception as e:
                    st.error(f"Error during curriculum generation: {e}")

    # Display Generated Results
    if "generated_curriculum" in st.session_state and st.session_state["generated_curriculum"]:
        curr = st.session_state["generated_curriculum"]

        st.divider()
        st.markdown(f"### {curr.get('course_title', 'Generated Curriculum')}")
        st.caption(f"**Level:** {curr.get('level')} | **Duration:** {curr.get('duration_weeks')} Weeks")

        # Industry Alignment Callout
        align = curr.get("industry_skill_alignment")
        if align:
            st.success(f"**Industry Alignment:** {align.get('alignment_summary', '')}")
            st.markdown("**Skills Integrated:** " + "".join([f'<span class="skill-pill">{s}</span>' for s in align.get("skills_integrated", [])]), unsafe_allow_html=True)
            st.write("")

        # Course Outcomes
        st.markdown("#### Course Outcomes (COs)")
        for i, co in enumerate(curr.get("course_outcomes", []), 1):
            st.markdown(f"**CO{i}:** {co}")

        # Modules Accordion
        st.markdown("#### Weekly Modules Breakdown")
        for module in curr.get("modules", []):
            with st.expander(f"Week {module.get('week')}: {module.get('module_title')}", expanded=True):
                m_col_left, m_col_right = st.columns([2, 1])

                with m_col_left:
                    st.markdown("**Topics Covered:**")
                    for t in module.get("topics", []):
                        st.markdown(f"- {t}")

                    st.markdown("**Module Learning Outcomes:**")
                    for lo in module.get("learning_outcomes", []):
                        st.markdown(f"- {lo}")

                with m_col_right:
                    if module.get("skills_covered"):
                        st.markdown("**Skills Addressed:**")
                        for s in module.get("skills_covered", []):
                            st.markdown(f'<span class="skill-pill">{s}</span>', unsafe_allow_html=True)
                        st.write("")

                    if module.get("suggested_resources"):
                        st.markdown("**Resources:**")
                        for r in module.get("suggested_resources", []):
                            st.markdown(f"- {r}")

        # Capstone Project Ideas
        if curr.get("project_ideas"):
            st.markdown("#### Recommended Capstone Projects")
            for proj in curr.get("project_ideas", []):
                st.info(proj)

# ==========================================
# TAB 2: INDUSTRY SKILL INTELLIGENCE
# ==========================================
with tab_skill_intel:
    st.subheader("Industry Skill Intelligence (Multi-Source Fusion)")
    st.write("Real-time skill demand pipeline combining Adzuna live job market postings and Gartner Strategic Technology Trends.")

    # --- DYNAMIC LIVE EXTRACTION CONTROL PANEL ---
    with st.expander("Dynamic Live Skill Mining Control Panel", expanded=False):
        st.markdown("#### Trigger Dynamic Extraction for Any AI Subject")
        st.write("Run on-demand skill extraction across live job markets and emerging tech reports for specific AI domains.")

        with st.form("live_extraction_form"):
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                default_q = preset_data.get("search_queries", "machine learning engineer, AI engineer")
                search_keywords = st.text_input("Job Search Queries (comma-separated)", default_q)
                results_limit = st.slider("Job Postings per Query", 2, 10, 3)
            with col_ex2:
                include_adzuna = st.checkbox("Include Adzuna Live Job Postings", value=True)
                include_gartner = st.checkbox("Include Gartner Strategic Technology Trends", value=True)

            run_extraction_btn = st.form_submit_button("Run Dynamic Skill Mining", type="primary", use_container_width=True)

        if run_extraction_btn:
            if not os.getenv("GROQ_API_KEY"):
                st.error("GROQ_API_KEY missing from .env file.")
            else:
                with st.spinner("Fetching live postings & extracting skills via Groq API..."):
                    try:
                        queries = [q.strip() for q in search_keywords.split(",") if q.strip()]
                        live_jobs = []
                        if include_adzuna:
                            for q in queries:
                                try:
                                    fetched = fetch_jobs(query=q, results_per_page=results_limit)
                                    live_jobs.extend(fetched)
                                except Exception as err:
                                    st.warning(f"Could not fetch jobs for '{q}': {err}")

                        # Extract skills using Groq API
                        from collections import Counter
                        live_counter = Counter()
                        live_roles_map = {}

                        for idx, job in enumerate(live_jobs):
                            t_title = job.get("title", "Unknown")
                            t_desc = job.get("description", "")
                            e_skills = extract_skills(t_title, t_desc)
                            for s in e_skills:
                                live_counter[s] += 1
                                live_roles_map.setdefault(s, set()).add(t_title)

                        # Build fused demand report
                        new_report = build_demand_report(
                            skill_counter=live_counter,
                            skill_to_roles=live_roles_map,
                            total_jobs=len(live_jobs),
                            include_gartner=include_gartner
                        )

                        # Save and update session state
                        with open("industry_skill_demand.json", "w") as f:
                            json.dump(new_report, f, indent=2)

                        st.session_state["m3_live_data"] = new_report
                        industry_skill_data = new_report
                        st.success(f"Dynamic extraction complete! Analyzed {len(live_jobs)} jobs and fused Gartner strategic trends.")
                    except Exception as ex:
                        st.error(f"Dynamic skill extraction failed: {ex}")

    st.divider()

    # --- DISPLAY MULTI-SOURCE METRICS ---
    if not industry_skill_data:
        st.warning("No industry skill demand data found. Please use the control panel above to run live skill mining.")
    else:
        skills_list = industry_skill_data.get("skills_ranked", [])
        total_jobs = industry_skill_data.get("total_jobs_analyzed", 0)
        gartner_count = industry_skill_data.get("gartner_trends_integrated", len(get_gartner_tech_trends()))

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Data Pipeline", "Adzuna + Gartner")
        m_col2.metric("Jobs Analyzed", total_jobs)
        m_col3.metric("Gartner Trends Fused", gartner_count)
        if skills_list:
            m_col4.metric("Top In-Demand Skill", skills_list[0]["skill_name"], f"Score: {skills_list[0]['demand_score']}")

        st.divider()

        # Skill Demand Bar Chart
        if skills_list:
            df_skills = pd.DataFrame(skills_list)

            st.markdown("### Fused Skill Demand Ranking (Adzuna Frequency + Gartner Strategic Weight)")
            top_n = st.slider("Select number of top skills to display", 5, len(df_skills), 15)

            df_top = df_skills.head(top_n)

            st.bar_chart(
                data=df_top,
                x="skill_name",
                y="demand_score",
                color="#1E40AF",
                use_container_width=True,
            )

            # Detailed Skill Table
            st.markdown("### Multi-Source Skill Taxonomy Table")
            search_query = st.text_input("Search for a skill (e.g., Agentic AI, RAG, Python, MLOps, Computer Vision)", "")

            if search_query:
                df_filtered = df_skills[df_skills["skill_name"].str.contains(search_query, case=False, na=False)]
            else:
                df_filtered = df_skills

            st.dataframe(
                df_filtered[["skill_name", "demand_score", "source", "category", "frequency", "seen_in_roles"]],
                column_config={
                    "skill_name": "Skill Name",
                    "demand_score": st.column_config.ProgressColumn("Fused Demand Score (0-1)", min_value=0, max_value=1),
                    "source": "Data Source",
                    "category": "Skill Category / Impact",
                    "frequency": "Job Posting Frequency",
                    "seen_in_roles": "Associated Job Roles",
                },
                use_container_width=True,
            )

# ==========================================
# TAB 3: OVERVIEW & ARCHITECTURE
# ==========================================
with tab_overview:
    st.subheader("Project Problem Statement & Architecture")
    st.write("""
    Designing an effective curriculum is a complex and time-consuming manual process. As technology rapidly evolves,
    academic syllabi often fall behind industry needs. This system leverages **Groq LLM Acceleration** and
    **multi-source market skill mining (Adzuna + Gartner Reports)** to automatically generate structured, customizable, and job-aligned curricula across any AI subject area.
    """)

    st.markdown("### Core Component Architecture")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h4>Learner Proficiency Module</h4>
            <b>Student Skill Estimation</b>
            <p>Estimates student skill mastery scores using quiz performance metrics. <i>(Configured via learner profile inputs in Streamlit UI).</i></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h4>Curriculum Synthesis Engine</h4>
            <b>LLM Syllabus Generator</b>
            <p>Uses Groq (GPT-OSS-120B / Llama architecture) to generate structured weekly modules, outcomes, resources, and capstone projects in clean JSON.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h4>Industry Skill Intelligence</h4>
            <b>Job Market & Gartner Mining</b>
            <p>Fetches real-time job postings via Adzuna API and strategic trends from Gartner reports, extracting/ranking skills using Groq (Llama 3.3 70B).</p>
        </div>
        """, unsafe_allow_html=True)

    st.info("Current Progress: The Curriculum Synthesis Engine and Multi-Source Industry Skill Intelligence Module are fully integrated via Groq API. You can generate skill-aligned curricula across any AI Subject in Tab 1 and run dynamic skill mining in Tab 2.")

# ==========================================
# TAB 4: EXPORT & DOWNLOAD
# ==========================================
with tab_export:
    st.subheader("Export & Download Curriculum")

    if "generated_curriculum" not in st.session_state or not st.session_state["generated_curriculum"]:
        st.info("No curriculum generated yet. Please use Tab 1 ('Curriculum Generator') to generate a curriculum first.")
    else:
        curr_data = st.session_state["generated_curriculum"]

        col_d1, col_d2 = st.columns(2)

        json_str = json.dumps(curr_data, indent=2)
        md_str = convert_curriculum_to_markdown(curr_data)

        with col_d1:
            st.markdown("### Download as JSON")
            st.download_button(
                label="Download JSON File",
                data=json_str,
                file_name=f"{curr_data.get('course_title', 'curriculum').lower().replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True,
            )
            st.json(curr_data, expanded=False)

        with col_d2:
            st.markdown("### Download as Markdown Syllabus")
            st.download_button(
                label="Download Markdown (.md) File",
                data=md_str,
                file_name=f"{curr_data.get('course_title', 'curriculum').lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.markdown("```markdown\n" + md_str[:1500] + "\n...\n```")
