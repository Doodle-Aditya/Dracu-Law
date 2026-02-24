import re


def clean_markdown(text: str) -> str:
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"#+ ", "", text)
    text = re.sub(r"`+", "", text)
    return text.strip()


def format_results(raw_response: str) -> dict:

    raw_response = clean_markdown(raw_response)

    result = {
        "risk_score": 5,
        "red_flags": [],
        "explanation": "",
        "suggestions": []
    }

    try:
        # ---------- SCORE ----------
        score = re.search(r'RISK_SCORE[:\- ]+(\d+)', raw_response, re.I)
        if score:
            result["risk_score"] = max(1, min(10, int(score.group(1))))

        # ---------- FLAGS ----------
        flags = re.search(r'RED_FLAGS:(.*?)(EXPLANATION:|$)', raw_response, re.S | re.I)
        if flags:
            result["red_flags"] = re.findall(r'-\s*(.+)', flags.group(1))

        # ---------- SUMMARY ----------
        exp = re.search(r'EXPLANATION:(.*?)(SUGGESTIONS:|$)', raw_response, re.S | re.I)
        if exp:
            result["explanation"] = exp.group(1).strip()

        # ---------- SUGGESTIONS ----------
        sug = re.search(r'SUGGESTIONS:(.*)', raw_response, re.S | re.I)
        if sug:
            result["suggestions"] = re.findall(r'-\s*(.+)', sug.group(1))

    except:
        result["explanation"] = raw_response

    return result


def get_risk_label(score: int):
    if score <= 3:
        return "Low Risk", "green"
    elif score <= 6:
        return "Medium Risk", "orange"
    else:
        return "High Risk", "red"