from __future__ import annotations

import re
from typing import Dict, List


_WHITESPACE_RE = re.compile(r"\s+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SENSITIVE_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"developer\s+(message|instructions?)", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?(secret|hidden)\s+(prompt|instructions?)", re.IGNORECASE),
    re.compile(r"authorization\s*:\s*bearer\s+[a-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"api[_\s-]?key\s*[:=]\s*[^\s]+", re.IGNORECASE),
    re.compile(r"secret[_\s-]?key\s*[:=]\s*[^\s]+", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*[^\s]+", re.IGNORECASE),
    re.compile(r"token\s*[:=]\s*[^\s]+", re.IGNORECASE),
]


def sanitize_public_text(text: str, max_length: int = 280) -> Dict[str, object]:
    normalized = _WHITESPACE_RE.sub(" ", (text or "").strip())
    normalized = _HTML_TAG_RE.sub("", normalized)
    normalized = normalized.replace("<", "").replace(">", "")

    redactions: List[str] = []
    safe_text = normalized
    for pattern in _SENSITIVE_PATTERNS:
        if pattern.search(safe_text):
            redactions.append(pattern.pattern)
            safe_text = pattern.sub("[redacted]", safe_text)

    safe_text = safe_text[:max_length].strip()
    return {
        "text": safe_text,
        "redactions": redactions,
        "was_sanitized": bool(redactions) or safe_text != normalized,
    }


def contains_sensitive_instruction(text: str) -> bool:
    normalized = _WHITESPACE_RE.sub(" ", (text or "").strip())
    return any(pattern.search(normalized) for pattern in _SENSITIVE_PATTERNS)