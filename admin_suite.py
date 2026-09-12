import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from cachetools import TTLCache
from aiogram import Bot, types
from aiohttp import web
from dotenv import load_dotenv

from database import db

load_dotenv()
logger = logging.getLogger("AdminSuite")

ADMIN_ID_STR = os.getenv("ADMIN_ID", "")
ADMIN_IDS: List[int] = [int(i.strip()) for i in ADMIN_ID_STR.split(",") if i.strip().isdigit()]

# In-Memory LRU Cache (max 1000 items, expires in 2 hours)
essay_cache = TTLCache(maxsize=1000, ttl=7200)

# Anti-Spam rate limiting tracker {user_id: timestamp}
user_last_action: Dict[int, float] = {}
RATE_LIMIT_SECONDS = 2.0

def is_rate_limited(user_id: int) -> bool:
    """Check if user sends requests too rapidly."""
    now = asyncio.get_event_loop().time()
    last = user_last_action.get(user_id, 0.0)
    if now - last < RATE_LIMIT_SECONDS:
        return True
    user_last_action[user_id] = now
    return False

async def broadcast_message(bot: Bot, text: str) -> Dict[str, int]:
    """Broadcast announcement to all users in database."""
    stats = await db.get_stats()
    sent_count = 0
    fail_count = 0
    
    # Fetch all user IDs from DB
    user_ids: List[int] = []
    if db.is_connected and db.users_col is not None:
        try:
            cursor = db.users_col.find({}, {"user_id": 1})
            async for doc in cursor:
                uid = doc.get("user_id")
                if uid:
                    user_ids.append(uid)
        except Exception as e:
            logger.error(f"Error fetching users for broadcast: {e}")
            
    if not user_ids:
        # Fallback to local
        data = db._load_local()
        user_ids = [int(uid) for uid in data.get("users", {}).keys()]

    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text=text, parse_mode="Markdown")
            sent_count += 1
            await asyncio.sleep(0.05)  # Telegram rate limit compliance
        except Exception as e:
            fail_count += 1
            logger.warning(f"Broadcast failed to {uid}: {e}")

    return {"sent": sent_count, "failed": fail_count, "total": len(user_ids)}

async def send_daily_report(bot: Bot):
    """Send daily stats report to admin."""
    if not ADMIN_IDS:
        return
    stats = await db.get_stats()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    db_type = "MongoDB Atlas (Bulut)" if db.is_connected else "Mahalliy JSON"
    
    report = (
        f"📊 *Kunlik Bot Hisoboti ({now_str})*\n\n"
        f"👥 *Jami foydalanuvchilar:* {stats.get('users', 0)} ta\n"
        f"📝 *Tayyorlangan mustaqil ishlar:* {stats.get('requests', 0)} ta\n"
        f"🗄 *Ma'lumotlar bazasi:* {db_type}\n"
        f"💾 *Kesh hajmi:* {len(essay_cache)} ta mavzu\n"
        f"🌐 *Holat:* Barcha tizimlar normal ishlamoqda."
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=report, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Daily report to {admin_id} failed: {e}")

async def daily_report_scheduler(bot: Bot):
    """Run daily report every 24 hours (86400 seconds)."""
    while True:
        await asyncio.sleep(86400)
        try:
            await send_daily_report(bot)
        except Exception as e:
            logger.error(f"Daily report error: {e}")

# Web Admin Dashboard HTML Handler
async def web_admin_dashboard_handler(request: web.Request) -> web.Response:
    stats = await db.get_stats()
    b_state = await db.get_backup_state()
    
    html = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Mustaqil Ish Bot - Web Admin Panel</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 20px; }}
        h1 {{ margin: 0; color: #38bdf8; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }}
        .card-title {{ font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
        .card-val {{ font-size: 32px; font-weight: bold; margin-top: 10px; color: #f1f5f9; }}
        .status-badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; background: #059669; color: white; }}
        .footer {{ margin-top: 40px; text-align: center; color: #64748b; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🤖 Mustaqil Ish Bot Dashboard</h1>
                <p style="color: #94a3b8; margin: 5px 0 0 0;">24/7 Monitoring va Boshqaruv Tizimi</p>
            </div>
            <span class="status-badge">● LIVE TIZIM</span>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">Foydalanuvchilar</div>
                <div class="card-val">{stats.get('users', 0)}</div>
            </div>
            <div class="card">
                <div class="card-title">Yozilgan Ishlar</div>
                <div class="card-val">{stats.get('requests', 0)}</div>
            </div>
            <div class="card">
                <div class="card-title">Ma'lumotlar Bazasi</div>
                <div class="card-val" style="font-size: 20px; color: #38bdf8;">{'MongoDB Atlas' if db.is_connected else 'Mahalliy JSON'}</div>
            </div>
            <div class="card">
                <div class="card-title">Backup Kanali</div>
                <div class="card-val" style="font-size: 20px; color: #a855f7;">{b_state.get('channel', '@soul_backups')}</div>
            </div>
        </div>

        <div class="card" style="margin-top: 30px;">
            <h3>🛡 Kiberxavfsizlik va Barqarorlik (Father Mode v6.0)</h3>
            <p style="color: #94a3b8;">Avtomatik API Key Rotation (3 ta zaxira server), Anti-Spam Rate-Limiter va In-Memory LRU kesh tizimi faol.</p>
        </div>

        <div class="footer">
            &copy; 2026 Mustaqil Ish Bot. Barcha huquqlar himoyalangan.
        </div>
    </div>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html; charset=utf-8")
