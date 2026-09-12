import os
import asyncio
import logging
import urllib.request
import urllib.error
import json
from datetime import datetime
from typing import Optional, Tuple

from aiogram import Bot
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv

from database import db

load_dotenv()
logger = logging.getLogger("BackupManager")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "soulpaupau2ooo-creator/Soul")
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL_SECONDS", 1800))  # 30 minutes

def fetch_github_backup_zip() -> Optional[bytes]:
    """Download repository zipball from GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/zipball/main"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Soulbekbot-Backup-System"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except Exception as e:
        logger.error(f"GitHub ZIP yuklab olishda xatolik: {e}")
        return None

def fetch_latest_commit() -> Tuple[str, str]:
    """Fetch latest commit SHA and commit message."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Soulbekbot-Backup-System"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha", "")[:7]
            msg = data.get("commit", {}).get("message", "").splitlines()[0]
            return sha, msg
    except Exception as e:
        logger.error(f"GitHub oxirgi commitni olishda xato: {e}")
        return "latest", "Avtomatik zaxira nusxasi"

async def perform_backup(bot: Bot, target_channel: Optional[str] = None) -> bool:
    """Perform a backup: delete previous message and send latest zipball."""
    state = await db.get_backup_state()
    channel = target_channel or state.get("channel") or os.getenv("BACKUP_CHANNEL", "@soul_backups")
    
    if not channel:
        logger.info("ℹ️ Backup kanali hali belgilanmagan (/set_backup @kanal buyrug'ini yuboring).")
        return False

    logger.info(f"🚀 {channel} kanaliga GitHub backup yuborish boshlanmoqda...")
    
    # 1. Fetch ZIP and Commit
    zip_bytes = await asyncio.to_thread(fetch_github_backup_zip)
    if not zip_bytes:
        logger.error("❌ ZIP fayl yuklab olinmadi. Backup to'xtatildi.")
        return False
        
    sha, msg = await asyncio.to_thread(fetch_latest_commit)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = f"Soul_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"

    # 2. Delete previous backup message if recorded
    last_msg_id = state.get("last_message_id")
    if last_msg_id:
        try:
            await bot.delete_message(chat_id=channel, message_id=last_msg_id)
            logger.info(f"🗑 Avvalgi backup xabari ({last_msg_id}) kanaldan muvaffaqiyatli o'chirildi.")
        except Exception as e:
            logger.warning(f"Avvalgi backup xabarini o'chirishda ogohlantirish (balki qo'lda o'chirilgan): {e}")

    # 3. Send new backup message
    caption = (
        f"📦 *Mustaqil Ish Bot — GitHub Zaxira Nusxasi (Backup)*\n\n"
        f"📅 *Vaqt:* `{now_str}`\n"
        f"📂 *Ombor:* `{GITHUB_REPO}`\n"
        f"🔖 *Commit:* `{sha}`\n"
        f"💬 *Izoh:* _{msg}_\n"
        f"⏱ *Davriylik:* Har 30 daqiqada yangilanadi\n\n"
        f"♻️ *Kanal tozaligi:* Yangi backup kelishi bilan avvalgisi avtomatik o'chirildi. Kanalda doimo eng so'nggi holat saqlanadi."
    )

    try:
        file_obj = BufferedInputFile(zip_bytes, filename=filename)
        sent = await bot.send_document(
            chat_id=channel,
            document=file_obj,
            caption=caption,
            parse_mode="Markdown"
        )
        await db.update_backup_state(channel=str(channel), last_message_id=sent.message_id)
        logger.info(f"✅ Yangi backup muvaffaqiyatli yuborildi! Message ID: {sent.message_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Backupni Telegram kanalga yuborishda xatolik: {e}")
        return False

async def backup_scheduler_loop(bot: Bot):
    """Background task running every 30 minutes."""
    logger.info(f"⏰ Backup taymer ishga tushdi (Har {BACKUP_INTERVAL // 60} daqiqada).")
    # Wait 10 seconds on startup before first check
    await asyncio.sleep(10)
    
    while True:
        try:
            await perform_backup(bot)
        except Exception as e:
            logger.error(f"Backup taymer xatolik: {e}")
            
        await asyncio.sleep(BACKUP_INTERVAL)
