import whisper
import torch
import os
from dotenv import load_dotenv

load_dotenv()

# Load Whisper model once at startup
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"🎙️ [STT] Loading Whisper model: {WHISPER_MODEL_NAME} on {device}")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=device)
print("✅ [STT] Whisper model loaded successfully")

async def transcribe_audio(audio_path: str, language: str = None) -> dict:
    '''
    Transcribe audio file to text using Whisper
    '''
    try:
        print("🎧 [STT] Transcription process started...")
        print("📂 [STT] Audio file:", audio_path)

        # Map language codes to Whisper format
        language_map = {
            "hi": "hi",  # Hindi
            "ta": "ta",  # Tamil
            "te": "te",  # Telugu
            "bn": "bn",  # Bengali
            "mr": "mr",  # Marathi
            "gu": "gu",  # Gujarati
            "pa": "pa",  # Punjabi
            "kn": "kn",  # Kannada
            "ml": "ml",  # Malayalam
        }

        whisper_lang = language_map.get(language, language) if language else None

        if whisper_lang:
            print(f"🌍 [STT] Forcing language: {whisper_lang}")
        else:
            print("🌍 [STT] Auto language detection enabled")

        # Transcribe
        result = whisper_model.transcribe(
            audio_path,
            language=whisper_lang,
            fp16=torch.cuda.is_available()
        )

        text = result["text"].strip()
        detected_lang = result.get("language", "unknown")

        print("✅ [STT] Transcription completed successfully!")
        print(f"🗣️ [STT] Detected language: {detected_lang}")
        print("📢 [STT] FULL TRANSCRIBED TEXT:")
        print(text)
        print("==================================================")

        return {
            "text": text,
            "language": detected_lang
        }

    except Exception as e:
        print("❌ [STT] Transcription Error:", e)
        raise Exception(f"Transcription error: {str(e)}")
