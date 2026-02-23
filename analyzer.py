import os
from groq import Groq
from prompts import CONTRACT_ANALYSIS_PROMPT

# ── You can swap this to Gemini or Mistral easily ──
# Just change the client and model name below

def get_client():
    """Initialize and return the LLM client."""
    api_key = os.getenv("API")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file or environment variables.")
    return Groq(api_key=api_key)


def run_llm_analysis(contract_text: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Sends the contract text to the LLM and returns the raw response.
    
    Args:
        contract_text: The extracted text from the PDF
        model: The LLM model to use (default: llama3-8b-8192 via Groq)
    
    Returns:
        Raw string response from the LLM
    """
    client = get_client()


    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=contract_text[:12000])  

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful legal contract analyst. Always respond in the exact format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  
            max_tokens=2000,
        )

        return response.choices[0].message.content

    except Exception as e:
        raise ConnectionError(f"LLM API call failed: {str(e)}")


def analyze_contract(contract_text: str, model: str = "llama3-8b-8192") -> str:
    """
    Main orchestrator function. Validates input and calls the LLM.
    
    Args:
        contract_text: Clean extracted text from PDF
        model: LLM model name
    
    Returns:
        Raw LLM response string
    """
    if not contract_text or len(contract_text.strip()) < 50:
        raise ValueError("The extracted text is too short. The PDF may be empty or unreadable.")

    raw_response = run_llm_analysis(contract_text, model)
    return raw_response


# ── OPTIONAL: Switch to Gemini instead of Groq ──
# Uncomment this block and comment out the Groq section above

# import google.generativeai as genai
#
# def analyze_contract_gemini(contract_text: str) -> str:
#     genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
#     model = genai.GenerativeModel("gemini-pro")
#     prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=contract_text[:12000])
#     response = model.generate_content(prompt)
#     return response.text