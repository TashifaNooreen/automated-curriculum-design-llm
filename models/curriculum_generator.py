"""
Automated Curriculum Design Using LLMs
Model 2 (M2) - Minimal Curriculum Synthesis Prototype

This is a first working prototype: it takes basic course inputs and
uses the Gemini API to generate a structured curriculum in JSON format.

Later, this will be wired to:
- M1 (student proficiency scores) to adapt difficulty
- M3 (industry skill demand) to align topics with market needs
For now, it just takes manual inputs and produces a draft syllabus.
"""

import os
import json
from google import genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

client = genai.Client(api_key=API_KEY)


def build_prompt(course_title, level, duration_weeks, objectives):
    """Builds a structured prompt instructing the LLM to return clean JSON."""
    prompt = f"""
You are an expert curriculum designer. Generate a structured course curriculum
based on the following inputs.

Course Title: {course_title}
Academic Level: {level}
Duration: {duration_weeks} weeks
Learning Objectives: {objectives}

Return ONLY valid JSON (no markdown, no commentary) in exactly this format:

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
      "suggested_resources": ["string", ...]
    }}
  ],
  "project_ideas": ["string", "string", ...]
}}

Make sure the number of modules matches the duration in weeks
(one module per week, unless it makes sense to combine early weeks
for foundational topics).
"""
    return prompt.strip()


def generate_curriculum(course_title, level, duration_weeks, objectives):
    """Calls the Gemini API and returns the parsed curriculum as a Python dict."""
    prompt = build_prompt(course_title, level, duration_weeks, objectives)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()

    # Clean up in case the model wraps output in markdown code fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    try:
        curriculum = json.loads(raw_text)
    except json.JSONDecodeError:
        print("Warning: Model did not return clean JSON. Raw output:")
        print(raw_text)
        return None

    return curriculum


if __name__ == "__main__":
    # --- Sample test run ---
    result = generate_curriculum(
        course_title="Introduction to Machine Learning",
        level="Undergraduate - Beginner",
        duration_weeks=6,
        objectives="Understand core ML concepts, build simple models, "
                   "and evaluate model performance using Python."
    )

    if result:
        # Save output as a sample JSON file for the report
        with open("sample_output.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Curriculum generated successfully. See sample_output.json")
        print(json.dumps(result, indent=2))