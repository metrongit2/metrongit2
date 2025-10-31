import re
from math import log2

# Basic regexes (expandable)
REGEXES = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                      # AWS Access Key ID
    re.compile(r"aws_secret_access_key.?[:=]\s*['\"]?([A-Za-z0-9/+=]{40,})"),
    re.compile(r"-----BEGIN (RSA )?PRIVATE KEY-----"),
    re.compile(r"(?:api[_-]?key|secret|token)[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9\-_+=]{8,})", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9_\-]{32,}"),                    # long token heuristic
]

def entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    ent = 0.0
    length = len(s)
    for v in freq.values():
        p = v / length
        ent -= p * log2(p)
    return ent

def scan_text_for_secrets(text: str) -> list[str]:
    matches = []
    for rx in REGEXES:
        for m in rx.finditer(text):
            snippet = m.group(0)
            # heuristic: if entropy high or known key marker
            if entropy(snippet) > 3.0 or "PRIVATE KEY" in snippet or "BEGIN" in snippet:
                matches.append(snippet)
    return matches
