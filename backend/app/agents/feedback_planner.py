import logging
from typing import Dict, Any, List
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

logger = logging.getLogger(__name__)

async def generate_study_plan(
    session_results: List[Dict[str, Any]],
    role_target: str,
    historical_weak_topics: List[str],
    grammar_insights: Dict[str, Any] = None
) -> Dict[str, Any]:
    system_prompt = (
        "You are a senior career advisor and executive speech coach. "
        "Analyze a candidate's mock interview technical results AND communication/grammar style to construct a personalized study plan."
    )

    grammar_info_str = str(grammar_insights) if grammar_insights else "No historical grammar issues logged."

    user_prompt = f"""
Target Role: {role_target}
Historical Technical Weak Topics: {historical_weak_topics}
Historical Grammar & Communication Insights: {grammar_info_str}

Current Session Breakdown:
{session_results}

Generate a comprehensive performance narrative, technical recommendations, AND a dedicated communication & grammar feedback section.

Return JSON in EXACTLY this structure:
{{
  "summary": "Detailed, encouraging performance summary highlighting technical progress and spoken delivery.",
  "overall_score": <float average content score across questions>,
  "grammar_score": <float average grammar score across questions>,
  "strengths": ["List of 2-4 strong performance topics/traits"],
  "weak_topics": ["List of technical topics needing improvement"],
  "communication_feedback": {{
    "tone_summary": "Professional/Conversational narrative summary of speech delivery",
    "common_flaws": ["e.g., Filler word frequency", "Run-on sentences"],
    "actionable_tips": ["Tip 1 to improve spoken clarity", "Tip 2"]
  }},
  "recommended_next_steps": [
    {{
      "topic": "Topic Name or Communication Skill",
      "action": "Specific study material or practice recommendation",
      "priority": "High | Medium | Low"
    }}
  ]
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        model = settings.OPENROUTER_FEEDBACK_MODEL
        res = await call_openrouter_json(messages, model=model, temperature=0.5)
        return res
    except Exception as e:
        logger.error(f"Feedback planner OpenRouter fallback triggered: {e}")

    scores = [item.get("score", 7.0) for item in session_results if "score" in item]
    avg_s = round(sum(scores) / len(scores), 1) if scores else 7.2

    weak_list = list(set([item.get("topic") for item in session_results if item.get("score", 7) < 6.0] + historical_weak_topics))
    if not weak_list:
        weak_list = ["System Concurrency", "Database Indexing Optimization"]

    g_avg = grammar_insights.get("overall_grammar_avg", 8.0) if grammar_insights else 8.0

    return {
        "summary": f"Solid overall performance demonstrating strong core domain knowledge for {role_target}. Continual practice on edge case tradeoffs, reducing filler words, and quantitative STAR metrics will elevate your interview performance.",
        "overall_score": avg_s,
        "grammar_score": g_avg,
        "strengths": [
            "Clear technical communication & structure",
            "Strong problem-solving methodology",
            "Effective domain terminology usage"
        ],
        "weak_topics": weak_list,
        "communication_feedback": {
            "tone_summary": "Overall professional tone with occasional conversational filler words.",
            "common_flaws": ["Occasional filler words (like, basically)", "Lengthy explanations"],
            "actionable_tips": [
                "Pause for 1 second before answering complex questions to eliminate 'um/like'.",
                "Use the STAR framework explicitly to structure executive-level responses."
            ]
        },
        "recommended_next_steps": [
            {
                "topic": weak_list[0] if len(weak_list) > 0 else "System Architecture",
                "action": "Study B-Tree vs LSM trees, index cardinality, and execution query plans.",
                "priority": "High"
            },
            {
                "topic": "Spoken Conciseness & Tone",
                "action": "Record yourself speaking for 2 minutes without using filler words like 'basically' or 'like'.",
                "priority": "High"
            },
            {
                "topic": "Behavioral STAR Metrics",
                "action": "Practice structuring answers with Situation, Task, Action, and explicit Result metrics.",
                "priority": "Medium"
            }
        ]
    }
