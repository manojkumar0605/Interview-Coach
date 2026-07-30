import json
import logging
import httpx
from typing import Any, Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

FALLBACK_MODELS = [
    "openrouter/auto",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-2.0-flash-lite-001",
    "openai/gpt-4o-mini"
]

async def call_openrouter_json(
    messages: list[dict[str, str]],
    model: str,
    temperature: float = 0.7,
    max_retries: int = 1
) -> Dict[str, Any]:
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is missing.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://ai-interview-coach.local",
        "X-Title": "AI Interview Coach",
        "Content-Type": "application/json"
    }

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = None

    for current_model in models_to_try:
        current_messages = list(messages)
        for attempt in range(max_retries + 1):
            payload = {
                "model": current_model,
                "messages": current_messages,
                "temperature": temperature,
                "response_format": {"type": "json_object"}
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                    if response.status_code in (402, 404, 429):
                        logger.warning(f"Model {current_model} returned {response.status_code}. Trying next model...")
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        break

                    response.raise_for_status()
                    data = response.json()
                except Exception as e:
                    logger.error(f"OpenRouter call failed for model {current_model} (attempt {attempt+1}): {str(e)}")
                    last_error = str(e)
                    if attempt == max_retries:
                        break
                    continue

            try:
                content = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                logger.error(f"Malformed payload structure from model {current_model}: {data}")
                last_error = "Invalid payload structure"
                break

            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()

            try:
                parsed_json = json.loads(cleaned_content)
                logger.info(f"Successfully obtained JSON response from model {current_model}")
                return parsed_json
            except json.JSONDecodeError as err:
                logger.warning(f"Failed to parse JSON from {current_model} (attempt {attempt+1}): {err}")
                if attempt < max_retries:
                    current_messages.append({"role": "assistant", "content": content})
                    current_messages.append({
                        "role": "user",
                        "content": "Your response was not valid JSON. Please return ONLY raw, valid JSON matching the requested schema."
                    })
                else:
                    break

    logger.error(f"All OpenRouter models failed. Last error: {last_error}")
    raise RuntimeError(f"OpenRouter API request failed across models: {last_error}")
