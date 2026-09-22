"""
Automated Curriculum Design Using LLMs
Model 3 (M3) - Industry Skill Intelligence Module
Step 2: Skill Extraction & Ranking (Groq version)

Reads raw job postings (job_postings_raw.json), uses Groq's Llama 3.3 70B
to extract structured skills from each description, then aggregates them
into a ranked demand list (industry_skill_demand.json).

Groq's free tier allows 30 requests/minute, much more headroom than
Gemini's free tier, so this runs considerably faster.
"""

import os
import json
import time
from collections import Counter
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Add it to your .env file.")

client = Groq(api_key=API_KEY)

CHECKPOINT_FILE = "skill_extraction_checkpoint.json"
SECONDS_BETWEEN_CALLS = 3  # safely under 30 requests/minute


def extract_skills(job_title, job_description, max_retries=5):
    """Calls Groq (Llama 3.3 70B) to extract a clean, normalized skill list."""
    prompt = f"""Extract the key technical and soft skills required for this job posting.
Normalize skill names (e.g. "python" and "Python programming" both become "Python").
Return ONLY a JSON array of skill name strings, nothing else. Limit to the
10 most important/explicit skills mentioned.

Job Title: {job_title}
Job Description: {job_description}

Example output format:
["Python", "SQL", "Machine Learning", "MLOps", "Communication"]"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            break
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                wait = 20
                print(f"  Rate limit hit, waiting {wait}s before retry ({attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            elif "503" in msg or "overloaded" in msg.lower():
                wait = 15
                print(f"  Server busy, waiting {wait}s before retry ({attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            else:
                raise
    else:
        print(f"  Failed after {max_retries} retries for '{job_title}' - skipping this one.")
        return []

    raw_text = response.choices[0].message.content.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    try:
        skills = json.loads(raw_text)
        if isinstance(skills, list):
            return skills
    except json.JSONDecodeError:
        pass

    print(f"  Warning: could not parse skills for '{job_title}'")
    return []


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"processed_indices": [], "results": []}


def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)


def process_all_jobs(input_file="job_postings_raw.json"):
    with open(input_file, "r") as f:
        jobs = json.load(f)

    checkpoint = load_checkpoint()
    processed = set(checkpoint["processed_indices"])

    if processed:
        print(f"Resuming from checkpoint: {len(processed)}/{len(jobs)} jobs already done.")

    for i, job in enumerate(jobs):
        if i in processed:
            continue

        title = job.get("title", "Unknown")
        desc = job.get("description", "")
        print(f"[{i+1}/{len(jobs)}] Extracting skills for: {title}")

        skills = extract_skills(title, desc)
        checkpoint["results"].append({"title": title, "skills": skills})
        checkpoint["processed_indices"].append(i)
        save_checkpoint(checkpoint)

        time.sleep(SECONDS_BETWEEN_CALLS)

    skill_counter = Counter()
    skill_to_roles = {}
    for entry in checkpoint["results"]:
        for skill in entry["skills"]:
            skill_counter[skill] += 1
            skill_to_roles.setdefault(skill, set()).add(entry["title"])

    return skill_counter, skill_to_roles, len(jobs)


def build_demand_report(skill_counter, skill_to_roles, total_jobs):
    max_count = max(skill_counter.values()) if skill_counter else 1

    report = []
    for skill, count in skill_counter.most_common():
        report.append({
            "skill_name": skill,
            "frequency": count,
            "demand_score": round(count / max_count, 3),
            "seen_in_roles": sorted(skill_to_roles[skill]),
        })

    return {
        "total_jobs_analyzed": total_jobs,
        "source": "Adzuna API (India) - ML/AI/Data Scientist roles",
        "extraction_model": "Groq - Llama 3.3 70B Versatile",
        "skills_ranked": report,
    }


if __name__ == "__main__":
    counter, roles_map, total = process_all_jobs("job_postings_raw.json")

    report = build_demand_report(counter, roles_map, total)

    with open("industry_skill_demand.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDone. Analyzed {total} jobs, extracted {len(counter)} unique skills.")
    print("Saved ranked demand report to industry_skill_demand.json")
    print("\nTop 10 skills by demand:")
    for item in report["skills_ranked"][:10]:
        print(f"  {item['skill_name']}: {item['frequency']} postings (score: {item['demand_score']})")