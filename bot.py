import asyncio
import logging
import os
import sys
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError
import google.generativeai as genai
from dotenv import load_dotenv

from database import db

# ==============================================================================
# 🛠️ KONFIGURATSIYA VA YADRO (FATHER MODE v6.0)
# ==============================================================================
load_dotenv()
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
API_KEYS_STR: str = os.getenv("GEMINI_API_KEYS", "")
API_KEYS: List[str] = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]

if not BOT_TOKEN:
    raise ValueError("CRITICAL ERROR: BOT_TOKEN is missing in environment variables.")

dp = Dispatcher()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

class GenerateState(StatesGroup):
    waiting_for_custom_topic = State()
    waiting_for_subject = State()

# ==============================================================================
# 📚 MA'LUMOTLAR BAZASI (KNOWLEDGE BASE)
# ==============================================================================
knowledge_base: Dict[str, Dict[str, Any]] = {
    "makro": {"title": "Makroiqtisodiyot", "topics": ["Yalpi ichki mahsulot va uni hisoblash", "Inflyatsiya va ishsizlik muammolari", "Davlat byudjeti va soliq siyosati", "Makroiqtisodiy beqarorlik"]},
    "mikro": {"title": "Mikroiqtisodiyot", "topics": ["Talab va taklif qonuniyati", "Iste'molchi xulq-atvori", "Ishlab chiqarish xarajatlari", "Raqobat va monopoliya"]},
    "nazariy_boshqa": {"title": "Iqtisodiy ta'limotlar tarixi / Institutsional", "topics": ["Klassik iqtisodiy maktablar", "Keynschilik nazariyasi", "Institutsional iqtisodiyot asoslari"]},
    "moliya": {"title": "Moliya", "topics": ["Davlat moliyasi", "Korxonalar moliyasi", "Moliya bozorlari", "Xalqaro moliya tizimi"]},
    "buxgalteriya": {"title": "Buxgalteriya hisobi", "topics": ["Buxgalteriya balansi", "Aktivlar va passivlar", "Asosiy vositalar hisobi"]},
    "soliq": {"title": "Soliq va soliqqa tortish", "topics": ["Soliq tizimi mohiyati", "To'g'ridan-to'g'ri va egri soliqlar", "Soliq siyosatining iqtisodiyotdagi o'rni"]},
    "marketing": {"title": "Marketing", "topics": ["Marketing majmuasi (4P)", "Bozor segmentatsiyasi", "Raqamli marketing"]},
    "menejment": {"title": "Menejment (Boshqaruv)", "topics": ["Menejment funksiyalari va usullari", "Strategik menejment", "Kadrlar (HR) menejmenti"]},
    "tadbirkorlik": {"title": "Kichik biznes va tadbirkorlik", "topics": ["Tadbirkorlik faoliyatini tashkil etish", "Biznes reja tuzish asoslari", "Kichik biznesni moliyalashtirish", "O'zbekistonda tadbirkorlik muhiti"]},
    "mintaqaviy": {"title": "Mintaqaviy iqtisodiyot", "topics": ["Hududlarni ijtimoiy-iqtisodiy rivojlantirish", "Mintaqaviy investitsiya jozibadorligi", "Namangan viloyati iqtisodiy salohiyati", "Erkin iqtisodiy zonalar faoliyati"]},
    "qishloq": {"title": "Qishloq xo'jaligi iqtisodiyoti", "topics": ["Agrar soha iqtisodiyoti", "Fermer xo'jaliklarini rivojlantirish", "Qishloq xo'jaligida kooperatsiya", "Oziq-ovqat xavfsizligi"]},
    "turizm": {"title": "Turizm iqtisodiyoti", "topics": ["Turizm xizmatlari bozori", "Ekoturizm va ziyorat turizmi", "Mehmonxona biznesi iqtisodiyoti"]},
    "sanoat": {"title": "Sanoat iqtisodiyoti", "topics": ["Sanoat korxonalarida ishlab chiqarishni tashkil etish", "Sanoatda mehnat unumdorligi", "Mahsulot tannarxi va raqobatbardoshligi"]},
    "muhandislik": {"title": "Muhandislik iqtisodiyoti", "topics": ["Muhandislik loyihalarini moliyalashtirish", "Yangi texnologiyalarni joriy etishning iqtisodiy samaradorligi", "Resurslardan oqilona foydalanish"]},
    "logistika": {"title": "Transport va Logistika iqtisodiyoti", "topics": ["Logistika tizimlari va ularni boshqarish", "Transport xarajatlarini optimallashtirish", "Xalqaro yuk tashish iqtisodiyoti"]},
    "innovatsiya": {"title": "Innovatsion iqtisodiyot", "topics": ["Startap loyihalar iqtisodiyoti", "Texnoparklar va innovatsion zonalar", "Raqamli iqtisodiyot va sun'iy intellekt"]},
    "xalqaro": {"title": "Xalqaro Iqtisodiyot", "topics": ["Xalqaro savdo nazariyalari", "Transmilliy korporatsiyalar", "Jahon savdo tashkiloti (JST) va O'zbekiston"]}
}

categories: Dict[str, Dict[str, Any]] = {
    "nazariy": {"title": "📚 Nazariy iqtisodiyot", "subjects": {"makro": "Makroiqtisodiyot", "mikro": "Mikroiqtisodiyot", "nazariy_boshqa": "Iqtisodiy ta'limotlar"}},
    "moliya": {"title": "💰 Moliya, Hisob va Soliq", "subjects": {"moliya": "Moliya", "buxgalteriya": "Buxgalteriya hisobi", "soliq": "Soliq va soliqqa tortish"}},
    "amaliy": {"title": "🏢 Tadbirkorlik, Menejment", "subjects": {"marketing": "Marketing", "menejment": "Menejment", "tadbirkorlik": "Kichik biznes va tadbirkorlik"}},
    "hududiy": {"title": "🌾 Mintaqaviy iqtisodiyot (NamDU)", "subjects": {"mintaqaviy": "Mintaqaviy iqtisodiyot", "qishloq": "Qishloq xo'jaligi iqtisodiyoti", "turizm": "Turizm iqtisodiyoti"}},
    "texnologik": {"title": "⚙️ Sanoat, Texnologiya, Muhandislik (NamDTU)", "subjects": {"sanoat": "Sanoat iqtisodiyoti", "muhandislik": "Muhandislik iqtisodiyoti", "logistika": "Transport va Logistika iqtisodiyoti", "innovatsiya": "Innovatsion iqtisodiyot"}},
    "xalqaro": {"title": "🌍 Xalqaro Iqtisodiyot", "subjects": {"xalqaro": "Xalqaro Iqtisodiyot"}}
}

# ==============================================================================
# 🖥️ FOYDALANUVCHI INTERFEYSI (UI)
# ==============================================================================
def get_main_reply_menu() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="📚 Mustaqil ish yozish")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Quyidagi tugmani bosing...")

def get_back_reply_menu() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="⬅️ Orqaga")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Asosiy menyuga qaytish...")

def get_main_menu() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=cat_data["title"], callback_data=f"cat_{cat_id}")] for cat_id, cat_data in categories.items()]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_subjects_menu(cat_id: str) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=subj_title, callback_data=f"subj_{subj_id}")] for subj_id, subj_title in categories[cat_id]["subjects"].items()]
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_topics_menu(subj_id: str) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=f"{i+1}. {topic}", callback_data=f"topic_{subj_id}_{i}")] for i, topic in enumerate(knowledge_base[subj_id]["topics"])]
    kb.append([InlineKeyboardButton(text="✍️ O'zim mavzu kiritaman", callback_data=f"custom_{subj_id}")])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==============================================================================
# 🌐 RENDER.COM VA CRON-JOB.ORG KEEP-ALIVE WEB SERVER (/health)
# ==============================================================================
async def health_check_handler(request: web.Request) -> web.Response:
    stats = await db.get_stats()
    return web.json_response({
        "status": "ok",
        "service": "Soulbekbot 24/7 Hosting",
        "database": "MongoDB Atlas" if db.is_connected else "Local JSON Fallback",
        "total_users": stats.get("users", 0),
        "total_requests": stats.get("requests", 0),
        "server_time": datetime.now().isoformat()
    })

async def root_handler(request: web.Request) -> web.Response:
    return web.Response(
        text="🤖 Soulbekbot 24/7 Cloud Hosting da faol ishlamoqda!\nKeep-alive health endpoint: /health",
        content_type="text/plain; charset=utf-8"
    )

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_check_handler)
    
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Keep-Alive Web Server 0.0.0.0:{port} portida ishga tushdi (/health tayyor)")
    return runner

# ==============================================================================
# 🤖 YUKORI DARAJADAGI AI VA QAYTA URINISH MANTIG'I (RESILIENCE)
# ==============================================================================
async def request_ai_content(prompt: str) -> str:
    """Asynchronous AI request with robust round-robin API Key rotation and exponential backoff."""
    if not API_KEYS:
        raise ValueError("AI API KEYS REQUIRED")
        
    shuffled_keys = list(API_KEYS)
    random.shuffle(shuffled_keys)
    
    last_exception: Optional[Exception] = None
    
    for attempt, current_key in enumerate(shuffled_keys):
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            if not response or not response.text:
                raise ValueError("Bosh javob olindi.")
                
            return response.text
            
        except Exception as e:
            last_exception = e
            error_str = str(e).lower()
            logger.warning(f"AI Error on attempt {attempt+1}: {error_str}")
            
            if "429" in error_str or "quota" in error_str:
                if attempt < len(shuffled_keys) - 1:
                    await asyncio.sleep(2)
                    continue
            
    if last_exception:
        raise last_exception
    return "Xatolik."

async def generate_essay(message: types.Message, subject: str, topic: str) -> None:
    if not API_KEYS:
        await message.answer("⚠️ Kechirasiz, botning Sun'iy Intelekt qismi (Brain) ulanmagan. Iltimos, ma'muriyatga xabar bering.")
        return
        
    wait_msg = await message.answer(f"⏳ *{subject}* fani bo'yicha *\"{topic}\"* mavzusida mukammal va qisqa mustaqil ish tayyorlanmoqda...\n\n_Iltimos, ozroq kuting..._", parse_mode="Markdown")
    
    prompt = (
        f"Sen iqtisodiyot professori rolidasan. "
        f"Menga {subject} fani bo'yicha '{topic}' mavzusida qisqa, lo'nda va juda ma'noli mustaqil ish yozib ber. "
        f"Qoidalar:\n"
        f"1. Til: O'zbek tili (lotin yozuvida).\n"
        f"2. Matn hajmi qisqa bo'lsin (taxminan 1000-1500 belgi), ortiqcha suv gaplarsiz, faqat eng muhim faktlar va mohiyat ochib berilsin.\n"
        f"3. Tuzilishi: Qisqacha kirish, 1-2 ta eng asosiy fikr/tahlil va aniq xulosa.\n"
        f"4. MUHIM: Hech qanday maxsus belgilarsiz (yulduzcha *, tagchiziq _ va qalin harflar) mutlaqo oddiy matn ko'rinishida yozing, chunki Telegram qabul qilolmaydi."
    )
    
    try:
        text = await request_ai_content(prompt)
        
        # Log to Database
        if message.from_user:
            await db.log_request(
                user_id=message.from_user.id,
                subject=subject,
                topic=topic
            )
        
        # Safe Telegram message sending (max 4096 chars per message)
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(text)
            
        await wait_msg.delete()
        
    except ValueError as ve:
        await wait_msg.edit_text("⚠️ Kechirasiz, AI ulanishida uzilish yuz berdi. Iltimos, kalitlarni tekshiring.")
        logger.error(f"Value Error: {ve}")
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str:
            await wait_msg.edit_text("⏳ Uzr, ayni vaqtda botdan juda ko'p foydalanilayotgani sababli barcha serverlar band bo'lib qoldi.\n\nIltimos, 1 daqiqadan so'ng qayta urinib ko'ring.")
        else:
            await wait_msg.edit_text("⚠️ Kechirasiz, matnni tayyorlashda texnik xatolik yuz berdi.\n\nIltimos, boshqa mavzu tanlab ko'ring.")
        logger.error(f"Unhandled Exception: {e}")

# ==============================================================================
# 🎮 XABARLAR YUKLATGICHI (HANDLERS)
# ==============================================================================
@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    
    # Save user to DB (MongoDB Atlas or JSON)
    if message.from_user:
        await db.add_or_update_user(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
        
    text = (
        f"Assalomu alaykum, {message.from_user.full_name}!\n\n"
        "O'zbekistondagi nufuzli OTMlar o'quv dasturi asosidagi **Mustaqil ish yaratuvchi bot**ga xush kelibsiz!\n\n"
        "Boshlash uchun pastdagi **\"📚 Mustaqil ish yozish\"** tugmasini bosing:"
    )
    try:
        await message.answer(text, reply_markup=get_main_reply_menu(), parse_mode="Markdown")
    except TelegramAPIError as e:
        logger.error(f"Failed to send start message: {e}")

@dp.message(Command("stats"))
async def stats_command_handler(message: types.Message) -> None:
    stats = await db.get_stats()
    db_type = "MongoDB Atlas (Bulut)" if db.is_connected else "Mahalliy Zaxira (JSON)"
    text = (
        f"📊 *Bot statistikasi:*\n\n"
        f"👥 Foydalanuvchilar: *{stats.get('users', 0)}* ta\n"
        f"📝 Tayyorlangan mustaqil ishlar: *{stats.get('requests', 0)}* ta\n"
        f"🗄 Ma'lumotlar bazasi: *{db_type}*\n"
        f"🌐 Keep-Alive Server: *Faol (/health)*"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "⬅️ Orqaga")
async def main_menu_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🏠 Asosiy menyudasiz. Boshlash uchun quyidagi tugmani bosing:", reply_markup=get_main_reply_menu())

@dp.message(F.text == "📚 Mustaqil ish yozish")
async def btn_mustaqil_ish_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    # Change bottom menu to 'Back'
    await message.answer("Bo'lim ochilmoqda...", reply_markup=get_back_reply_menu())
    # Display Inline menu
    text = "Ajoyib! Endi o'zingizga kerakli Iqtisodiyot yo'nalishini tanlang:"
    await message.answer(text, reply_markup=get_main_menu())

@dp.callback_query(F.data == "back_to_main")
async def back_main_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.edit_text("Yo'nalishni tanlang:", reply_markup=get_main_menu())
        await callback.answer()
    except TelegramAPIError:
        pass

@dp.callback_query(F.data.startswith("cat_"))
async def category_handler(callback: types.CallbackQuery) -> None:
    cat_id = callback.data.split("_")[1]
    if cat_id in categories:
        text = f"*{categories[cat_id]['title']}* yo'nalishidagi fanlar:\nQaysi fan bo'yicha mustaqil ish yozamiz?"
        try:
            await callback.message.edit_text(text, reply_markup=get_subjects_menu(cat_id), parse_mode="Markdown")
            await callback.answer()
        except TelegramAPIError:
            pass

@dp.callback_query(F.data.startswith("subj_"))
async def subject_handler(callback: types.CallbackQuery) -> None:
    subj_id = callback.data.split("_")[1]
    if subj_id in knowledge_base:
        title = knowledge_base[subj_id]["title"]
        text = f"*{title}* fani bo'yicha tayyor mavzuni tanlang yoki o'zingiz kiritishingiz mumkin:"
        try:
            await callback.message.edit_text(text, reply_markup=get_topics_menu(subj_id), parse_mode="Markdown")
            await callback.answer()
        except TelegramAPIError:
            pass

@dp.callback_query(F.data.startswith("custom_"))
async def custom_topic_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    subj_id = callback.data.split("_")[1]
    subj_title = knowledge_base[subj_id]["title"]
    
    await state.update_data(subject_title=subj_title)
    await state.set_state(GenerateState.waiting_for_custom_topic)
    
    try:
        await callback.message.edit_text(f"Yaxshi! *{subj_title}* fani bo'yicha o'z mavzusingizni matn qilib yozib yuboring:", parse_mode="Markdown")
        await callback.answer()
    except TelegramAPIError:
        pass

@dp.message(GenerateState.waiting_for_custom_topic)
async def custom_topic_message_handler(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    subj_title = data.get("subject_title", "Tanlanmagan fan")
    topic = message.text
    if not topic:
        await message.answer("Iltimos, mavzuni matn ko'rinishida kiriting.")
        return
        
    await state.clear()
    await generate_essay(message, subj_title, topic)

@dp.callback_query(F.data.startswith("topic_"))
async def predefined_topic_handler(callback: types.CallbackQuery) -> None:
    parts = callback.data.split("_")
    subj_id = parts[1]
    topic_index = int(parts[2])
    
    subj_title = knowledge_base[subj_id]["title"]
    topic_full = knowledge_base[subj_id]["topics"][topic_index]
    topic = topic_full.split(". ", 1)[-1] if ". " in topic_full else topic_full
    
    await generate_essay(callback.message, subj_title, topic)
    try:
        await callback.answer()
    except TelegramAPIError:
        pass

# ==============================================================================
# 🚀 SYSTEM ENTRY (POLLING + WEB SERVER CONCURRENTLY)
# ==============================================================================
async def main() -> None:
    bot = Bot(BOT_TOKEN)
    logger.info("Bot ishga tushirilmoqda... [FATHER MODE v6.0]")
    
    # 1. MongoDB bazaga ulanish
    await db.connect()
    
    # 2. Render & cron-job.org uchun /health veb-serverini ishga tushirish
    web_runner = await start_web_server()
    
    try:
        logger.info("🤖 Polling boshlandi...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
    finally:
        await web_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
