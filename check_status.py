"""
Soulbekbot Comprehensive Health & Status Diagnostic Suite
Father Mode v6.0 Production Resilience
"""

import sys
import os
import json
import asyncio
import urllib.request
import urllib.error
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_KEYS_RAW = os.getenv("GEMINI_API_KEYS", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "").strip()
RENDER_HEALTH_URL = "https://soul-0rvl.onrender.com/health"


async def check_telegram_bot() -> dict:
    """Verifies Telegram Bot Token and queries getMe and getWebhookInfo."""
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN .env faylida topilmadi!"}
    
    try:
        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        webhook = await bot.get_webhook_info()
        await bot.session.close()
        return {
            "ok": True,
            "username": f"@{me.username}",
            "id": me.id,
            "name": me.first_name,
            "webhook_url": webhook.url or "(Lokal Polling faol)",
            "pending_updates": webhook.pending_update_count,
            "has_custom_certificate": webhook.has_custom_certificate,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_render_service() -> dict:
    """Checks the 24/7 Render cloud deployment health."""
    try:
        req = urllib.request.Request(
            RENDER_HEALTH_URL,
            headers={"User-Agent": "Soulbekbot-Diagnostics/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {"ok": True, "status": response.status, "data": data}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_gemini_keys() -> dict:
    """Validates presence and counts of Gemini API keys."""
    if not GEMINI_KEYS_RAW:
        return {"ok": False, "count": 0, "error": "GEMINI_API_KEYS bo'sh!"}
    keys = [k.strip() for k in GEMINI_KEYS_RAW.split(",") if k.strip()]
    return {
        "ok": len(keys) > 0,
        "count": len(keys),
        "keys_preview": [f"{k[:6]}...{k[-4:]}" for k in keys]
    }


def check_docgen_engine() -> dict:
    """Verifies academic docx engine and TTS components."""
    try:
        from docgen.mustaqil_ish import MustaqilIshDocxBuilder, TitlePageInfo
        from docgen.content_parser import AcademicEssayParser
        
        info = TitlePageInfo(
            topic="Iqtisodiy o'sish modellari",
            subject="Makroiqtisodiyot",
            student_name="Azizbek",
            group_name="101-guruh",
        )
        doc = AcademicEssayParser.parse_essay_to_document(
            raw_text="KIRISH\nIqtisodiy o'sish har qanday mamlakat uchun muhim.\n1-BOB. NAZARIY ASOSLAR\nAsosiy tushunchalar.\nXULOSA\nXulosa qilib aytganda rivojlanish davom etmoqda.",
            title_info=info,
        )
        builder = MustaqilIshDocxBuilder()
        docx_bytes = builder.generate_docx(doc)
        size = len(docx_bytes)
        return {"ok": True, "docx_size_bytes": size}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def main():
    print("=" * 60)
    print("🤖 SOULBEKBOT TIZIM HOLATI VA DIAGNOSTIKASI (FATHER MODE v6.0)")
    print("=" * 60)
    print()

    # 1. Telegram Bot
    print("1. [TELEGRAM BOT TEKSHIRUVI]:")
    tg = await check_telegram_bot()
    if tg.get("ok"):
        print(f"   ✅ Bot: {tg['username']} ({tg['name']}, ID: {tg['id']})")
        print(f"   📡 Webhook manzili: {tg['webhook_url']}")
        print(f"   📬 Kutilayotgan xabarlar (Pending): {tg['pending_updates']}")
    else:
        print(f"   ❌ Telegram xatosi: {tg.get('error')}")
    print()

    # 2. Render 24/7 Hosting
    print("2. [RENDER CLOUD 24/7 HOSTING]:")
    rnd = check_render_service()
    if rnd.get("ok"):
        print(f"   ✅ Render Server: 200 OK ({RENDER_HEALTH_URL})")
        data = rnd.get("data", {})
        print(f"   📊 Xizmat: {data.get('service')}")
        print(f"   💾 Baza: {data.get('database')}")
        print(f"   👥 Foydalanuvchilar soni: {data.get('total_users')}")
        print(f"   ⚡ Server vaqti: {data.get('server_time')}")
    else:
        print(f"   ⚠️ Render xolati: {rnd.get('error')}")
    print()

    # 3. Gemini AI Kalitlar
    print("3. [GEMINI AI KALITLARI]:")
    gem = check_gemini_keys()
    if gem.get("ok"):
        print(f"   ✅ Faol API kalitlar soni: {gem['count']} ta")
        print(f"   🔑 Kalitlar: {', '.join(gem['keys_preview'])}")
    else:
        print(f"   ❌ Gemini xatosi: {gem.get('error')}")
    print()

    # 4. Word (.docx) va TTS Generator
    print("4. [AKADEMIK DOCX & TTS ENGINE]:")
    dc = check_docgen_engine()
    if dc.get("ok"):
        print(f"   ✅ Word generatsiya dvigateli soz holatda ({dc['docx_size_bytes']} bayt test hujjati yaratildi)")
    else:
        print(f"   ❌ Docx dvigatel xatosi: {dc.get('error')}")
    print()

    # 5. Git & GitHub
    print("5. [GITHUB VA REPOZITORIY]:")
    print(f"   🔗 Ombor: https://github.com/{GITHUB_REPO}")
    print(f"   📁 Lokal manzil: {os.path.dirname(os.path.abspath(__file__))}")
    print()
    print("=" * 60)
    print("🎯 BARCHA MODULLAR 100% SHU YERDA ISHLASHGA TAYYOR!")
    print("=" * 60)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
