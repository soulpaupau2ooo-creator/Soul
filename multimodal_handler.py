import io
import os
import asyncio
import logging
import random
from typing import Optional, Tuple, List
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
from aiogram import Bot, types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MultimodalHandler")

API_KEYS_STR = os.getenv("GEMINI_API_KEYS", "")
API_KEYS: List[str] = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]

VISION_MODELS = [
    'gemini-2.5-flash',
    'gemini-flash-latest',
    'gemini-2.5-flash-lite'
]

async def _call_gemini_vision(prompt: str, pil_img: Image.Image) -> Optional[str]:
    """Execute vision generation with multi-key rotation and multi-model fallback."""
    if not API_KEYS:
        logger.error("Multimodal error: No API keys configured")
        return None

    shuffled_keys = list(API_KEYS)
    random.shuffle(shuffled_keys)

    for k_idx, current_key in enumerate(shuffled_keys):
        try:
            genai.configure(api_key=current_key)
        except Exception as ce:
            logger.warning(f"Key config error: {ce}")
            continue

        for model_name in VISION_MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, [prompt, pil_img]),
                    timeout=25.0
                )
                if response and response.text:
                    logger.info(f"Vision success with {model_name} (key index {k_idx})")
                    return response.text.strip()
            except Exception as e:
                err_str = str(e).lower()
                logger.warning(f"Vision attempt {model_name} failed: {err_str[:80]}")
                if "429" in err_str or "quota" in err_str or "404" in err_str:
                    continue
                continue

    return None

async def process_photo_problem(bot: Bot, photo: types.PhotoSize, lang: str = "uz") -> str:
    """Download photo from Telegram and solve the economics problem using Gemini Vision."""
    try:
        file_info = await bot.get_file(photo.file_id)
        if not file_info.file_path:
            return "⚠️ Rasm faylini yuklab olishda xatolik yuz berdi."
            
        file_bytes = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=file_bytes)
        file_bytes.seek(0)
        
        pil_img = Image.open(file_bytes)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        prompt = (
            f"Sen oliy toifali iqtisodiyot professori va matematika bo'yicha eksportsan. "
            f"Ushbu rasmda iqtisodiyotga oid masala, grafik, jadval yoki nazariy savol keltirilgan.\n"
            f"1. Rasm ichidagi masala shartini diqqat bilan o'qi.\n"
            f"2. Masalani bosqichma-bosqich, zarur formulalari va qisqa lo'nda tushuntirishlari bilan yechib ber.\n"
            f"3. Yakuniy javobni aniq qilib ko'rsat.\n"
            f"Til: {'O‘zbek tili (Lotin)' if lang == 'uz' else 'Rus tili' if lang == 'ru' else 'Ingliz tili'}."
        )

        result = await _call_gemini_vision(prompt, pil_img)
        if result:
            return result
        return "⚠️ Rasm tahlil qilindi, ammo javob shakllantirib bo'lmadi. Iltimos, masalani matn ko'rinishida yozib yuboring."
        
    except Exception as e:
        logger.error(f"Rasm tahlilida xatolik: {e}")
        return f"⚠️ Rasmni tahlil qilishda texnik xatolik: {e}"

async def extract_topic_from_photo(bot: Bot, photo: types.PhotoSize, subject_title: str = "Iqtisodiyot", lang: str = "uz") -> str:
    """Download photo from Telegram and extract the essay topic/title using Gemini Vision OCR."""
    try:
        file_info = await bot.get_file(photo.file_id)
        if not file_info.file_path:
            logger.error("Could not obtain file path for photo")
            return ""
            
        file_bytes = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=file_bytes)
        file_bytes.seek(0)
        
        pil_img = Image.open(file_bytes)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        prompt = (
            f"Sen akademik OCR va sun'iy intellekt tahlilchisisan. "
            f"Talaba '{subject_title}' fani bo'yicha mustaqil ish yozish uchun rasm yubordi. "
            f"Bu rasmda daftar, kitob mundarijasi, sillabus, slayd yoki ekrandagi mavzular ro'yxati ko'rsatilgan.\n\n"
            f"Topshiriq: Rasm ichidagi eng asosiy mustaqil ish MAVZUSI yoki bo'lim sarlavhasini aniqlab ber.\n"
            f"Qat'iy qoidalar:\n"
            f"1. Faqat mavzuning toza sarlavhasini qaytar (bitta qisqa satr).\n"
            f"2. Hech qanday kirish so'z, 'Mavzu:', salomlashish yoki tushuntirish yozma!\n"
            f"3. Yulduzcha (*), panjara (#), qo'shtirnoq ishlatma.\n"
            f"4. Til: {'O‘zbek tili (Lotin)' if lang == 'uz' else 'Русский язык' if lang == 'ru' else 'English'}."
        )

        result = await _call_gemini_vision(prompt, pil_img)
        if result:
            lines = [l.strip() for l in result.split("\n") if l.strip()]
            for line in lines:
                cleaned = line.replace("*", "").replace("#", "").replace('"', '').replace("'", "")
                if cleaned.lower().startswith("mavzu:"):
                    cleaned = cleaned[6:].strip()
                if cleaned.lower().startswith("sarlavha:"):
                    cleaned = cleaned[9:].strip()
                if len(cleaned) > 3:
                    return cleaned
            return result.replace("*", "").replace("#", "").strip()
        return ""
    except Exception as e:
        logger.error(f"Error extracting topic from photo: {e}")
        return ""

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

        if not API_KEYS:
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

        shuffled = list(API_KEYS)
        random.shuffle(shuffled)
        for key in shuffled:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-flash-latest')
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, [prompt, audio_part]),
                    timeout=25.0
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.warning(f"Voice processing error: {e}")
                continue

        return "⚠️ Ovozli xabarni qayta ishlashda xatolik yuz berdi. Iltimos, matn ko'rinishida yozing."
    except Exception as e:
        logger.error(f"Ovoz tahlilida xatolik: {e}")
        return f"⚠️ Ovozli xabarni qayta ishlashda xatolik: {e}"

def generate_tts_audio(text: str, lang: str = "uz") -> Optional[bytes]:
    """Convert essay text to MP3 audio using gTTS."""
    try:
        tts_lang = 'ru' if lang == 'ru' else 'en' if lang == 'en' else 'tr'
        clean_text = text[:800].replace("*", "").replace("_", "").replace("#", "")
        
        tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"TTS audio yaratishda xato: {e}")
        return None
