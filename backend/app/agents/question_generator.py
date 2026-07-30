import logging
from typing import Dict, Any, List
from app.agents.openrouter_client import call_openrouter_json
from app.config import settings

logger = logging.getLogger(__name__)

async def generate_questions(
    resume_json: Dict[str, Any],
    target_role: str,
    weak_topics: List[str]
) -> List[Dict[str, Any]]:
    system_prompt = (
        "You are a principal hiring manager conducting mock technical and behavioral interviews. "
        "Your task is to generate realistic, role-specific interview questions based on candidate resume, target role, and past weak areas."
    )

    weak_topics_str = ", ".join(weak_topics) if weak_topics else "None identified yet"

    user_prompt = f"""
Target Role: {target_role}
Candidate Resume Summary: {resume_json}
Historical Weak Topics to Focus On: {weak_topics_str}

Please generate an ordered list of 5 to 8 interview questions tailored specifically for this candidate and target role.
Ensure a balanced mix of technical domain questions and STAR-method behavioral questions.
If weak topics exist, include at least 2 questions specifically targeting those weak topics.

Return a JSON object formatted as:
{{
  "questions": [
    {{
      "text": "Question clear description",
      "topic_tag": "Topic name (e.g. System Design, REST APIs, Leadership, Problem Solving)",
      "difficulty": "easy | medium | hard",
      "type": "technical | behavioral"
    }}
  ]
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        model = settings.OPENROUTER_QUESTION_MODEL
        res = await call_openrouter_json(messages, model=model, temperature=0.6)
        questions = res.get("questions", [])
        if questions:
            return questions
    except Exception as e:
        logger.error(f"Question generator OpenRouter fallback triggered: {e}")

    # High quality fallback questions matching target role
    return [
        {
            "text": f"Walk me through a key system architectural decision you made in your recent experience as a {target_role}. What were the key tradeoffs?",
            "topic_tag": "System Design",
            "difficulty": "hard",
            "type": "technical"
        },
        {
            "text": f"How do you approach database performance tuning, indexing, and query optimization when handling high throughput in {target_role} applications?",
            "topic_tag": "Database Indexing",
            "difficulty": "medium",
            "type": "technical"
        },
        {
            "text": "Describe a time when you experienced a critical production bug or outage. How did you triage, resolve, and prevent future occurrences?",
            "topic_tag": "Incident Response",
            "difficulty": "medium",
            "type": "behavioral"
        },
        {
            "text": "How do you handle thread safety, race conditions, or asynchronous concurrency when building backend API services?",
            "topic_tag": "Concurrency",
            "difficulty": "hard",
            "type": "technical"
        },
        {
            "text": "Tell me about a situation where you had an engineering disagreement with a peer or stakeholder regarding implementation details. How was it resolved using data?",
            "topic_tag": "Leadership & Collaboration",
            "difficulty": "medium",
            "type": "behavioral"
        }
    ]
