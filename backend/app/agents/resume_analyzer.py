import logging
from typing import Dict, Any
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

logger = logging.getLogger(__name__)

async def analyze_resume(raw_text: str, target_role: str = "") -> Dict[str, Any]:
    system_prompt = (
        "You are an expert technical recruiter and resume analyst. "
        "Analyze the provided resume text and extract key candidate features into structured JSON."
    )
    
    user_prompt = f"""
Target Role: {target_role if target_role else 'Not specified'}

Resume Content:
{raw_text[:4000]}

Return a JSON object with EXACTLY the following structure:
{{
  "skills": ["list", "of", "key", "skills"],
  "years_experience": <number or estimated total years of experience, e.g. 4>,
  "past_roles": ["list of recent job titles"],
  "seniority_estimate": "<Junior|Mid-Level|Senior|Staff|Lead>"
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        model = settings.OPENROUTER_QUESTION_MODEL
        result = await call_openrouter_json(messages, model=model, temperature=0.2)
        return result
    except Exception as e:
        logger.error(f"Resume analyzer OpenRouter fallback triggered: {e}")
        # Deterministic fallback based on raw text heuristic
        skills = []
        for word in ["Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "SQL", "Docker", "AWS", "System Design", "PostgreSQL", "Git", "REST APIs", "GraphQL", "Java", "C++", "Go"]:
            if word.lower() in raw_text.lower():
                skills.append(word)
        if not skills:
            skills = ["Software Engineering", "System Design", "Problem Solving"]
            
        return {
            "skills": skills[:8],
            "years_experience": 4,
            "past_roles": [target_role if target_role else "Software Developer"],
            "seniority_estimate": "Senior" if "senior" in raw_text.lower() or "lead" in raw_text.lower() else "Mid-Level"
        }
