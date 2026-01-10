from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import shutil
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

from app.services.stt import transcribe_audio
from app.services.gemini_llm import get_gemini_response
from app.services.elevenlabs_tts import text_to_speech_elevenlabs

router = APIRouter()

TEMP_DIR = Path("temp")

@router.post("/process-voice")
async def process_voice_v2(
    audio: UploadFile = File(..., description="Audio file from farmer")
):
    '''
    Process farmer's voice query using Gemini and Eleven Labs
    '''
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = TEMP_DIR / f"v2_input_{timestamp}_{audio.filename}"
        
        # Save uploaded audio
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # Step 1: Speech to Text (Whisper) - Auto-detect language
        print(f"[V2] [1/3] Transcribing audio...")
        transcription_result = await transcribe_audio(str(input_path))
        transcription = transcription_result["text"]
        detected_language = transcription_result.get("language", "hi")
        
        print(f"[V2] Transcription: {transcription} (Lang: {detected_language})")
        
        # Step 2: Get LLM response (Gemini)
        print(f"[V2] [2/3] Getting Gemini response...")
        response_text = await get_gemini_response(transcription, detected_language)
        print(f"[V2] Response: {response_text}")
        
        # Step 3: Text to Speech (Eleven Labs)
        print(f"[V2] [3/3] Converting to speech (Eleven Labs)...")
        output_audio_path = await text_to_speech_elevenlabs(response_text)
        
        # Cleanup input file
        input_path.unlink()
        
        # Return audio file with metadata
        return FileResponse(
            output_audio_path,
            media_type="audio/mpeg",
            headers={
                "X-Transcription": quote(transcription[:200], safe=''),
                "X-Response-Text": quote(response_text[:200], safe=''),
                "X-Language": detected_language
            },
            filename=f"v2_response_{timestamp}.mp3"
        )
        
    except Exception as e:
        # Cleanup on error
        if input_path.exists():
            input_path.unlink()
        print(f"Error in v2 pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-gemini")
async def test_gemini(
    query: str = Form(...),
    language: str = Form("hi")
):
    '''Test endpoint for Gemini response'''
    try:
        response = await get_gemini_response(query, language)
        return JSONResponse({
            "query": query,
            "response": response,
            "language": language
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-elevenlabs")
async def test_elevenlabs(
    text: str = Form(...)
):
    '''Test endpoint for Eleven Labs TTS'''
    try:
        output_path = await text_to_speech_elevenlabs(text)
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename="test_elevenlabs.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
