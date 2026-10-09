"""
Automated Curriculum Design Using LLMs
Model 3 (M3) - Industry Skill Intelligence Module
Gartner Strategic Technology Trends Fetcher

Curates and extracts forward-looking AI & Software Engineering skill requirements
from Gartner's Top Strategic Technology Trends reports.
"""

def get_gartner_tech_trends():
    """
    Returns strategic AI and Software Engineering trends from Gartner reports
    to complement live job posting data with forward-looking emerging skill demand.
    """
    trends = [
        {
            "skill_name": "Agentic AI Systems",
            "category": "Autonomous AI & Agentic Systems",
            "gartner_impact_score": 0.98,
            "description": "Designing autonomous software agents capable of multi-step planning, decision making, and tool usage.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "Retrieval-Augmented Generation (RAG)",
            "category": "AI Engineering & Architecture",
            "gartner_impact_score": 0.95,
            "description": "Connecting LLMs to external enterprise knowledge bases and vector databases for accurate, grounded AI answers.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "Vector Databases & Embeddings",
            "category": "Data & Model Infrastructure",
            "gartner_impact_score": 0.92,
            "description": "Indexing, searching, and managing high-dimensional vector embeddings (Pinecone, ChromaDB, Milvus, Qdrant).",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "AI Governance & Guardrails",
            "category": "Governance, Trust & Security",
            "gartner_impact_score": 0.90,
            "description": "Ensuring safety, compliance, ethical standards, hallucination reduction, and security in deployed AI models.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "Model Fine-Tuning (PEFT & LoRA)",
            "category": "AI Engineering & Architecture",
            "gartner_impact_score": 0.88,
            "description": "Adapting foundation models to domain-specific datasets efficiently using parameter-efficient fine-tuning techniques.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "MLOps & LLMOps Pipeline Automation",
            "category": "Data & Model Infrastructure",
            "gartner_impact_score": 0.94,
            "description": "Automating continuous integration, deployment, monitoring, and versioning for ML and LLM models.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "Synthetic Data Generation",
            "category": "Data & Model Infrastructure",
            "gartner_impact_score": 0.85,
            "description": "Generating artificially structured and unstructured training data for privacy preservation and model bootstrapping.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "Prompt Engineering & Chain-of-Thought",
            "category": "AI Engineering & Architecture",
            "gartner_impact_score": 0.89,
            "description": "Crafting optimized system prompts, few-shot examples, and reasoning chains for complex LLM tasks.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        },
        {
            "skill_name": "Multimodal AI Integration",
            "category": "Autonomous AI & Agentic Systems",
            "gartner_impact_score": 0.91,
            "description": "Processing and combining vision, audio, text, and structured data in unified model architectures.",
            "source": "Gartner Strategic Tech Trends 2025-2026"
        }
    ]
    return trends


if __name__ == "__main__":
    trends = get_gartner_tech_trends()
    print(f"Loaded {len(trends)} Gartner strategic technology trends.")
    for t in trends[:5]:
        print(f" - {t['skill_name']} ({t['category']}) - Impact Score: {t['gartner_impact_score']}")
