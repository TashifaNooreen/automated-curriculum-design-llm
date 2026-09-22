"""
Automated Curriculum Design Using LLMs
Model 3 (M3) - Industry Skill Intelligence Module
Step 1: Job Description Fetcher

Fetches real AI/ML job postings from the Adzuna API and saves them
as raw data for skill extraction (next step).
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not APP_ID or not APP_KEY:
    raise ValueError("ADZUNA_APP_ID / ADZUNA_APP_KEY not found. Add them to your .env file.")

# Adzuna is country-specific. "in" = India, "gb" = UK, "us" = USA, etc.
COUNTRY = "in"
BASE_URL = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/1"


def fetch_jobs(query="machine learning engineer", results_per_page=10):
    """Fetches job postings matching the query from Adzuna."""
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json",
    }

    # timeout=15 so a bad connection fails fast instead of hanging forever
    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    jobs = []
    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "url": job.get("redirect_url"),
        })

    return jobs


if __name__ == "__main__":
    queries = [
        "machine learning engineer",
        "AI engineer",
        "data scientist",
    ]

    all_jobs = []
    for q in queries:
        print(f"Fetching jobs for: {q}")
        try:
            jobs = fetch_jobs(query=q, results_per_page=10)
            all_jobs.extend(jobs)
        except requests.exceptions.RequestException as e:
            print(f"  Failed to fetch '{q}': {e}")

    with open("job_postings_raw.json", "w") as f:
        json.dump(all_jobs, f, indent=2)

    print(f"\nFetched {len(all_jobs)} job postings total.")
    print("Saved to job_postings_raw.json")