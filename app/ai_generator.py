import os
import random
import json
from typing import List
import requests

# Generate questions via Hugging Face Inference API if configured, otherwise
# fall back to the local question bank. Configure with environment variables:
# HF_API_KEY (required for HF) and HF_MODEL (optional, default chosen).


def _hf_generate(prompt: str, model: str, token: str, max_tokens: int = 256):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "return_full_text": False},
        "options": {"wait_for_model": True}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    # response may be a list of dicts or plain text
    try:
        data = resp.json()
        return data
    except Exception:
        return resp.text


def generate_ai_questions(subject: str = None, topic: str = None, difficulty: str = 'Mixed', num: int = 5) -> List[dict]:
    hf_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')
    hf_model = os.environ.get('HF_MODEL', 'google/flan-t5-small')

    # Build a clear prompt asking for JSON output
    prompt = (
        f"Generate {num} multiple-choice questions in JSON array format. "
        f"Each item must be an object with keys: question, options (array of 4), answer, explanation. "
        f"Subject: {subject or 'General'}. Topic: {topic or 'General'}. Difficulty: {difficulty}. "
        "Return only valid JSON.")

    if hf_key:
        try:
            raw = _hf_generate(prompt, hf_model, hf_key, max_tokens=512)
            # If HF returns a list of tokens/dicts, try to parse for JSON
            if isinstance(raw, list):
                # Some models return [{'generated_text': '...'}]
                text = ''.join([item.get('generated_text', '') for item in raw if isinstance(item, dict)])
            elif isinstance(raw, dict):
                text = raw.get('generated_text') or json.dumps(raw)
            else:
                text = str(raw)

            # try to extract JSON from text
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return parsed[:num]
            except Exception:
                # attempt to find first '[' .. ']' block
                start = text.find('[')
                end = text.rfind(']')
                if start != -1 and end != -1 and end > start:
                    snippet = text[start:end+1]
                    try:
                        parsed = json.loads(snippet)
                        if isinstance(parsed, list):
                            return parsed[:num]
                    except Exception:
                        pass
        except Exception:
            # on any HF error fall back silently to local bank
            pass

    # Fallback: return random existing questions from data folder
    base = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
    with open(base, 'r', encoding='utf-8') as f:
        all_q = json.load(f)

    filtered = [q for q in all_q if (not subject or q.get('subject') == subject) and (not topic or topic == 'All' or q.get('topic') == topic)]
    if not filtered:
        filtered = all_q

    random.shuffle(filtered)
    return filtered[:min(len(filtered), num)]

