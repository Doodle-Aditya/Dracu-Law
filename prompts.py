CONTRACT_ANALYSIS_PROMPT = """
You are an expert legal contract analyst. Analyze the following contract text carefully and return your analysis in the EXACT format below. Do not deviate from this format.

CONTRACT TEXT:
{contract_text}

Return your response in this exact format:

RISK_SCORE: [a number from 1 to 10, where 1 is very safe and 10 is very risky]

RED_FLAGS:
- [red flag 1]
- [red flag 2]
- [red flag 3]
(list as many as you find, or write "None found" if there are no red flags)

EXPLANATION:
[Write 3-5 sentences explaining the contract in simple, plain English. Avoid legal jargon. Explain what the contract is about, what the main obligations are, and any important things the signer should know.]

SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
- [suggestion 3]
(list 3-5 actionable suggestions for the person before signing)

Important: Be thorough but concise. Focus on protecting the interests of the person signing the contract.
"""