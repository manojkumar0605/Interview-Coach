import logging
from typing import Dict, Any
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

logger = logging.getLogger(__name__)

async def evaluate_grammar(answer_text: str) -> Dict[str, Any]:
    """
    Evaluates the grammatical correctness, sentence structure, filler words,
    clarity, and tone of a candidate's spoken/written interview response.

    Returns:
    {
      "grammar_score": 8.0,
      "issues": [
        { "type": "grammar|filler_word|clarity", "original": "...", "suggestion": "...", "explanation": "..." }
      ],
      "filler_word_count": 2,
      "tone": "conversational | professional | too_casual",
      "corrected_version": "Full rewritten response..."
    }
    """
    system_prompt = (
        "You are an expert executive speech coach and English grammar advisor for interview preparation. "
        "Analyze candidate responses for grammar errors, filler words (um, like, sort of, basically, ya know), "
        "sentence structure clarity, and professional tone."
    )

    user_prompt = f"""
Candidate Response:
"{answer_text}"

Evaluate the grammar, sentence structure, filler word usage, and professional tone.

Return JSON in EXACTLY this structure:
{{
  "grammar_score": <int 1 to 10 based on language precision>,
  "issues": [
    {{
      "type": "grammar | filler_word | clarity",
      "original": "Exact phrase from candidate response",
      "suggestion": "Suggested fix or 'remove'",
      "explanation": "Brief explanation of the improvement"
    }}
  ],
  "filler_word_count": <int total count of filler words used>,
  "tone": "conversational | professional | too_casual",
  "corrected_version": "The full candidate response rewritten into clean, polished, professional English."
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        model = settings.OPENROUTER_GRAMMAR_MODEL
        res = await call_openrouter_json(messages, model=model, temperature=0.3)
        
        # Ensure score bounds
        score = float(res.get("grammar_score", 8))
        res["grammar_score"] = max(1.0, min(10.0, score))
        return res
    except Exception as e:
        logger.error(f"Grammar coach OpenRouter fallback triggered: {e}")

        # Heuristic fallback analysis
        text_lower = answer_text.lower()
        filler_words = ["um", "uh", "like", "basically", "you know", "sort of", "kind of", "actually"]
        detected_fillers = [fw for fw in filler_words if fw in text_lower]
        filler_count = sum(text_lower.count(fw) for fw in detected_fillers)

        issues = []
        for fw in detected_fillers:
            issues.append({
                "type": "filler_word",
                "original": fw,
                "suggestion": "remove",
                "explanation": f"Remove filler word '{fw}' to maintain a concise, confident tone."
            })

        calculated_score = max(5.0, 9.0 - (filler_count * 0.8))

        return {
            "grammar_score": round(calculated_score, 1),
            "issues": issues,
            "filler_word_count": filler_count,
            "tone": "professional" if filler_count < 2 else "conversational",
            "corrected_version": answer_text
        }
