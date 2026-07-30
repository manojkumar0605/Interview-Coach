import logging
from typing import Dict, Any, List
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

logger = logging.getLogger(__name__)

async def match_roles(resume_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes extracted candidate skills, experience, and seniority from resume_analyzer output,
    and returns 4-6 ranked role recommendations with match scores, skill gaps, and market positioning.

    Returns:
    {
      "recommended_roles": [
        {
          "title": "Senior Backend Engineer",
          "match_score": 88,
          "reasoning": "Strong experience in Python, FastAPI, and database indexing...",
          "matching_skills": ["Python", "FastAPI", "PostgreSQL"],
          "skill_gaps": ["GraphQL"],
          "seniority_fit": "matches current level"
        },
        ...
      ],
      "summary": "Candidate has strong backend infrastructure experience..."
    }
    """
    system_prompt = (
        "You are an executive talent strategist and career counselor. "
        "Analyze structured candidate profile data and generate a ranked list of 4 to 6 job roles "
        "the candidate is well-suited for, complete with match scores, transferable skill analysis, and skill gaps."
    )

    user_prompt = f"""
Candidate Profile JSON:
{resume_json}

Analyze this profile and generate 4 to 6 target job roles ranked by suitability.
Include a mix of 2-3 'matches current level' roles, 1-2 'slight stretch' roles, and 1 'reach role'.

Return JSON in EXACTLY this structure:
{{
  "recommended_roles": [
    {{
      "title": "Job Title",
      "match_score": <int between 50 and 98, descending order>,
      "reasoning": "1-2 sentence explanation of why this candidate fits",
      "matching_skills": ["Skill1", "Skill2", "Skill3"],
      "skill_gaps": ["Missing Skill 1", "Missing Skill 2"],
      "seniority_fit": "matches current level | slight stretch | reach role"
    }}
  ],
  "summary": "1-2 sentence overview of candidate's overall market positioning and highest leverage career directions."
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        model = settings.OPENROUTER_MATCH_MODEL
        res = await call_openrouter_json(messages, model=model, temperature=0.4)
        roles = res.get("recommended_roles", [])
        if roles:
            # Sort by match_score descending just in case
            roles.sort(key=lambda r: r.get("match_score", 0), reverse=True)
            res["recommended_roles"] = roles
            return res
    except Exception as e:
        logger.error(f"Job matcher OpenRouter fallback triggered: {e}")

    skills = resume_json.get("skills", ["Software Engineering"])
    seniority = resume_json.get("seniority_estimate", "Mid-Level")
    past_roles = resume_json.get("past_roles", [])
    primary_role = past_roles[0] if past_roles else "Software Engineer"

    return {
        "recommended_roles": [
            {
                "title": f"Senior {primary_role}",
                "match_score": 90,
                "reasoning": f"Strong alignment with candidate's proven background in {', '.join(skills[:3])}.",
                "matching_skills": skills[:4],
                "skill_gaps": ["Distributed Tracing", "System Resilience"],
                "seniority_fit": "matches current level"
            },
            {
                "title": "Backend Systems Architect",
                "match_score": 83,
                "reasoning": "Leverages technical design expertise and backend service engineering background.",
                "matching_skills": skills[:3] + ["System Design"],
                "skill_gaps": ["High-Availability Cluster Management"],
                "seniority_fit": "slight stretch"
            },
            {
                "title": "Full Stack Lead Engineer",
                "match_score": 78,
                "reasoning": "Good fit for end-to-end service delivery and technical leadership.",
                "matching_skills": skills[:3] + ["API Architecture"],
                "skill_gaps": ["Frontend Performance Optimization"],
                "seniority_fit": "slight stretch"
            },
            {
                "title": "Staff Platform Engineer",
                "match_score": 68,
                "reasoning": "High-impact reach role expanding infrastructure automation and developer tooling.",
                "matching_skills": skills[:2] + ["Cloud Infrastructure"],
                "skill_gaps": ["Kubernetes Operator Development", "eBPF Monitoring"],
                "seniority_fit": "reach role"
            }
        ],
        "summary": f"Strong market positioning for {seniority} engineering roles specializing in backend architecture and service scalability."
    }
