"""
Automated Curriculum Design Using LLMs
Model 2 (M2) - LLM Curriculum Synthesis Engine (Groq Version)

Uses Groq API (GPT-OSS-120B / 20B) to generate structured curricula
in clean JSON format, integrating M3 industry skill demand and manual M1 student proficiency.
"""

import os
import json
import time
# pyrefly: ignore [missing-import]
from groq import Groq
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Add it to your .env file.")

client = Groq(api_key=API_KEY)


def build_prompt(course_title, level, duration_weeks, objectives, industry_skills=None, student_proficiency_notes=None):
    """Builds a structured prompt instructing the LLM to return clean JSON with industry skill alignment."""
    skills_context = ""
    if industry_skills:
        if isinstance(industry_skills, list):
            skills_str = ", ".join([s if isinstance(s, str) else s.get("skill_name", "") for s in industry_skills])
        else:
            skills_str = str(industry_skills)
        skills_context = f"\nTarget Industry In-Demand Skills to Integrate: {skills_str}"

    proficiency_context = ""
    if student_proficiency_notes:
        proficiency_context = f"\nTarget Learner Background / Prior Proficiency (M1 Input): {student_proficiency_notes}"

    prompt = f"""
You are an expert curriculum designer. Generate a structured, highly effective, and industry-aligned course curriculum based on the following parameters.

Course Title: {course_title}
Academic Level / Learner Profile: {level}{proficiency_context}
Duration: {duration_weeks} weeks
Learning Objectives: {objectives}{skills_context}

Return ONLY valid JSON (no markdown code blocks, no preamble, no explanation) in exactly this JSON schema format:

{{
  "course_title": "string",
  "level": "string",
  "duration_weeks": number,
  "course_outcomes": ["string", "string", ...],
  "modules": [
    {{
      "week": number,
      "module_title": "string",
      "topics": ["string", "string", ...],
      "learning_outcomes": ["string", ...],
      "skills_covered": ["string", ...],
      "suggested_resources": ["string", ...]
    }}
  ],
  "project_ideas": ["string", "string", ...],
  "industry_skill_alignment": {{
    "skills_integrated": ["string", ...],
    "alignment_summary": "string explaining how the curriculum meets industry demands"
  }}
}}

Make sure:
1. The number of modules matches the duration in weeks (one module per week).
2. Industry skills are naturally embedded into weekly topics and learning outcomes.
3. The content difficulty directly matches the specified academic level and learner profile.
"""
    return prompt.strip()


def generate_curriculum(course_title, level, duration_weeks, objectives, industry_skills=None, student_proficiency_notes=None):
    """Calls the Groq API and returns the parsed curriculum as a Python dict."""
    prompt = build_prompt(course_title, level, duration_weeks, objectives, industry_skills, student_proficiency_notes)

    candidate_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

    raw_text = None
    for model_name in candidate_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            raw_text = response.choices[0].message.content.strip()
            break
        except Exception as e:
            print(f"Warning: Model {model_name} failed: {e}. Trying fallback model...")
            time.sleep(1)

    if not raw_text:
        print("Error: All Groq models failed to respond.")
        return None

    # Clean up in case the model wraps output in markdown code fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    # Remove any trailing fence if present
    if "```" in raw_text:
        raw_text = raw_text.split("```")[0].strip()

    try:
        curriculum = json.loads(raw_text)
    except json.JSONDecodeError:
        # Try to locate valid JSON block between { and }
        start_idx = raw_text.find("{")
        end_idx = raw_text.rfind("}")
        if start_idx != -1 and end_idx != -1:
            try:
                curriculum = json.loads(raw_text[start_idx:end_idx + 1])
                return curriculum
            except json.JSONDecodeError:
                pass

        print("Warning: Model did not return clean JSON. Raw output:")
        print(raw_text)
        return None

    return curriculum


if __name__ == "__main__":
    # --- Sample test run with M3 industry skill integration ---
    sample_industry_skills = ["Python", "SQL", "Scikit-Learn", "Model Evaluation", "MLOps Basics"]
    result = generate_curriculum(
        course_title="Introduction to Machine Learning",
        level="Undergraduate - Beginner",
        duration_weeks=6,
        objectives="Understand core ML concepts, build simple models, and evaluate model performance using Python.",
        industry_skills=sample_industry_skills,
        student_proficiency_notes="Students have completed Python 101; no prior statistics or ML exposure."
    )

    if result:
        # Save output as a sample JSON file for the report
        with open("sample_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Curriculum generated successfully using Groq API! See sample_output.json")
        print(json.dumps(result, indent=2))