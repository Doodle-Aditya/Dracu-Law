import re


def format_results(raw_response: str) -> dict:
    """
    Parses the raw LLM response into a structured dictionary.
    
    Args:
        raw_response: The raw text response from the LLM
    
    Returns:
        A dictionary with keys: risk_score, red_flags, explanation, suggestions
    """
    result = {
        "risk_score": 5,         # Default middle score
        "red_flags": [],
        "explanation": "",
        "suggestions": []
    }

    try:
        # ── Parse Risk Score ──────────────────────────────────────────
        score_match = re.search(r'RISK_SCORE:\s*(\d+)', raw_response, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            result["risk_score"] = max(1, min(10, score))  # Clamp between 1 and 10

        # ── Parse Red Flags ───────────────────────────────────────────
        red_flags_match = re.search(
            r'RED_FLAGS:\s*(.*?)(?=EXPLANATION:|$)',
            raw_response,
            re.DOTALL | re.IGNORECASE
        )
        if red_flags_match:
            flags_text = red_flags_match.group(1).strip()
            if "none found" in flags_text.lower():
                result["red_flags"] = []
            else:
                flags = re.findall(r'-\s(.+)', flags_text)
                result["red_flags"] = [f.strip() for f in flags if f.strip()]

        # ── Parse Explanation ─────────────────────────────────────────
        explanation_match = re.search(
            r'EXPLANATION:\s*(.*?)(?=SUGGESTIONS:|$)',
            raw_response,
            re.DOTALL | re.IGNORECASE
        )
        if explanation_match:
            result["explanation"] = explanation_match.group(1).strip()

        # ── Parse Suggestions ─────────────────────────────────────────
        suggestions_match = re.search(
            r'SUGGESTIONS:\s*(.*?)$',
            raw_response,
            re.DOTALL | re.IGNORECASE
        )
        if suggestions_match:
            suggestions_text = suggestions_match.group(1).strip()
            suggestions = re.findall(r'-\s(.+)', suggestions_text)
            result["suggestions"] = [s.strip() for s in suggestions if s.strip()]

    except Exception as e:
        # If parsing fails, return the raw response in the explanation field
        result["explanation"] = f"Could not fully parse the AI response. Raw output:\n\n{raw_response}"

    return result


def get_risk_label(risk_score: int) -> tuple:
    """
    Returns a human-readable label and color for a given risk score.
    
    Args:
        risk_score: Integer from 1 to 10
    
    Returns:
        Tuple of (label string, color string)
    """
    if risk_score <= 3:
        return "Low Risk ✅", "green"
    elif risk_score <= 6:
        return "Medium Risk ⚠️", "orange"
    else:
        return "High Risk 🚨", "red"