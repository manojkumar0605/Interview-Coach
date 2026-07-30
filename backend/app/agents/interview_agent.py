from typing import Dict, Any, Optional
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

async def evaluate_shallowness_and_maybe_followup(
    question_text: str,
    user_answer: str,
    topic_tag: str,
    eval_score: float
) -> Optional[Dict[str, Any]]:
    """
    Decides whether an answer is too shallow or missing critical depth.
    If shallow and score < 7.0, returns a follow-up question object:
    {
      "text": "Follow-up probe question...",
      "topic_tag": topic_tag,
      "difficulty": "medium",
      "type": "follow-up"
    }
    Otherwise returns None.
    """
    # If the user gave a strong answer or very short refusal, don't generate follow-up
    if eval_score >= 7.5 or len(user_answer.strip().split()) < 4:
        return None

    system_prompt = (
        "You are an interview agent. Determine if a candidate's answer was shallow or missing key depth. "
        "If so, formulate ONE concise follow-up probe question asking for specific metrics, examples, or technical details."
    )

    user_prompt = f"""
Original Question: {question_text}
Candidate's Answer: {user_answer}
Topic: {topic_tag}
Evaluation Score: {eval_score}/10

Determine if a follow-up probe question is needed.
Return a JSON object formatted as:
{{
  "needs_follow_up": true | false,
  "follow_up_question": {{
    "text": "Can you elaborate on...",
    "topic_tag": "{topic_tag}",
    "difficulty": "medium",
    "type": "follow-up"
  }} // or null if needs_follow_up is false
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        res = await call_openrouter_json(messages, model=settings.OPENROUTER_EVAL_MODEL, temperature=0.5)
        if res.get("needs_follow_up") and res.get("follow_up_question"):
            fq = res["follow_up_question"]
            if isinstance(fq, dict) and fq.get("text"):
                return {
                    "text": fq["text"],
                    "topic_tag": fq.get("topic_tag", topic_tag),
                    "difficulty": fq.get("difficulty", "medium"),
                    "type": "follow-up"
                }
    except Exception:
        pass

    return None
