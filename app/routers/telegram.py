from fastapi import APIRouter, Request, BackgroundTasks
import requests
import os

from app.services.stt import transcribe_audio
from app.services.gemini_llm import get_gemini_response
from app.services.elevenlabs_tts import text_to_speech_elevenlabs

router = APIRouter()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

processed_updates = set()   # 🛡 duplicate guard

@router.post("/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print("Incoming Telegram Update:", data)

    # 🛑 Ignore non-message updates
    if "message" not in data:
        return {"status": "ignored"}

    update_id = data.get("update_id")
    if update_id in processed_updates:
        print("⚠ Duplicate update ignored:", update_id)
        return {"status": "duplicate"}
    processed_updates.add(update_id)

    # ⚡ Immediately acknowledge Telegram
    background_tasks.add_task(process_update, data)
    return {"status": "ok"}   # <-- THIS STOPS RE-SENDING


# ================= BACKGROUND WORK =================

def process_update(data):
    try:
        chat_id = data["message"]["chat"]["id"]

        # 📝 Text Message
        if "text" in data["message"]:
            reply = "🎙 Please send a voice message. I will reply in voice."
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            })
            return

        # 🎧 Voice Message
        if "voice" in data["message"]:
            file_id = data["message"]["voice"]["file_id"]

            # 1️⃣ Get file path
            file_info = requests.get(
                f"{BASE_URL}/getFile?file_id={file_id}"
            ).json()

            if not file_info.get("ok"):
                print("Telegram getFile Error:", file_info)
                requests.post(f"{BASE_URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "❌ Audio file process nahi ho paayi. Please dubara bhejein."
                })
                return

            file_path = file_info["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

            # 2️⃣ Download audio
            os.makedirs("temp", exist_ok=True)
            local_audio = "temp/telegram_input.ogg"
            with open(local_audio, "wb") as f:
                f.write(requests.get(file_url).content)

            # 3️⃣ Speech → Text
            result = transcribe_audio_sync(local_audio)
            user_text = result["text"]
            lang = result.get("language", "hi")

            # 4️⃣ Gemini Response
            reply_text = get_gemini_response_sync(user_text, lang)

            # 5️⃣ Text → Speech
            output_audio = text_to_speech_elevenlabs_sync(reply_text)

            # 6️⃣ Send voice back
            with open(output_audio, "rb") as audio:
                requests.post(
                    f"{BASE_URL}/sendVoice",
                    data={"chat_id": chat_id},
                    files={"voice": audio}
                )

    except Exception as e:
        print("❌ Error in background task:", e)


# ================= SYNC WRAPPERS =================
# (kyunki background task normal function hota hai)

def transcribe_audio_sync(path):
    import asyncio
    return asyncio.run(transcribe_audio(path))

def get_gemini_response_sync(text, lang):
    import asyncio
    return asyncio.run(get_gemini_response(text, lang))

def text_to_speech_elevenlabs_sync(text):
    import asyncio
    return asyncio.run(text_to_speech_elevenlabs(text))
