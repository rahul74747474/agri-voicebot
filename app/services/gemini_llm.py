import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in .env")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Gemini Model Configuration
# We prioritize Gemini 1.5 Flash for speed and cost-efficiency.
# The list includes fallbacks to ensure reliability.
GEMINI_MODEL_NAME = "gemini-1.5-flash" 

async def get_gemini_response(query: str, language_code: str = "hi") -> str:
    '''
    Get LLM response using Gemini
    
    Args:
        query: User query
        language_code: Detected language code
    
    Returns:
        Response text
    '''
    try:
        # Language map for prompt
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
        
        # Determine response style based on language
        if language_code == "hi":
            # Special handling for Hindi: Use "Casual Hinglish" (Romanized Hindi mixed with English)
            # This provides a more natural, conversational tone for voice interactions.
            response_instruction = "Respond in Casual Hinglish (Hindi sentences mixed with English words, written in Roman script)."
        else:
            response_instruction = f"Respond in {lang_name} language."

        system_prompt = f'''You are an expert agricultural advisor for Indian farmers.
Your role:
- Answer queries about farming, crops, diseases, etc.
- Be helpful, concise, and practical.
- {response_instruction}
- Keep answer short (under 3-4 sentences) for voice output.
'''

        # Model Candidate List
        # We attempt to connect to the most appropriate available model.
        model_candidates = [
            "gemini-2.5-flash", 
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-2.0-flash-exp",
            "models/gemini-1.5-flash",
            "models/gemini-2.5-flash",
        ]

        model = None
        last_error = None
        
        for model_name in model_candidates:
            try:
                # print(f"Connecting to model: {model_name}") 
                model = genai.GenerativeModel(model_name, system_instruction=system_prompt)
                response = await model.generate_content_async(query)
                return response.text.strip()
            except Exception as e:
                # Silently fail and try next candidate, log if needed
                # print(f"Model {model_name} unavailable, trying next...")
                last_error = e
                continue
        
        # If all candidates fail, log available models for debugging
        print("Error: All model candidates failed to respond.")
        try:
            print("Available models:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"- {m.name}")
        except:
            pass
            
        raise last_error
            
        raise last_error
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        raise Exception(f"Gemini Error: {str(e)}")
