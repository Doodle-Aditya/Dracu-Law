import os
from groq import Groq
from prompts import CONTRACT_ANALYSIS_PROMPT, COMPARISON_PROMPT, REWRITE_PROMPT


def get_client():
    api_key = os.getenv("API")
    if not api_key:
        raise ValueError("Missing GROQ API key")
    return Groq(api_key=api_key)


def run_llm(prompt, model):
    client = get_client()

    res = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a strict legal analyzer. Follow output format exactly."
            },
            {"role":"user","content":prompt}
        ],
        temperature=0,
        max_tokens=2000
    )

    return res.choices[0].message.content.strip()


# ---------- SINGLE ----------
def analyze_contract(text, model):
    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=text[:12000])
    return run_llm(prompt, model)


# ---------- COMPARE ----------
def compare_contracts(text1, text2, model):

    prompt = COMPARISON_PROMPT.format(
        contract1=text1[:8000],
        contract2=text2[:8000]
    )

    return run_llm(prompt, model)


# ---------- REWRITE ----------
def rewrite_contract(text, flags, model):

    joined = "\n".join(flags)

    prompt = REWRITE_PROMPT.format(
        contract=text[:12000],
        clauses=joined
    )

    return run_llm(prompt, model)