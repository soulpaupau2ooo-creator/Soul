import io
import os
import asyncio
import logging
import random
from typing import Optional, Tuple
from gtts import gTTS
import google.generativeai as genai
from aiogram import Bot, types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MultimodalHandler")

API_KEYS_STR = os.getenv("GEMINI_API_KEYS", "")
API_KEYS = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]

def get_genai_model():
    if not API_KEYS:
        return None
    key = random.choice(API_KEYS)
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-flash-latest')

async def process_photo_problem(bot: Bot, photo: types.PhotoSize, lang: str = "uz") -> str:
    """Download photo from Telegram and solve the economics problem using Gemini Vision."""
    try:
        file_info = await bot.get_file(photo.file_id)
        if not file_info.file_path:
            return "⚠️ Rasm faylini yuklab olishda xatolik yuz berdi."
            
        file_bytes = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=file_bytes)
        file_bytes.seek(0)
        image_data = file_bytes.read()

        model = get_genai_model()
        if not model:
            return "⚠️ AI kalitlari ulanmagan."

        prompt = (
            f"Sen iqtisodiyot professori va matematika bo'yicha eksportsan. "
            f"Ushbu rasmda iqtisodiyotga oid masala, grafik, jadval yoki nazariy savol keltirilgan. "
            f"1. Rasm ichidagi matn yoki topshiriqni to'liq o'qi (OCR).\n"
            f"2. Masalani bosqichma-bosqich, formulalari va batafsil tushuntirishlari bilan yechib ber.\n"
            f"3. Aniq yakuniy javobni alohida ajratib ko'rsat.\n"
            f"Til: {'O‘zbek tili (Lotin)' if lang == 'uz' else 'Rus tili' if lang == 'ru' else 'Ingliz tili'}."
        )

        image_part = {
            "mime_type": "image/jpeg",
            "data": image_data
        }

        response = await asyncio.to_thread(model.generate_content, [prompt, image_part])
        if response and response.text:
            return response.text
        return "⚠️ Rasm tahlil qilindi, ammo aniq javob shakllantirib bo'lmadi."
        
    except Exception as e:
        logger.error(f"Rasm tahlilida xatolik: {e}")
        return f"⚠️ Rasmni tahlil qilishda texnik xatolik: {e}"

async def process_voice_topic(bot: Bot, voice: types.Voice, lang: str = "uz") -> str:
    """Download voice note and transcribe/process with Gemini multimodal."""
    try:
        file_info = await bot.get_file(voice.file_id)
        if not file_info.file_path:
            return "⚠️ Ovozli xabarni yuklab bo'lmadi."
            
        file_bytes = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=file_bytes)
        file_bytes.seek(0)
        audio_data = file_bytes.read()

        model = get_genai_model()
        if not model:
            return "⚠️ AI kalitlari ulanmagan."

        prompt = (
            f"Ushbu audio xabarni tingla. Foydalanuvchi iqtisodiyotga oid mavzu yoki savol aytmoqda. "
            f"1. Uning aytgan mavzusini aniqlab, matnini keltir.\n"
            f"2. Shu mavzu bo'yicha qisqa, mukammal mustaqil ish tayyorlab ber.\n"
            f"Til: {'O‘zbek tili (Lotin)' if lang == 'uz' else 'Rus tili' if lang == 'ru' else 'Ingliz tili'}."
        )

        audio_part = {
            "mime_type": "audio/ogg",
            "data": audio_data
        }

        response = await asyncio.to_thread(model.generate_content, [prompt, audio_part])
        if response and response.text:
            return response.text
        return "⚠️ Ovozli xabar eshitildi, lekin matn aniqlanmadi."
    except Exception as e:
        logger.error(f"Ovoz tahlilida xatolik: {e}")
        return f"⚠️ Ovozli xabarni qayta ishlashda xatolik: {e}"

def generate_tts_audio(text: str, lang: str = "uz") -> Optional[bytes]:
    """Convert essay text to MP3 audio using gTTS."""
    try:
        # gTTS supports 'tr' (very close for uzbek phonetics if 'uz' not supported, or 'ru')
        tts_lang = 'ru' if lang == 'ru' else 'en' if lang == 'en' else 'tr'
        # Clean text from special characters
        clean_text = text[:800].replace("*", "").replace("_", "").replace("#", "")
        
        tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"TTS audio yaratishda xato: {e}")
        return None
