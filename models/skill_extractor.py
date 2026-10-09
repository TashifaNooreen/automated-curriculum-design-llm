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
# pyrefly: ignore [missing-import]
from groq import Groq
# pyrefly: ignore [missing-import] 
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


try:
    from models.gartner_fetcher import get_gartner_tech_trends
except ImportError:
    from gartner_fetcher import get_gartner_tech_trends


def build_demand_report(skill_counter, skill_to_roles, total_jobs, include_gartner=True):
    """
    Fuses Adzuna job posting frequency with Gartner Strategic Technology Trends
    to create a multi-source weighted industry skill demand report.
    """
    max_count = max(skill_counter.values()) if skill_counter else 1

    # Map of skill_name -> unified data object
    unified_skills = {}

    # 1. Process Adzuna job posting skills
    for skill, count in skill_counter.most_common():
        norm_score = round(count / max_count, 3)
        unified_skills[skill] = {
            "skill_name": skill,
            "frequency": count,
            "demand_score": norm_score,
            "seen_in_roles": sorted(skill_to_roles.get(skill, [])),
            "source": "Adzuna Job Market",
            "category": "Current Market Demand",
            "gartner_boost": False,
        }

    # 2. Integrate Gartner emerging tech trends
    gartner_trends = get_gartner_tech_trends() if include_gartner else []
    for trend in gartner_trends:
        name = trend["skill_name"]
        impact = trend["gartner_impact_score"]

        if name in unified_skills:
            # Boost score for skills present in BOTH live jobs and Gartner reports
            item = unified_skills[name]
            fused_score = round(0.6 * item["demand_score"] + 0.4 * impact, 3)
            item["demand_score"] = fused_score
            item["source"] = "Adzuna Job Market + Gartner Strategic Trend"
            item["category"] = f"High-Impact ({trend['category']})"
            item["gartner_boost"] = True
        else:
            unified_skills[name] = {
                "skill_name": name,
                "frequency": 1,
                "demand_score": round(0.85 * impact, 3),
                "seen_in_roles": ["AI/Software Engineer (Emerging Role)"],
                "source": "Gartner Strategic Tech Trend",
                "category": trend["category"],
                "gartner_boost": True,
            }

    # Sort final report by fused demand_score descending
    ranked_report = sorted(unified_skills.values(), key=lambda x: x["demand_score"], reverse=True)

    return {
        "total_jobs_analyzed": total_jobs,
        "source": "Multi-Source Fusion (Adzuna API + Gartner Tech Trends)",
        "extraction_model": "Groq - Llama 3.3 70B Versatile",
        "gartner_trends_integrated": len(gartner_trends),
        "skills_ranked": ranked_report,
    }


if __name__ == "__main__":
    counter, roles_map, total = process_all_jobs("job_postings_raw.json")

    report = build_demand_report(counter, roles_map, total, include_gartner=True)

    with open("industry_skill_demand.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDone. Analyzed {total} jobs & Gartner trends, extracted {len(report['skills_ranked'])} unique skills.")
    print("Saved multi-source ranked demand report to industry_skill_demand.json")
    print("\nTop 10 skills by demand (Adzuna + Gartner Fused):")
    for item in report["skills_ranked"][:10]:
        print(f"  {item['skill_name']}: score {item['demand_score']} ({item['source']})")