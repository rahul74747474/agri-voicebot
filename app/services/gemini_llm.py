import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("⚠ GOOGLE_API_KEY not found in .env")

# Create Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Use a valid model name (jo tumhare list me hai)
GEMINI_MODEL_NAME = "models/gemini-flash-latest"

# -------------------------------
# ASYNC WRAPPER FOR FASTAPI
# -------------------------------
async def get_gemini_response(query: str, language_code: str = "hi") -> str:
    try:
        print("🤖 [LLM] Gemini response generation started...")
        print("📝 [LLM] User query:")
        print(query)
        print("--------------------------------------------------")

        language_names = {
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "mr": "Marathi",
            "gu": "Gujarati",
            "pa": "Punjabi",
            "kn": "Kannada",
            "ml": "Malayalam",
        }

        lang_name = language_names.get(language_code, "the user's language")

        if language_code == "hi":
            response_instruction = (
                "Respond in Casual Hinglish (Hindi sentences mixed with English words, "
                "written in Roman script)."
            )
        else:
            response_instruction = f"Respond in {lang_name} language."

        system_prompt = f"""
You are an expert agricultural advisor for Indian farmers.
Your role:
- Answer queries about farming, crops, diseases, etc.
- Be helpful, concise, and practical.
- {response_instruction}
- Keep answer short (under 3-4 sentences) for voice output.
"""

        print("⚙️ [LLM] Using model:", GEMINI_MODEL_NAME)

        # ❌ DO NOT use await here
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=f"{system_prompt}\n\nUser: {query}"
        )

        final_text = response.text.strip()

        print("✅ [LLM] Gemini response received successfully!")
        print("📢 [LLM] FULL RESPONSE:")
        print(final_text)
        print("==================================================")

        return final_text

    except Exception as e:
        print("❌ [LLM] Gemini Error:", e)
        raise Exception(f"Gemini Error: {str(e)}")
