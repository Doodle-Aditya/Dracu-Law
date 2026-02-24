CONTRACT_ANALYSIS_PROMPT = """
You are a legal contract analyst.

Analyze this contract and return ONLY the following format.
DO NOT add markdown.
DO NOT add explanations.
DO NOT add headings.
DO NOT use ** or symbols.

CONTRACT:
{contract_text}

FORMAT:

RISK_SCORE: number

RED_FLAGS:
- text
- text

EXPLANATION:
text

SUGGESTIONS:
- text
- text
"""
# --------------------------
COMPARISON_PROMPT = """
Compare these two contracts and decide which is better for the signer.

CONTRACT 1:
{contract1}

CONTRACT 2:
{contract2}

Return plain text only:

WINNER: Contract 1 or Contract 2

REASON:
short explanation

KEY DIFFERENCES:
- point
- point
"""

# --------------------------
REWRITE_PROMPT = """
Rewrite the contract below removing or improving these clauses:

CLAUSES TO FIX:
{clauses}

CONTRACT:
{contract}

Return ONLY the improved contract text.
No markdown.
No commentary.
"""