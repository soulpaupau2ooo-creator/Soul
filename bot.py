import asyncio
import logging
import os
import sys
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, ADMINISTRATOR
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton, ChatMemberUpdated,
    BufferedInputFile, InlineQueryResultArticle, InputTextMessageContent,
    BotCommand, BotCommandScopeDefault
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError
import google.generativeai as genai
from dotenv import load_dotenv

from database import db
from backup_manager import backup_scheduler_loop, perform_backup
from academic_tools import (
    solve_economic_problem, generate_teacher_questions,
    summarize_article, proofread_text, generate_economic_chart
)
from multimodal_handler import process_photo_problem, process_voice_topic, generate_tts_audio, extract_topic_from_photo
from admin_suite import (
    web_admin_dashboard_handler, broadcast_message, send_daily_report,
    daily_report_scheduler, is_rate_limited, essay_cache, ADMIN_IDS
)
from economics_curriculum import (
    CATEGORIES as categories,
    KNOWLEDGE_BASE as knowledge_base,
    UZBEKISTAN_MACRO_INDICATORS,
    get_category_subjects,
    get_subject_info,
    get_subject_topics,
    get_macro_stats_text,
    build_academic_essay_prompt
)

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
logger = logging.getLogger("Soulbekbot")

class BotStates(StatesGroup):
    in_problem_mode = State()      # Persistent problem solving & questions
    in_custom_essay_mode = State() # Persistent essay writing
    in_teacher_mode = State()      # Persistent teacher Q&A
    in_proofread_mode = State()    # Persistent proofreading
    in_feedback_mode = State()     # Feedback

# In-memory storage for TTS audio generation of essays
last_generated_essays: Dict[int, str] = {}

# ==============================================================================
# 🖥️ FOYDALANUVCHI INTERFEYSI (UI MENYULAR)
# ==============================================================================
def get_main_reply_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📚 Mustaqil ish yozish")],
        [KeyboardButton(text="🧮 Masala yechish"), KeyboardButton(text="📊 Iqtisodiy grafiklar")],
        [KeyboardButton(text="🎓 O'qituvchi savollari"), KeyboardButton(text="✍️ Matn tahrirlash")],
        [KeyboardButton(text="📊 O'zbekiston statistikasi"), KeyboardButton(text="👥 Referal (Do'stlar)")],
        [KeyboardButton(text="🌐 Tilni tanlash")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Kerakli bo'limni tanlang...")

def get_back_only_menu() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="⬅️ Orqaga")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Chiqish uchun 'Orqaga' bosing...")

def get_language_reply_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")],
        [KeyboardButton(text="🇬🇧 English"), KeyboardButton(text="🇺🇿 Ўзбекcha")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Tilni tanlang / Выберите язык...")

def get_start_language_inline() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha (Lotin)", callback_data="firstlang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="firstlang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="firstlang_en")],
        [InlineKeyboardButton(text="🇺🇿 Ўзбекcha (Кирилл)", callback_data="firstlang_uz_cyr")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_main_menu() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=cat_data["title"], callback_data=f"cat_{cat_id}")] for cat_id, cat_data in categories.items()]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_subjects_menu(cat_id: str) -> InlineKeyboardMarkup:
    cat = categories.get(cat_id, {})
    subjs = cat.get("subjects", {})
    kb = [[InlineKeyboardButton(text=f"📘 {subj_title}", callback_data=f"subj_{subj_id}")] for subj_id, subj_title in subjs.items()]
    kb.append([InlineKeyboardButton(text="⬅️ Yo'nalishlarga qaytish", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_subject_topics_menu(subj_id: str, cat_id: str = "nazariy", page: int = 0) -> InlineKeyboardMarkup:
    """Fan tanlanganda 5 tadan tayyor mavzular, sahifalash va o'zi kiritish/rasm variantlari."""
    topics = get_subject_topics(subj_id)
    per_page = 5
    total_pages = max(1, (len(topics) + per_page - 1) // per_page)
    cur_page = max(0, min(page, total_pages - 1))
    
    start_idx = cur_page * per_page
    end_idx = min(start_idx + per_page, len(topics))
    
    kb = []
    for i in range(start_idx, end_idx):
        t_name = topics[i]
        btn_text = f"{i+1}. {t_name}"
        if len(btn_text) > 42:
            btn_text = btn_text[:40] + "..."
        kb.append([InlineKeyboardButton(text=btn_text, callback_data=f"tpk_{subj_id}_{i}")])
        
    if total_pages > 1:
        nav_row = []
        if cur_page > 0:
            nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"tpg_{subj_id}_{cat_id}_{cur_page - 1}"))
        nav_row.append(InlineKeyboardButton(text=f"📄 {cur_page + 1}/{total_pages}", callback_data="noop"))
        if cur_page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"tpg_{subj_id}_{cat_id}_{cur_page + 1}"))
        kb.append(nav_row)
        
    kb.append([
        InlineKeyboardButton(text="✍️ O'z mavzuingizni yozish", callback_data=f"write_topic_{subj_id}"),
        InlineKeyboardButton(text="📸 Rasmdan o'qish", callback_data=f"photo_topic_{subj_id}")
    ])
    kb.append([InlineKeyboardButton(text="⬅️ Fanlar ro'yxatiga qaytish", callback_data=f"cat_{cat_id}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_chart_selection_menu() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📈 Talab va Taklif muvozanati", callback_data="chart_supply_demand")],
        [InlineKeyboardButton(text="📊 O'zbekiston YaIM o'sishi", callback_data="chart_gdp_growth")],
        [InlineKeyboardButton(text="📉 Fillips egri chizig'i (Inflyatsiya/Ishsizlik)", callback_data="chart_phillips")],
        [InlineKeyboardButton(text="🥧 Iqtisodiyot tarmoqlari ulushi", callback_data="chart_sectors")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_languages_menu() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha (Lotin)", callback_data="setlang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="setlang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en")],
        [InlineKeyboardButton(text="🇺🇿 Ўзбекча (Кирилл)", callback_data="setlang_uz_cyr")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_essay_action_menu(user_id: int) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🎧 Ovozli tinglash (Audio)", callback_data=f"tts_play_{user_id}")],
        [InlineKeyboardButton(text="🎓 O'qituvchi savollari (Imtihon)", callback_data=f"exam_sim_{user_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==============================================================================
# 🌐 KEEP-ALIVE & WEB ADMIN SERVER (/health va /admin)
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
        text="🤖 Soulbekbot 24/7 Cloud Hosting da faol ishlamoqda!\nKeep-alive health endpoint: /health\nWeb Admin Dashboard: /admin",
        content_type="text/plain; charset=utf-8"
    )

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_check_handler)
    app.router.add_get("/admin", web_admin_dashboard_handler)
    
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Keep-Alive Web Server 0.0.0.0:{port} portida ishga tushdi (/health va /admin tayyor)")
    return runner

# ==============================================================================
# 🤖 YUKORI DARAJADAGI AI VA KESH (RESILIENCE + LRU CACHE)
# ==============================================================================
CANDIDATE_MODELS: List[str] = [
    'gemini-3.5-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.6-flash',
    'gemini-flash-latest'
]

async def request_ai_content(prompt: str) -> str:
    """Asynchronous AI request with robust round-robin API Key rotation, multi-model cascade, and LRU caching."""
    cache_key = prompt.strip()
    if cache_key in essay_cache:
        logger.info("⚡ Javob keshdan olindi (Cache Hit)!")
        return essay_cache[cache_key]

    if not API_KEYS:
        raise ValueError("AI API KEYS REQUIRED")
        
    shuffled_keys = list(API_KEYS)
    random.shuffle(shuffled_keys)
    
    last_exception: Optional[Exception] = None
    
    for attempt, current_key in enumerate(shuffled_keys):
        try:
            genai.configure(api_key=current_key)
        except Exception as ce:
            logger.warning(f"Key {attempt+1} configure error: {ce}")
            continue

        for model_name in CANDIDATE_MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, prompt),
                    timeout=25.0
                )
                
                if response and response.text:
                    result_text = response.text
                    essay_cache[cache_key] = result_text
                    logger.info(f"[SUCCESS] AI muvaffaqiyatli: {model_name} (Kalit: {attempt+1})")
                    return result_text
                    
            except Exception as me:
                last_exception = me
                err_lower = str(me).lower()
                logger.warning(f"Model {model_name} xatosi: {err_lower[:90]}")
                if "429" in err_lower or "quota" in err_lower or "404" in err_lower:
                    continue
                else:
                    continue
                    
        if attempt < len(shuffled_keys) - 1:
            await asyncio.sleep(1)
            
    if last_exception:
        raise last_exception
    return "Xatolik."

async def generate_essay(message: types.Message, subject: str, topic: str) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if not API_KEYS:
        await message.answer("⚠️ Sun'iy Intelekt qismi (Brain) ulanmagan. Iltimos, ma'muriyatga xabar bering.")
        return
        
    wait_msg = await message.answer(
        f"⏳ *{subject}* bo'yicha *\"{topic}\"* mavzusida qisqa va lo'nda mustaqil ish tayyorlanmoqda...",
        parse_mode="Markdown"
    )
    
    lang = await db.get_user_language(user_id) if user_id else "uz"
    prompt = build_academic_essay_prompt(subject_title=subject, topic=topic, lang=lang)
    
    try:
        text = await request_ai_content(prompt)
        
        if user_id:
            last_generated_essays[user_id] = text
        
        if message.from_user:
            await db.log_request(
                user_id=message.from_user.id,
                subject=subject,
                topic=topic
            )
        
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(text, reply_markup=get_essay_action_menu(user_id))
            
        await wait_msg.delete()
        
    except ValueError as ve:
        await wait_msg.edit_text("⚠️ AI ulanishida uzilish yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        logger.error(f"Value Error: {ve}")
    except Exception as e:
        logger.error(f"Initial attempt error: {e}")
        # Father Mode: Automatic rapid retry with backoff
        try:
            await asyncio.sleep(2)
            retry_text = await request_ai_content(prompt)
            if user_id:
                last_generated_essays[user_id] = retry_text
            await wait_msg.delete()
            await message.answer(retry_text, reply_markup=get_essay_action_menu(user_id))
            return
        except Exception as retry_e:
            logger.error(f"Retry failed: {retry_e}")
            
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str:
            await wait_msg.edit_text("⏳ Tarmoqda qisqa tirbandlik. Iltimos, tugmani yana bir bor bosing.")
        else:
            await wait_msg.edit_text("⚠️ Texnik xatolik yuz berdi. Iltimos, boshqa mavzu tanlab ko'ring.")

# ==============================================================================
# 🎮 XABARLAR YUKLATGICHI (HANDLERS)
# ==============================================================================
@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    uid = message.from_user.id if message.from_user else 0
    
    if is_rate_limited(uid):
        return
        
    if await db.is_banned(uid):
        await message.answer("🚫 Siz botdan foydalanishdan chetlashtirilgansiz.")
        return

    # Check referral start: /start ref_123456
    text_parts = (message.text or "").split()
    if len(text_parts) > 1 and text_parts[1].startswith("ref_"):
        try:
            inviter_id = int(text_parts[1].replace("ref_", ""))
            referred = await db.add_referral(inviter_id=inviter_id, new_user_id=uid)
            if referred:
                try:
                    await message.bot.send_message(
                        chat_id=inviter_id,
                        text=f"🎉 Yangi do'stingiz ({message.from_user.full_name}) botga qo'shildi! Sizga +10 ball berildi."
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Referral parsing error: {e}")

    # Save user to DB
    if message.from_user:
        await db.add_or_update_user(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
        
    # Start bosganda faqatgina til tanlash chiqadi, boshqa hech qanday menyu chiqmaydi!
    welcome_text = (
        "Iltimos, o'zingizga qulay tilni tanlang:\n"
        "Пожалуйста, выберите язык:\n"
        "Please choose your language:"
    )
    await message.answer(welcome_text, reply_markup=get_language_reply_menu())

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English", "🇺🇿 Ўзбекча"]))
async def language_selection_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    uid = message.from_user.id if message.from_user else 0
    choice = message.text
    
    if choice == "🇺🇿 O'zbekcha":
        lang = "uz"
        reply_text = "Assalomu alaykum! Sizga qanday yordam kerak?\n\nQuyidagi bo'limlardan birini tanlang:"
    elif choice == "🇷🇺 Русский":
        lang = "ru"
        reply_text = "Здравствуйте! Чем я могу вам помочь?\n\nВыберите нужный раздел:"
    elif choice == "🇬🇧 English":
        lang = "en"
        reply_text = "Hello! How can I help you today?\n\nPlease select an option:"
    else:
        lang = "uz_cyr"
        reply_text = "Ассалому алайкум! Сизга қандай ёрдам керак?\n\nКеракли бўлимни танланг:"
        
    if uid:
        await db.set_user_language(uid, lang)
        
    await message.answer(reply_text, reply_markup=get_main_reply_menu())

@dp.callback_query(F.data.startswith("firstlang_"))
async def first_language_callback(callback: types.CallbackQuery):
    lang_code = callback.data.replace("firstlang_", "")
    uid = callback.from_user.id
    await db.set_user_language(uid, lang_code)
    await callback.answer("Til tanlandi!")
    
    if lang_code == "uz":
        text = "Assalomu alaykum! Sizga qanday yordam kerak?\n\nQuyidagi bo'limlardan birini tanlang:"
    elif lang_code == "ru":
        text = "Здравствуйте! Чем я могу вам помочь?\n\nВыберите нужный раздел:"
    elif lang_code == "en":
        text = "Hello! How can I help you today?\n\nPlease select an option:"
    else:
        text = "Ассалому алайкум! Сизга қандай ёрдам керак?\n\nКеракли бўлимни танланг:"
        
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(text, reply_markup=get_main_reply_menu())

@dp.message(F.text == "⬅️ Orqaga")
async def back_to_main_reply(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🏠 Asosiy menyudasiz. Quyidagi bo'limlardan birini tanlang:", reply_markup=get_main_reply_menu())

# --- 📚 1. Mustaqil Ish Bo'limi ---
@dp.message(Command("fanlar"))
@dp.message(Command("mustaqil_ish"))
@dp.message(F.text == "📚 Mustaqil ish yozish")
async def btn_mustaqil_ish_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Bo'lim ochilmoqda...", reply_markup=get_back_only_menu())
    text = (
        "📚 *Barcha Iqtisodiyot Fanlari va Mavzular Kutubxonasi*\n\n"
        "O'zingizga kerakli Iqtisodiyot yo'nalishini tanlang. "
        "Har bir yo'nalishda 6 tadan fan va yuzlab rasmiy OTM mustaqil ish mavzulari mavjud:"
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- 🧮 2. Masala va Savol-Javob Bo'limi (Davomiy Rejim) ---
@dp.message(Command("masala"))
@dp.message(F.text == "🧮 Masala yechish")
async def btn_problem_solve_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(BotStates.in_problem_mode)
    await message.answer("Bo'lim ochildi...", reply_markup=get_back_only_menu())
    await message.answer(
        "🧮 *Iqtisodiy Masala va Savol-Javob Bo'limidasiz*\n\n"
        "Iqtisodiyotga oid istalgan masalangizni yoki savolingizni yozib yuboring (yoki daftardagi rasmini tashlang).\n\n"
        "💡 *Bu bo'limda ketma-ket istagancha savol berishingiz mumkin!* Bot har biriga javob beradi.\n"
        "Chiqish uchun pastdagi *\"⬅️ Orqaga\"* tugmasini bosing.",
        parse_mode="Markdown"
    )

@dp.message(BotStates.in_problem_mode, F.text)
async def problem_continuous_text_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyudasiz.", reply_markup=get_main_reply_menu())
        return

    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    wait_msg = await message.answer("⏳ Javob tayyorlanmoqda...")
    solution = await solve_economic_problem(message.text, lang=lang)
    await wait_msg.delete()
    # DO NOT CLEAR STATE! User can keep asking!
    await message.answer(solution, reply_markup=get_back_only_menu())

# --- 📸 3. Rasm orqali masala yechish (Gemini Vision OCR) ---
@dp.message(F.photo)
async def photo_message_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    photo = message.photo[-1]
    wait_msg = await message.answer("📸 Rasm qabul qilindi! Masala o'qilib, qisqa va lo'nda yechim tayyorlanmoqda...")
    solution = await process_photo_problem(bot, photo, lang=lang)
    await wait_msg.delete()
    await message.answer(solution, reply_markup=get_back_only_menu())

# --- 🎤 4. Ovozli xabar orqali mavzu qabul qilish ---
@dp.message(F.voice)
async def voice_message_handler(message: types.Message, bot: Bot) -> None:
    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    wait_msg = await message.answer("🎙 Ovozli xabaringiz eshitilmoqda...")
    result = await process_voice_topic(bot, message.voice, lang=lang)
    await wait_msg.delete()
    await message.answer(result, reply_markup=get_back_only_menu())

# --- 📊 5. Iqtisodiy Grafiklar Bo'limi ---
@dp.message(F.text == "📊 Iqtisodiy grafiklar")
async def btn_charts_handler(message: types.Message) -> None:
    text = (
        "📊 *Iqtisodiy Grafik va Diagrammalar Generatori*\n\n"
        "Mustaqil ish yoki taqdimotingizga qo'shish uchun quyidagi diagrammalardan birini tanlang. "
        "Bot uni yuqori sifatli rasm holida chizib beradi:"
    )
    await message.answer(text, reply_markup=get_chart_selection_menu(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("chart_"))
async def chart_callback_handler(callback: types.CallbackQuery):
    chart_type = callback.data.replace("chart_", "")
    await callback.answer("Grafik chizilmoqda...")
    
    titles = {
        "supply_demand": "Bozor Muvozanati (Talab va Taklif)",
        "gdp_growth": "O'zbekiston YaIM o'sish sur'atlari dinamikasi",
        "phillips": "Fillips egri chizig'i (Inflyatsiya va Ishsizlik)",
        "sectors": "Iqtisodiyot tarmoqlarining YaIMdagi ulushi"
    }
    title = titles.get(chart_type, "Iqtisodiy Diagramma")
    
    chart_bytes = await asyncio.to_thread(generate_economic_chart, chart_type, title)
    file_obj = BufferedInputFile(chart_bytes, filename=f"{chart_type}.png")
    
    await callback.message.answer_photo(
        photo=file_obj,
        caption=f"📈 *{title}*",
        parse_mode="Markdown"
    )

# --- 🎓 6. O'qituvchi Savollari (Davomiy Rejim) ---
@dp.message(Command("savollar"))
@dp.message(F.text == "🎓 O'qituvchi savollari")
async def btn_teacher_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(BotStates.in_teacher_mode)
    await message.answer("Bo'lim ochildi...", reply_markup=get_back_only_menu())
    await message.answer(
        "🎓 *O'qituvchi bilan Suhbat Trenajyori*\n\n"
        "Qaysi mavzudan imtihonga yoki darsga tayyorlanmoqchisiz? Mavzuni yozing:\n"
        "Bot o'qituvchi berishi mumkin bo'lgan 3 ta qiyin savol va qisqa javoblarni chiqaradi.\n\n"
        "💡 *Bu bo'limda ketma-ket turli mavzularni yozishingiz mumkin!*",
        parse_mode="Markdown"
    )

@dp.message(BotStates.in_teacher_mode, F.text)
async def teacher_continuous_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyudasiz.", reply_markup=get_main_reply_menu())
        return

    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    wait_msg = await message.answer("⏳ Savollar tayyorlanmoqda...")
    questions = await generate_teacher_questions(message.text, lang=lang)
    await wait_msg.delete()
    await message.answer(questions, reply_markup=get_back_only_menu())

# --- ✍️ 7. Matn Tahrirlash (Davomiy Rejim) ---
@dp.message(Command("tahrirlash"))
@dp.message(F.text == "✍️ Matn tahrirlash")
async def btn_proofread_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(BotStates.in_proofread_mode)
    await message.answer("Bo'lim ochildi...", reply_markup=get_back_only_menu())
    await message.answer(
        "✍️ *Akademik Tahrirchi (Proofreading)*\n\n"
        "O'zingiz yozgan matnni yuboring. Bot imlo xatolarini to'g'rilab, ilmiy va ravon holatga keltiradi.\n\n"
        "💡 *Xohlagancha matnlaringizni ketma-ket tashlashingiz mumkin!*",
        parse_mode="Markdown"
    )

@dp.message(BotStates.in_proofread_mode, F.text)
async def proofread_continuous_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyudasiz.", reply_markup=get_main_reply_menu())
        return

    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    wait_msg = await message.answer("⏳ Matn tahrir qilinmoqda...")
    edited = await proofread_text(message.text, lang=lang)
    await wait_msg.delete()
    await message.answer(edited, reply_markup=get_back_only_menu())

# --- 🎧 8. TTS Audio Tinglash Callbacks ---
@dp.callback_query(F.data.startswith("tts_play_"))
async def tts_callback_handler(callback: types.CallbackQuery):
    uid = int(callback.data.replace("tts_play_", ""))
    essay_text = last_generated_essays.get(uid)
    if not essay_text:
        await callback.answer("⚠️ Audio tayyorlash uchun avval mustaqil ish yozing.", show_alert=True)
        return
        
    await callback.answer("🎧 Audio tayyorlanmoqda (10 soniya)...")
    wait_msg = await callback.message.answer("⏳ Mustaqil ish audio shaklga o'tkazilmoqda...")
    
    lang = await db.get_user_language(uid)
    audio_bytes = await asyncio.to_thread(generate_tts_audio, essay_text, lang)
    await wait_msg.delete()
    
    if audio_bytes:
        audio_file = BufferedInputFile(audio_bytes, filename="mustaqil_ish_audio.mp3")
        await callback.message.answer_audio(
            audio=audio_file,
            caption="🎧 *Mustaqil ishning audio versiyasi*",
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer("⚠️ Audioni tayyorlashda xatolik yuz berdi.")

@dp.callback_query(F.data.startswith("exam_sim_"))
async def exam_sim_callback_handler(callback: types.CallbackQuery):
    uid = int(callback.data.replace("exam_sim_", ""))
    essay_text = last_generated_essays.get(uid, "Iqtisodiyot")
    await callback.answer("Savollar tayyorlanmoqda...")
    wait_msg = await callback.message.answer("⏳ Mavzu bo'yicha imtihon savollari olinmoqda...")
    lang = await db.get_user_language(uid)
    questions = await generate_teacher_questions(essay_text[:200], lang=lang)
    await wait_msg.delete()
    await callback.message.answer(questions)

# --- 👥 9. Referal Tizimi ---
@dp.message(F.text == "👥 Referal (Do'stlar)")
async def btn_referral_handler(message: types.Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{uid}"
    
    user_data = await db.get_user(uid) or {}
    count = user_data.get("referral_count", 0)
    points = user_data.get("points", 0)
    
    text = (
        f"👥 *Do'stlarni taklif qilish va Ballar yig'ish*\n\n"
        f"Siz taklif qilgan do'stlar: *{count} ta*\n"
        f"Sizning to'plagan ballaringiz: *{points} ball*\n\n"
        f"🔗 *Sizning shaxsiy havolangiz:*\n`{ref_link}`\n\n"
        f"💡 Ushbu havolani kursdoshlaringiz va talabalar guruhlariga yuboring. "
        f"Har bir yangi do'stingiz uchun sizga +10 ball beriladi!"
    )
    await message.answer(text, parse_mode="Markdown")

# --- 🌐 10. Tilni Tanlash ---
@dp.message(F.text == "🌐 Tilni tanlash")
async def btn_language_handler(message: types.Message) -> None:
    await message.answer("Iltimos, o'zingizga qulay tilni tanlang:", reply_markup=get_language_reply_menu())

@dp.callback_query(F.data.startswith("setlang_"))
async def set_language_callback(callback: types.CallbackQuery):
    lang_code = callback.data.replace("setlang_", "")
    uid = callback.from_user.id
    await db.set_user_language(uid, lang_code)
    await callback.answer("Til o'zgartirildi!")
    await callback.message.edit_text("✅ Til sozlamalari yangilandi.")

# --- 📩 11. Feedback (Fikr-mulohaza) ---
@dp.message(Command("feedback"))
async def feedback_command_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(BotStates.in_feedback_mode)
    await message.answer("✍️ Iltimos, o'z fikr-mulohazangiz yoki taklifingizni bitta xabar qilib yozib yuboring:")

@dp.message(BotStates.in_feedback_mode)
async def feedback_process_handler(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    uid = message.from_user.id
    name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "mavjud emas"
    
    admin_text = (
        f"📩 *Yangi Fikr-Mulohaza (Feedback)*\n\n"
        f"👤 Kimdan: *{name}* ({username})\n"
        f"🆔 ID: `{uid}`\n"
        f"💬 Xabar:\n{message.text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_text, parse_mode="Markdown")
        except Exception:
            pass
            
    await message.answer("✅ Fikr-mulohazangiz adminga yetkazildi! Rahmat.")

# --- 🔎 12. Inline Query Rejimi (@Soulbekbot ...) ---
@dp.inline_query()
async def inline_search_handler(inline_query: types.InlineQuery):
    query = (inline_query.query or "").strip().lower()
    results = []
    
    bot_info = await inline_query.bot.get_me()
    bot_username = bot_info.username or "Soulbekbot"
    
    count = 0
    for subj_id, data in knowledge_base.items():
        title = data["title"]
        for topic in data["topics"]:
            if not query or query in title.lower() or query in topic.lower():
                results.append(InlineQueryResultArticle(
                    id=f"{subj_id}_{count}",
                    title=f"{title}: {topic}",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            f"📚 *Fan:* {title}\n"
                            f"📝 *Mavzu:* {topic}\n\n"
                            f"Ushbu mavzu bo'yicha to'liq mustaqil ish tayyorlash uchun @{bot_username} ga kiring!"
                        ),
                        parse_mode="Markdown"
                    ),
                    description=f"{title} fani bo'yicha mustaqil ish mavzusi"
                ))
                count += 1
                if count >= 8:
                    break
        if count >= 8:
            break
            
    await inline_query.answer(results, cache_time=300)

# --- 👑 13. Admin Buyruqlari (/broadcast, /ban, /unban) ---
@dp.message(Command("broadcast"))
async def broadcast_cmd_handler(message: types.Message, bot: Bot) -> None:
    uid = message.from_user.id if message.from_user else 0
    if uid not in ADMIN_IDS:
        return
        
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        await message.answer("Xabar matnini kiriting: `/broadcast Xabar matni`", parse_mode="Markdown")
        return
        
    wait_msg = await message.answer("⏳ Xabar barcha foydalanuvchilarga yuborilmoqda...")
    res = await broadcast_message(bot, text_to_send)
    await wait_msg.edit_text(f"✅ Xabar yuborildi!\n\nYetkazildi: *{res['sent']}* ta\nXatolik: *{res['failed']}* ta\nJami: *{res['total']}* ta", parse_mode="Markdown")

@dp.message(Command("ban"))
async def ban_cmd_handler(message: types.Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    if uid not in ADMIN_IDS:
        return
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Foydalanuvchi ID sini kiriting: `/ban 12345678`", parse_mode="Markdown")
        return
    target_id = int(args[1])
    await db.set_ban_status(target_id, True)
    await message.answer(f"🚫 Foydalanuvchi `{target_id}` qora ro'yxatga kiritildi.", parse_mode="Markdown")

@dp.message(Command("unban"))
async def unban_cmd_handler(message: types.Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    if uid not in ADMIN_IDS:
        return
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Foydalanuvchi ID sini kiriting: `/unban 12345678`", parse_mode="Markdown")
        return
    target_id = int(args[1])
    await db.set_ban_status(target_id, False)
    await message.answer(f"✅ Foydalanuvchi `{target_id}` qora ro'yxatdan chiqarildi.", parse_mode="Markdown")

# --- ⚙️ Asosiy Navigatsiya & Mavzular ---
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

# --- ⚙️ Fan va Mavzu Tanlash Oqimi ---
@dp.callback_query(F.data.startswith("subj_"))
async def subject_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    subj_id = callback.data.split("_")[1]
    
    # Kategoriya ID sini aniqlash
    cat_id = "nazariy"
    for c_id, c_data in categories.items():
        if subj_id in c_data["subjects"]:
            cat_id = c_id
            break
            
    subj_info = get_subject_info(subj_id)
    subj_title = subj_info.get("title", "Iqtisodiyot") if subj_info else "Iqtisodiyot"
    await state.update_data(subject_title=subj_title, subject_id=subj_id, cat_id=cat_id)
    await state.set_state(BotStates.in_custom_essay_mode)
    
    text = (
        f"📘 Tanlangan fan: *{subj_title}*\n\n"
        f"Quyidagi tayyor mavzulardan birini tanlang (ustiga bosing) yoki o'z mavzuingizni yozing/rasmini yuboring:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=get_subject_topics_menu(subj_id, cat_id, page=0), parse_mode="Markdown")
        await callback.answer()
    except TelegramAPIError:
        pass

@dp.callback_query(F.data.startswith("tpg_"))
async def topic_page_handler(callback: types.CallbackQuery) -> None:
    # tpg_{subj_id}_{cat_id}_{page}
    parts = callback.data.split("_")
    page = int(parts[-1])
    cat_id = parts[-2]
    subj_id = "_".join(parts[1:-2])
    
    subj_info = get_subject_info(subj_id)
    subj_title = subj_info.get("title", "Iqtisodiyot") if subj_info else "Iqtisodiyot"
    
    text = (
        f"📘 Tanlangan fan: *{subj_title}*\n\n"
        f"Quyidagi tayyor mavzulardan birini tanlang (ustiga bosing) yoki o'z mavzuingizni yozing/rasmini yuboring:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=get_subject_topics_menu(subj_id, cat_id, page=page), parse_mode="Markdown")
        await callback.answer()
    except TelegramAPIError:
        pass

@dp.callback_query(F.data.startswith("tpk_"))
async def topic_picked_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    # tpk_{subj_id}_{idx}
    parts = callback.data.split("_")
    idx = int(parts[-1])
    subj_id = "_".join(parts[1:-1])
    
    subj_info = get_subject_info(subj_id)
    if not subj_info:
        await callback.answer("⚠️ Fan topilmadi.")
        return
        
    topics = subj_info.get("topics", [])
    if 0 <= idx < len(topics):
        topic = topics[idx]
        subj_title = subj_info["title"]
        await callback.answer(f"Tanlandi: {topic[:30]}...")
        await generate_essay(callback.message, subj_title, topic)
    else:
        await callback.answer("⚠️ Mavzu topilmadi.")

@dp.callback_query(F.data == "noop")
async def noop_callback_handler(callback: types.CallbackQuery) -> None:
    await callback.answer()

@dp.callback_query(F.data.startswith("write_topic_"))
async def write_topic_click_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    subj_id = callback.data.replace("write_topic_", "")
    subj_title = knowledge_base.get(subj_id, {}).get("title", "Iqtisodiyot")
    
    await state.update_data(subject_title=subj_title, subject_id=subj_id)
    await state.set_state(BotStates.in_custom_essay_mode)
    
    msg_text = (
        f"✍️ *{subj_title}* fani bo'yicha mustaqil ish mavzuingizni matn qilib yozib yuboring:\n\n"
        f"*(Chiqish uchun pastdagi \"⬅️ Orqaga\" tugmasini bosing)*"
    )
    try:
        await callback.message.edit_text(msg_text, parse_mode="Markdown")
        await callback.answer()
    except TelegramAPIError:
        pass

@dp.callback_query(F.data.startswith("photo_topic_"))
async def photo_topic_click_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    subj_id = callback.data.replace("photo_topic_", "")
    subj_title = knowledge_base.get(subj_id, {}).get("title", "Iqtisodiyot")
    
    await state.update_data(subject_title=subj_title, subject_id=subj_id)
    await state.set_state(BotStates.in_custom_essay_mode)
    
    msg_text = (
        f"📸 *{subj_title}* fani bo'yicha daftardagi, kitob mundarijasidagi yoki ekrandagi mavzu rasmini yuboring.\n\n"
        f"💡 AI Vision rasm ichidan mavzuni o'zi avtomatik ajratib oladi va to'liq mustaqil ish yozib beradi!"
    )
    try:
        await callback.message.edit_text(msg_text, parse_mode="Markdown")
        await callback.answer()
    except TelegramAPIError:
        pass

@dp.message(BotStates.in_custom_essay_mode, F.text)
async def custom_topic_message_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyudasiz.", reply_markup=get_main_reply_menu())
        return

    data = await state.get_data()
    subj_title = data.get("subject_title", "Iqtisodiyot")
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("Iltimos, mavzuni matn ko'rinishida kiriting.")
        return
        
    await generate_essay(message, subj_title, topic)

@dp.message(BotStates.in_custom_essay_mode, F.photo)
async def custom_topic_photo_handler(message: types.Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    subj_title = data.get("subject_title", "Iqtisodiyot")
    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    
    wait_msg = await message.answer("📸 Rasm tahlil qilinmoqda, mavzu aniqlanmoqda...")
    photo = message.photo[-1]
    detected_topic = await extract_topic_from_photo(bot, photo, subject_title=subj_title, lang=lang)
    
    if detected_topic and len(detected_topic) > 3:
        await wait_msg.edit_text(
            f"🎯 *Rasm ichidan aniqlangan mavzu:*\n`{detected_topic}`\n\n"
            f"⏳ Ushbu mavzu bo'yicha *{subj_title}* fanidan mustaqil ish tayyorlanmoqda...",
            parse_mode="Markdown"
        )
        await generate_essay(message, subj_title, detected_topic)
    else:
        await wait_msg.edit_text(
            "⚠️ Rasm ichidagi mavzuni aniq o'qib bo'lmadi. "
            "Iltimos, rasmni yaqinroq va tiniqroq qilib qayta yuboring yoki mavzuni matn ko'rinishida yozing."
        )

@dp.message(BotStates.in_custom_essay_mode, F.voice)
async def custom_topic_voice_handler(message: types.Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    subj_title = data.get("subject_title", "Iqtisodiyot")
    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    
    wait_msg = await message.answer("🎙 Ovozli xabardan mavzu o'qilmoqda...")
    result = await process_voice_topic(bot, message.voice, lang=lang)
    await wait_msg.delete()
    await message.answer(result, reply_markup=get_back_only_menu())

# --- 📊 14. Statistika va Makroiqtisodiy Ko'rsatkichlar (/stats) ---
@dp.message(Command("stats"))
@dp.message(F.text == "📊 O'zbekiston statistikasi")
@dp.message(F.text == "📊 Statistika")
async def stats_command_handler(message: types.Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    stats = await db.get_stats()
    b_state = await db.get_backup_state()
    ch_info = b_state.get("channel", "@soul_backups")
    db_type = "MongoDB Atlas (Bulut)" if db.is_connected else "Mahalliy Zaxira (JSON)"
    
    macro_text = get_macro_stats_text(lang=lang)
    bot_stats_text = (
        f"\n\n🤖 *Soulbekbot Faoliyat Ko'rsatkichlari:*\n"
        f"👥 Ro'yxatdan o'tgan talabalar: *{stats.get('users', 0)}* ta\n"
        f"📝 Tayyorlangan mustaqil ishlar: *{stats.get('requests', 0)}* ta\n"
        f"🗄 Ma'lumotlar bazasi: *{db_type}*\n"
        f"📦 Backup kanali: `{ch_info}`\n"
        f"⚡ LRU Kesh: *{len(essay_cache)} ta mavzu*\n"
        f"🌐 Bulutli Server: *24/7 Faol (/health & /admin)*"
    )
    await message.answer(macro_text + bot_stats_text, parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help_handler(message: types.Message) -> None:
    help_text = (
        "ℹ️ *Soulbekbot — O'zbekiston Talabalari Uchun Qo'llanma:*\n\n"
        "1. 📚 *Mustaqil ish yozish* (`/fanlar`) — 30 ta fandan birini tanlang, 300+ tayyor mavzulardan birini bosing yoki o'zingiz yozing/rasmini yuboring.\n"
        "2. 🧮 *Masala yechish* (`/masala`) — masala shartini yoki daftardagi rasmini yuboring.\n"
        "3. 📊 *Grafiklar* — talab va taklif, YaIM, Fillips egri chizig'i grafiklarini rasm qilib oling.\n"
        "4. 🎓 *O'qituvchi savollari* (`/savollar`) — imtihonga tayyorgarlik ko'rish uchun mavzu yuboring.\n"
        "5. ✍️ *Matn tahrirlash* (`/tahrirlash`) — o'z matningizni akademik tahrir qildiring.\n"
        "6. 📊 *Statistika* (`/stats`) — O'zbekiston rasmiy makroiqtisodiy ko'rsatkichlari bilan tanishing.\n\n"
        "💡 *Telegramda istalgan paytda '/' belgisini qo'ysangiz, barcha buyruqlar ro'yxati chiqadi!*"
    )
    await message.answer(help_text, reply_markup=get_main_reply_menu(), parse_mode="Markdown")

@dp.message(Command("set_backup"))
async def set_backup_handler(message: types.Message, bot: Bot) -> None:
    args = message.text.split()
    if len(args) < 2:
        state = await db.get_backup_state()
        current = state.get("channel", "@soul_backups")
        await message.answer(
            f"ℹ️ *Joriy backup kanali:* `{current}`\n\n"
            "Yangi kanalni ulash uchun: `/set_backup @kanal_nomi`",
            parse_mode="Markdown"
        )
        return
        
    new_channel = args[1].strip()
    await db.update_backup_state(channel=new_channel)
    wait_msg = await message.answer(f"⏳ Backup kanali `{new_channel}` ga o'rnatildi. Birinchi zaxira nusxasi yuborilmoqda...", parse_mode="Markdown")
    success = await perform_backup(bot, target_channel=new_channel)
    if success:
        await wait_msg.edit_text(f"✅ Kanal `{new_channel}` ga muvaffaqiyatli ulandi va birinchi GitHub zaxira nusxasi yuborildi!", parse_mode="Markdown")
    else:
        await wait_msg.edit_text(f"⚠️ Kanal `{new_channel}` ga saqlandi, ammo zaxirani yuborishda xatolik bo'ldi. Bot kanalda ADMIN ekanligini tekshiring.", parse_mode="Markdown")

@dp.message(Command("backup"))
async def trigger_backup_handler(message: types.Message, bot: Bot) -> None:
    wait_msg = await message.answer("⏳ Yangi GitHub backup tayyorlanmoqda va kanalga yuborilmoqda...")
    success = await perform_backup(bot)
    if success:
        state = await db.get_backup_state()
        ch = state.get("channel", "@soul_backups")
        await wait_msg.edit_text(f"✅ Yangi GitHub backup `{ch}` kanaliga yuborildi! (Eski backup o'chirildi).")
    else:
        await wait_msg.edit_text("❌ Backup yuborilmadi.")

@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=ADMINISTRATOR))
async def bot_added_to_channel_handler(event: ChatMemberUpdated, bot: Bot):
    chat = event.chat
    if chat.type in ("channel", "supergroup"):
        channel_identifier = f"@{chat.username}" if chat.username else str(chat.id)
        logger.info(f"📢 Bot {chat.title} ({channel_identifier}) kanaliga admin qilindi!")
        await db.update_backup_state(channel=channel_identifier)
        await perform_backup(bot, target_channel=channel_identifier)

@dp.message(F.forward_from_chat)
async def forwarded_channel_message_handler(message: types.Message, bot: Bot):
    chat = message.forward_from_chat
    if chat and chat.type in ("channel", "supergroup"):
        ch_id = str(chat.id)
        title = chat.title or "Kanal"
        await db.update_backup_state(channel=ch_id)
        wait_msg = await message.answer(f"✅ Maxfiy kanal aniqlandi: *{title}* (ID: `{ch_id}`)\n\nBackup yuborilmoqda...", parse_mode="Markdown")
        success = await perform_backup(bot, target_channel=ch_id)
        if success:
            await wait_msg.edit_text(f"✅ *{title}* kanaliga muvaffaqiyatli ulandi va birinchi GitHub zaxira nusxasi yuborildi!", parse_mode="Markdown")
        else:
            await wait_msg.edit_text(f"⚠️ Kanal ID si `{ch_id}` saqlandi, ammo bot xabar yubora olmadi.", parse_mode="Markdown")

# --- 💬 14. Umumiy Matn Qabul Qiluvchi (Hech Qachon Jim Qolmaslik Uchun) ---
@dp.message(F.text)
async def fallback_text_handler(message: types.Message) -> None:
    if message.text == "⬅️ Orqaga":
        await message.answer("🏠 Asosiy menyudasiz. Quyidagi bo'limlardan birini tanlang:", reply_markup=get_main_reply_menu())
        return

    uid = message.from_user.id if message.from_user else 0
    lang = await db.get_user_language(uid) if uid else "uz"
    
    # Quick short answer to any general economics question
    wait_msg = await message.answer("⏳ Javob tayyorlanmoqda...")
    ans = await solve_economic_problem(message.text, lang=lang)
    await wait_msg.delete()
    await message.answer(ans, reply_markup=get_main_reply_menu())

# ==============================================================================
# 🚀 SYSTEM ENTRY (POLLING + WEB SERVER + BACKUP SCHEDULER)
# ==============================================================================
async def main() -> None:
    bot = Bot(BOT_TOKEN)
    logger.info("Bot ishga tushirilmoqda... [FATHER MODE v6.0 SUPER-SUITE]")
    
    # 1. MongoDB bazaga ulanish
    await db.connect()
    
    # 2. Render & cron-job.org uchun /health va /admin veb-serverini ishga tushirish
    web_runner = await start_web_server()
    
    # 3. Har 30 minutda GitHub Backup yuboruvchi fon xizmati
    backup_task = asyncio.create_task(backup_scheduler_loop(bot))
    
    # 4. Kunlik hisobot xizmati
    daily_task = asyncio.create_task(daily_report_scheduler(bot))
    
    # 5. Telegram Slash Commands - foydalanuvchi '/' belgisini bosishi bilan barcha buyruqlar chiqishi
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish / Qayta boshlash"),
        BotCommand(command="fanlar", description="📚 Barcha 30 ta fan va 300 ta mavzu"),
        BotCommand(command="stats", description="📊 O'zbekiston statistikasi va hisobot"),
        BotCommand(command="masala", description="🧮 Iqtisodiy masala va formulalar yechish"),
        BotCommand(command="savollar", description="🎓 O'qituvchi savollari (Imtihon)"),
        BotCommand(command="tahrirlash", description="✍️ Matnni akademik tahrirlash"),
        BotCommand(command="help", description="ℹ️ Qo'llanma va yordam")
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("✅ Telegram Bot Commands ('/') muvaffaqiyatli ro'yxatdan o'tkazildi!")
    except Exception as cmd_err:
        logger.warning(f"⚠️ Bot commands ro'yxatdan o'tkazishda ogohlantirish: {cmd_err}")
    
    try:
        logger.info("🤖 Polling boshlandi...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
    finally:
        backup_task.cancel()
        daily_task.cancel()
        await web_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
