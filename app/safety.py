import re

MAX_USER_PROMPT_LEN = 2000

DANGEROUS_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions?',
    r'reveal\s+(your|the)\s+(system\s+)?prompt',
    r'you\s+are\s+now\s+in\s+developer\s+mode',
    r'system\s+override',
    r'bypass\s+safety',
]

def validate_user_prompt(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "Query is empty."
    if len(text) > MAX_USER_PROMPT_LEN:
        return False, f"Query is too long (max {MAX_USER_PROMPT_LEN} chars)."
    return True, ""

def detect_prompt_injection(text: str) -> bool:
    text = text.strip()
    return any(re.search(p, text, re.IGNORECASE) for p in DANGEROUS_PATTERNS)

def sanitize_user_prompt(text: str) -> str:
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned[:MAX_USER_PROMPT_LEN]

