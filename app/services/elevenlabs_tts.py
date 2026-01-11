import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pathlib import Path
from datetime import datetime

load_dotenv()

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
TEMP_DIR = Path("temp")

if not ELEVEN_LABS_API_KEY:
    print("⚠ Warning: ELEVEN_LABS_API_KEY not found in .env")

client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)

async def text_to_speech_elevenlabs(text: str) -> str:
    '''
    Convert text to speech using Eleven Labs
    '''
    try:
        print("🔊 [TTS] Text-to-Speech process started...")
        print("📝 [TTS] Input text preview:", text[:80], "...")

        # Ensure temp folder exists
        TEMP_DIR.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = TEMP_DIR / f"eleven_{timestamp}.mp3"

        print("📁 [TTS] Output file:", output_path)

        # Audio generation
        print("⚙️ [TTS] Sending request to ElevenLabs API...")
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2"
        )

        print("🎧 [TTS] Audio stream received. Writing to file...")

        # Save to file
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        print("✅ [TTS] Audio generation completed successfully!")
        return str(output_path)

    except Exception as e:
        print("❌ [TTS] ElevenLabs Error:", e)
        raise Exception(f"ElevenLabs Error: {str(e)}")
