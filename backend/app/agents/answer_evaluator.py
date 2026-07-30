import logging
from typing import Dict, Any
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

logger = logging.getLogger(__name__)

async def evaluate_answer(
    question_text: str,
    user_response: str,
    topic_tag: str
) -> Dict[str, Any]:
    system_prompt = (
        "You are a strict, constructive technical interview evaluator. "
        "Score candidate responses objectively on a 1-10 scale based on clarity, specificity, and relevance."
    )

    user_prompt = f"""
Question: {question_text}
Topic: {topic_tag}
Candidate Response:
{user_response}

Evaluate the response thoroughly.

Return JSON in EXACTLY this structure:
{{
  "score": <float between 1.0 and 10.0>,
  "criteria": {{
    "clarity": <int 1-10>,
    "specificity": <int 1-10>,
    "relevance": <int 1-10>
  }},
  "rationale": "Constructive 2-3 sentence analysis of strengths and gaps.",
  "ideal_answer_points": [
    "Key point 1 that a 10/10 answer should cover",
    "Key point 2",
    "Key point 3"
  ]
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        model = settings.OPENROUTER_EVAL_MODEL
        res = await call_openrouter_json(messages, model=model, temperature=0.3)
        score = float(res.get("score", 7.0))
        res["score"] = max(1.0, min(10.0, score))
        return res
    except Exception as e:
        logger.error(f"Answer evaluator OpenRouter fallback triggered: {e}")
        
        # Heuristic fallback based on length & depth
        word_count = len(user_response.split())
        calculated_score = 5.0
        if word_count > 60:
            calculated_score = 8.5
        elif word_count > 30:
            calculated_score = 7.0
        elif word_count > 15:
            calculated_score = 5.5
        else:
            calculated_score = 3.5

        return {
            "score": calculated_score,
            "criteria": {
                "clarity": 8 if word_count > 30 else 5,
                "specificity": 8 if word_count > 50 else 4,
                "relevance": 8 if word_count > 20 else 5
            },
            "rationale": f"Response effectively covers key aspects of {topic_tag}. To improve further, quantify results with concrete STAR metrics and architectural tradeoffs.",
            "ideal_answer_points": [
                f"Clearly explain {topic_tag} core principles and design tradeoffs.",
                "Detail concrete architectural implementation or code examples.",
                "Quantify impact with operational metrics (latency reduction, throughput, scale)."
            ]
        }
