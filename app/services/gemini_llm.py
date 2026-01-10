import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in .env")

genai.configure(api_key=GOOGLE_API_KEY)

# Use Gemini Flash 2.5 (using "gemini-1.5-flash" as proxy if 2.5 is preview or use "gemini-1.5-pro-latest" etc. 
# User asked for "gemini flash 2.5", usually "gemini-1.5-flash" is the current flash model. 
# There's no public "2.5" yet, usually it's 1.5. I'll use "gemini-1.5-flash" or "gemini-2.0-flash-exp" if available.
# Safest bet is "gemini-1.5-flash" which is very fast. Or "gemini-2.0-flash-exp" if the user insists on latest.
# Given the prompt, I'll stick to "gemini-1.5-flash" widely available or check if 2.0 is expected.
# Actually, Google recently released Gemini 2.0 Flash Experimental. I will try to use the model name provided or a standard one.
# User said "gemini flash 2.5". I suspect they mean 1.5 or 2.0. I will use "gemini-1.5-flash" as a stable fallback or "gemini-2.0-flash-exp".
# Let's use "gemini-1.5-flash" for reliability unless I see docs.
# I will define it as a variable.

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
        
        # Special case for Hindi -> Casual Hinglish
        if language_code == "hi":
            response_instruction = "Respond in Casual Hinglish (blend of Hindi and English, written in Devanagari or Latin script as appropriate for casual conversation, but preferably Devanagari for readability if standard, or Latin if very casual. The user asked for 'Casual Hinglish'). Let's use Latin script (Hinglish) or Devanagari mixed? User said 'Casual Hinglish'. usually implies Latin or mixed. I will instruct for 'Casual Hinglish using Roman/Latin characters mixed with English phrases'."
            # Re-reading user request: "casual hinglish instead of casual hindi".
            # Usually Hinglish is written in Roman script. e.g. "AAP kaise hain?"
            # But text-to-speech might handle Devanagari better if the TTS engine expects it.
            # ElevenLabs is good.
            # Let's aim for a natural Hinglish.
            response_instruction = "Respond in Casual Hinglish. Use a mix of Hindi and English words. You can use Roman script or Devanagari, but Roman script is often what 'Hinglish' implies. HOWEVER, for TTS, Devanagari is often better for pronunciation if the TTS is Hindi-optimized. BUT ElevenLabs is multilingual. Let's ask for 'Casual Hinglish (Hindi written in Roman script mixed with English)'?"
            # Wait, if I send Roman script "Aap kaise ho" to a TTS, it might be read as English.
            # ElevenLabs multilingual model usually detects language.
            # If I want Hindi pronunciation, Devanagari is safer: "आप कैसे हो (Aap kaise ho)".
            # Let's try to output in Devanagari script but using Hinglish vocabulary (English words written in Hindi).
            # OR, user might want Roman script.
            # "Casual Hinglish" usually means "Romanized Hindi".
            # Let's stick to Roman script as it's the standard definition of Hinglish, and test if TTS handles it.
            # Actually, for a voice bot, pronunciation is key.
            # If I strictly use Roman script, ElevenLabs might read it with an English accent.
            # Let's prompt for "Hindi with English words (Hinglish style) written in Devanagari script" for better TTS?
            # User said "casual hinglish instead of casual hindi".
            # Let's provide Romanized Hinglish as it is distinct.
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

        # Try to find a valid model if default fails or usage error
        model_candidates = [
            "gemini-2.5-flash", # User requested
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
                print(f"Attempting to use model: {model_name}")
                model = genai.GenerativeModel(model_name, system_instruction=system_prompt)
                response = await model.generate_content_async(query)
                return response.text.strip()
            except Exception as e:
                print(f"Failed with {model_name}: {e}")
                last_error = e
                continue
        
        # If all fail, list models to debug
        print("All candidates failed. Listing available models:")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"- {m.name}")
        except:
            pass
            
        raise last_error
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        raise Exception(f"Gemini Error: {str(e)}")
