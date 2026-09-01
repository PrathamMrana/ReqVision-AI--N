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

# Explicit policy prohibition patterns (the feature/access itself is forbidden by policy)
POLICY_PROHIBITION_PATTERNS = [
    r'\b(?:is|are|shall\s+be|must\s+be)\s+(?:strictly\s+)?(?:prohibited|forbidden|disallowed|not\s+permitted|not\s+allowed)\b',
    r'\b(?:must\s+not|shall\s+not|should\s+not|may\s+not|cannot|can\s+not)\s+(?:be\s+allowed|be\s+permitted|access|use|perform|execute|checkout|login|authenticate)\b',
    r'\bno\s+(?:guest|anonymous|unauthenticated|unauthorized)\s+.*?\b(?:allowed|permitted|access|checkout)\b',
    r'\bprohibit\w*\s+.*?\b(?:guest|anonymous|unauthorized|reversible|plaintext|unencrypted)\b',
    r'\b(?:strictly\s+)?forbidden\b',
    r'\bdisallowed\b',
    r'\bnot\s+(?:permitted|allowed)\b',
]

# Explicit policy permission patterns (access/feature is explicitly permitted without standard constraints)
POLICY_PERMISSION_PATTERNS = [
    r'\bwithout\s+(?:logging|authenticating|credentials|mfa|2fa|login|auth)\b',
    r'\bguest\s+checkout\s+allowed\b',
    r'\banonymous\s+access\s+(?:is\s+)?allowed\b',
    r'\bmay\s+(?:check\s*out|access|view|browse|purchase)\s+without\b',
    r'\ballow(?:s|ed)?\s+.*?\bwithout\s+(?:login|auth|credentials)\b',
]

# Mutually exclusive concept pairs
EXCLUSIVE_PAIRS = [
    (r'\bwithout\s+(?:logging|login|auth)\b|\bguest\s+checkout\s+allowed\b|\bguests?\s+may\s+check\s*out\b', r'\bprohibit\w*\b|\bno\s+guest\b|\bguest\s+.*?\bprohibited\b', 'Guest access allowed vs prohibited'),
    (r'\bpassword(?:\s+only)?\b', r'\bmfa\b|\b2fa\b|\bmulti.factor\b', 'Password-only vs MFA requirement'),
    (r'\brequired\s+.*?\b(?:multi-?factor|mfa|2fa)\b|\bmandatory\s+(?:mfa|2fa|multi-?factor)\b', r'\b(?:multi-?factor|mfa|2fa)\s+.*?\b(?:prohibited|disabled|forbidden)\b', 'MFA Required vs Prohibited'),
    (r'\b(?:is|are|shall\s+be)\s+enabled\b|\benabled\s+by\s+default\b', r'\b(?:is|are)\s+disabled\b|\bdisabled\s+and\b', 'Enabled vs Disabled policy conflict'),
    (r'\b(?:stored?\s+(?:using|as)\s+)?reversible\s+(?:des\s+|caesar\s+)?(?:encrypt\w*|storage|password|cipher)?\b|\breversible\s+(?:storage|encryption|phrase|key)\b', r'\bsalted\s+(?:pbkdf2|bcrypt|argon2id|hash)\b|\b(?:never|must\s+not|shall\s+not|cannot|prohibit\w*|forbid\w*|disallow\w*|avoid\w*)\s+.*?\b(?:stored?\s+)?reversib\w*\b|\breversible\s+.*?\b(?:prohibited|forbidden|disallowed)\b|\bone-way\s+hash\b', 'Reversible credential encryption vs Salted one-way cryptographic hashing'),
    (r'\bstore\w*\s+in\s+plaintext\b|\bplaintext\s+(?:storage|records?|passwords?|credentials?)\b|\bunencrypted\s+storage\b', r'\bencrypt\w*\s+all\b|\bencrypted\s+at\s+rest\b|\b(?:never|must\s+not|shall\s+not|cannot|prohibit\w*|forbid\w*)\s+.*?\bplaintext\b', 'Plaintext vs Encrypted storage'),
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


def is_defensive_system_behavior(text: str) -> bool:
    """
    Returns True if the text describes defensive system behavior:
    preventing, blocking, rejecting, filtering, denying, or discarding
    invalid, incompatible, unauthorized, unsafe, duplicate, or out-of-bounds states/inputs.
    """
    t = text.lower()
    
    # Defensive action verbs
    has_defensive_action = bool(re.search(
        r'\b(?:prevent|block|reject|deny|filter|flag|discard|suppress|guard|stop|disallow|intercept|safeguard)\w*\b',
        t
    ))
    
    # Violation / constraint conditions
    has_violation_condition = bool(re.search(
        r'\b(?:invalid|unauthorized|duplicate|expired|malformed|corrupted|tampered|unauthenticated|'
        r'un-?approved|illegal|incompatible|unsafe|conflict\w*|collision|error|over-?limit|'
        r'exceed\w*|outside\b.{0,15}\brange|breach|abnormal|hazard|defect|out\s+of\s+range)\b',
        t
    ))
    
    # Context-scoped constraint enforcement (e.g. "before a schedule is committed", "unless authorized")
    has_scoped_guard = bool(re.search(
        r'\b(?:unless|except|before\s+.*?\bcommitted|exceed\w*\s+limits?|pressure\s+limits?|without\s+authorization)\b',
        t
    ))
    
    return has_defensive_action and (has_violation_condition or has_scoped_guard)


def is_defensive_validation(text: str) -> bool:
    """Legacy alias for is_defensive_system_behavior."""
    return is_defensive_system_behavior(text)


def extract_policy_polarity(text: str) -> str:
    """
    Classifies the policy stance of a requirement into:
      - 'PROHIBIT' (explicit policy forbidding an action/feature)
      - 'ALLOW'    (explicit policy allowing an unconstrained action/feature)
      - 'NEUTRAL'  (standard affirmative functional requirement)
    """
    t = text.lower()
    
    # If the sentence is defensive system behavior (e.g. "block invalid input", "prevent incompatible schedules"),
    # it is an affirmative engineering defense, not a policy prohibition against the capability
    if is_defensive_system_behavior(text):
        return 'NEUTRAL'
        
    for p in POLICY_PROHIBITION_PATTERNS:
        if re.search(p, t):
            return 'PROHIBIT'
            
    for p in POLICY_PERMISSION_PATTERNS:
        if re.search(p, t):
            return 'ALLOW'
            
    return 'NEUTRAL'


def detect_negation_polarity(text: str) -> bool:
    """Returns True if the text contains an explicit policy prohibition pattern."""
    return extract_policy_polarity(text) == 'PROHIBIT'


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

    pattern = r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(%|ms|seconds?\b|sec\b|minutes?\b|hours?\b|days?\b|users?\b|concurrent\b|simultaneous\b|books?\b|seats?\b|attempts?\b|items?\b|records?\b)?'
    for m in re.finditer(pattern, t):
        value_str = m.group(1).replace(',', '')
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
    Checks if two texts describe contradictory policies or polarities.
    Returns (True, reason) if polarity conflict is detected, else (False, '').
    
    A polarity conflict requires:
    1. Genuine policy contradiction (ALLOW vs PROHIBIT) on a shared substantive capability.
    2. OR explicit architectural mutual exclusion (e.g. reversible cipher vs one-way hash).
    
    Defensive system behavior (e.g. prevent incompatible vs block unsafe) is NOT a conflict.
    """
    ta = text_a.lower()
    tb = text_b.lower()

    # 1. Defensive system actions (e.g. prevent incompatible vs block unsafe, reject invalid vs block invalid)
    # represent positive implementation alignment, NEVER a polarity conflict
    if is_defensive_system_behavior(text_a) or is_defensive_system_behavior(text_b):
        return False, ""

    # 2. Check explicit mutual exclusion pairs (e.g. reversible vs one-way salted hash)
    for pattern_a, pattern_b, reason in EXCLUSIVE_PAIRS:
        # If pattern_a checks for plaintext/unencrypted, but the text prohibits plaintext, it is NOT an endorsement of plaintext
        if "plaintext" in pattern_a:
            a_in_ta = bool(re.search(pattern_a, ta)) and not bool(re.search(r'\b(?:prohibit|forbidden|must\s+not|shall\s+not)\w*\b', ta))
            a_in_tb = bool(re.search(pattern_a, tb)) and not bool(re.search(r'\b(?:prohibit|forbidden|must\s+not|shall\s+not)\w*\b', tb))
        else:
            a_in_ta = bool(re.search(pattern_a, ta))
            a_in_tb = bool(re.search(pattern_a, tb))

        b_in_tb = bool(re.search(pattern_b, tb))
        b_in_ta = bool(re.search(pattern_b, ta))

        if (a_in_ta and b_in_tb) or (a_in_tb and b_in_ta):
            return True, f"Polarity conflict: {reason}"

    # 3. Check Policy Polarity (ALLOW vs PROHIBIT on shared capability)
    pol_a = extract_policy_polarity(text_a)
    pol_b = extract_policy_polarity(text_b)

    if (pol_a == 'PROHIBIT' and pol_b == 'ALLOW') or (pol_a == 'ALLOW' and pol_b == 'PROHIBIT'):
        stopwords = {
            'this', 'that', 'with', 'from', 'into', 'when', 'then', 'will',
            'shall', 'must', 'should', 'have', 'been', 'only', 'which', 'where',
            'system', 'platform', 'user', 'service', 'may', 'can', 'allow', 'allowed'
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
