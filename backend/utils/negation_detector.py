"""
backend/utils/negation_detector.py

Generic negation and value-contradiction detector for requirement text.

Operates on raw text strings only.
NO project-specific logic, IDs, or filenames.

Detects:
- Prohibition vs Permission polarity conflicts (e.g. permitted without login vs prohibited)
- Mutually exclusive value conflicts (e.g. required vs optional, plaintext vs encrypted)
- Numeric constraint extraction and dimension comparison (e.g. 500 users vs 2000 users)

Rules for numeric comparison:
  CONFLICT:       functionally opposite (e.g. 0 vs positive where 0 = disabled)
  MODIFIED_VALUE: same capability dimension with different quantitative limit 
                  (e.g. 500 concurrent users vs 2000 simultaneous users) — NOT a conflict
  NONE:           no meaningful numeric relationship found
"""

import re
from typing import Tuple, List, Dict

# Explicit prohibition patterns (capability is forbidden / disabled)
PROHIBITION_PATTERNS = [
    r'\bmust\s+not\b',
    r'\bshall\s+not\b',
    r'\bshould\s+not\b',
    r'\bwill\s+not\b',
    r'\bcannot\b',
    r'\bcan\s+not\b',
    r'\bnot\s+allowed\b',
    r'\bnot\s+permitted\b',
    r'\bprohibited\b',
    r'\bforbidden\b',
    r'\bdisallowed\b',
    r'\bdisabled\b',
    r'\bprevented\b',
    r'\bblocked\b',
    r'\bno\s+\w+\s+(?:is|are|shall|must)\b',
    r'\bprohibit(?:s|ed|ing)?\b',
]

# Explicit permission / enablement patterns (capability is allowed / supported)
PERMISSION_PATTERNS = [
    r'\bmay\b',
    r'\bcan\b',
    r'\ballow(?:s|ed)?\b',
    r'\bpermitted\b',
    r'\benabled\b',
    r'\bsupported\b',
    r'\bwithout\s+(?:logging|authenticating|credentials|mfa|2fa|login)\b',
]

# Mutually exclusive concept pairs
EXCLUSIVE_PAIRS = [
    (r'\bwithout\s+(?:logging|login|auth)\b|\bguest\s+checkout\s+allowed\b', r'\bprohibit\w*\b|\bno\s+guest\b', 'Guest access allowed vs prohibited'),
    (r'\bpassword(?:\s+only)?\b', r'\bmfa\b|\b2fa\b|\bmulti.factor\b', 'Password-only vs MFA requirement'),
    (r'\bencrypt(?:ed|ion)?\b', r'\bunencrypt(?:ed|ion)?\b|\bno\s+encrypt\b|\bplaintext\b|\bcleartext\b', 'Encrypted vs unencrypted / plaintext'),
    (r'\brequired\b|\bmandatory\b', r'\boptional\b|\bvoluntary\b', 'Required/Mandatory vs Optional'),
]

# Common engineering measurement dimensions
DIMENSION_KEYWORDS = {
    'users': {'users', 'user', 'concurrent', 'simultaneous', 'clients', 'sessions', 'subscribers', 'riders', 'members', 'patients'},
    'latency': {'ms', 'millisecond', 'milliseconds', 'seconds', 'second', 'sec', 'response time', 'latency', 'duration', 'timeout'},
    'availability': {'uptime', 'availability', 'sla', '%', 'percent'},
    'capacity': {'books', 'seats', 'items', 'records', 'vehicles', 'limit', 'quota', 'max', 'maximum'},
    'attempts': {'attempts', 'retries', 'failed logins', 'tries', 'threshold'}
}


def _stem(word: str) -> str:
    """Basic normalization stem to match morphological variants like guests/guest, checkout/check."""
    w = word.lower().strip()
    if w.endswith('s') and len(w) > 3:
        w = w[:-1]
    if w.endswith('ing') and len(w) > 5:
        w = w[:-3]
    if w.endswith('ed') and len(w) > 4:
        w = w[:-2]
    return w[:4] if len(w) >= 4 else w


def is_prohibition(text: str) -> bool:
    """Returns True if the text contains an explicit prohibition statement."""
    t = text.lower()
    return any(re.search(p, t) for p in PROHIBITION_PATTERNS)


def is_permission(text: str) -> bool:
    """Returns True if the text contains an explicit permission statement."""
    t = text.lower()
    return any(re.search(p, t) for p in PERMISSION_PATTERNS)


def detect_negation_polarity(text: str) -> bool:
    """Returns True if the text contains an explicit prohibition pattern."""
    return is_prohibition(text)


def has_negation(text: str) -> bool:
    return detect_negation_polarity(text)


def _detect_dimension(context: str, unit: str) -> str:
    """Maps extracted context and unit to a canonical measurement dimension."""
    combined = f"{context} {unit}".lower()
    for dim, kw_set in DIMENSION_KEYWORDS.items():
        if any(kw in combined for kw in kw_set):
            return dim
    return unit if unit else 'quantity'


def extract_numeric_constraints(text: str) -> List[Dict]:
    """Extracts numeric constraints and dimensions from requirement text."""
    constraints = []
    t = text.lower()

    pattern = r'(\d+(?:\.\d+)?)\s*(%|ms|seconds?\b|sec\b|minutes?\b|hours?\b|days?\b|users?\b|concurrent\b|simultaneous\b|books?\b|seats?\b|attempts?\b|items?\b|records?\b)?'
    for m in re.finditer(pattern, t):
        value_str = m.group(1)
        unit = (m.group(2) or '').strip()
        start = max(0, m.start() - 35)
        end = min(len(t), m.end() + 35)
        context = t[start:end].strip()

        try:
            value = float(value_str)
            dim = _detect_dimension(context, unit)
            constraints.append({
                'value': value,
                'unit': unit,
                'dimension': dim,
                'context': context,
                'raw': m.group(0).strip()
            })
        except ValueError:
            continue

    return constraints


def check_polarity_conflict(text_a: str, text_b: str) -> Tuple[bool, str]:
    """
    Returns (True, reason) if text_a and text_b have conflicting polarity on the same concept.
    """
    ta = text_a.lower()
    tb = text_b.lower()

    # 1. Check explicit mutual exclusion pairs
    for pattern_a, pattern_b, reason in EXCLUSIVE_PAIRS:
        a_in_ta = bool(re.search(pattern_a, ta))
        b_in_tb = bool(re.search(pattern_b, tb))
        a_in_tb = bool(re.search(pattern_a, tb))
        b_in_ta = bool(re.search(pattern_b, ta))

        if (a_in_ta and b_in_tb) or (a_in_tb and b_in_ta):
            return True, f"Polarity conflict: {reason}"

    # 2. Check Prohibition vs Permission on shared concept
    prohib_a = is_prohibition(ta)
    prohib_b = is_prohibition(tb)
    perm_a = is_permission(ta)
    perm_b = is_permission(tb)

    if (prohib_a and perm_b and not prohib_b) or (prohib_b and perm_a and not prohib_a):
        stopwords = {
            'this', 'that', 'with', 'from', 'into', 'when', 'then', 'will',
            'shall', 'must', 'should', 'have', 'been', 'only', 'which', 'where',
            'system', 'platform', 'user', 'service', 'may', 'can'
        }
        tokens_a = [w for w in re.findall(r'\b[a-z]{3,}\b', ta) if w not in stopwords]
        tokens_b = [w for w in re.findall(r'\b[a-z]{3,}\b', tb) if w not in stopwords]

        stems_a = {_stem(w) for w in tokens_a}
        stems_b = {_stem(w) for w in tokens_b}

        # Also handle compound words like "checkout" vs "check out"
        ta_collapsed = ta.replace('check out', 'checkout')
        tb_collapsed = tb.replace('check out', 'checkout')
        if 'checkout' in ta_collapsed and 'checkout' in tb_collapsed:
            stems_a.add('check')
            stems_b.add('check')

        shared = stems_a & stems_b
        if len(shared) >= 1:
            return True, f"Polarity conflict: capability permitted in one requirement but prohibited in another [{', '.join(list(shared)[:4])}]"

    return False, ""


def check_numeric_conflict(text_a: str, text_b: str) -> Tuple[str, str]:
    """
    Compares numeric constraints between two texts.

    Returns:
        ('CONFLICT', reason)       — truly contradictory values (e.g. 0 vs positive where 0 = disabled)
        ('MODIFIED_VALUE', reason) — same capability dimension, different quantity
        ('NONE', '')               — no meaningful numeric comparison found
    """
    nums_a = extract_numeric_constraints(text_a)
    nums_b = extract_numeric_constraints(text_b)

    if not nums_a or not nums_b:
        return 'NONE', ''

    for na in nums_a:
        for nb in nums_b:
            va = na['value']
            vb = nb['value']
            dima = na['dimension']
            dimb = nb['dimension']

            if va == vb:
                continue

            # Check if both numbers measure the same dimension
            if dima == dimb and dima != 'quantity':
                # True conflict: zero vs positive in an access/capacity limit (0 means disabled)
                if (va == 0 and vb > 0) or (vb == 0 and va > 0):
                    return 'CONFLICT', f"Contradictory limit: {va} vs {vb} ({dima})"

                # Modified quantitative value
                return 'MODIFIED_VALUE', f"Same capability dimension ({dima}) with modified quantity: {va} → {vb}"

            # Direct unit match
            if na['unit'] and nb['unit'] and na['unit'] == nb['unit']:
                if (va == 0 and vb > 0) or (vb == 0 and va > 0):
                    return 'CONFLICT', f"Contradictory limit: {va} vs {vb} {na['unit']}"
                return 'MODIFIED_VALUE', f"Same capability with modified value: {va} {na['unit']} → {vb} {nb['unit']}"

    return 'NONE', ''
