import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "")
LOCAL_DB_FILE = "users_db.json"

class DatabaseManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.users_col = None
        self.logs_col = None
        self.is_connected = False

    async def connect(self):
        """Connect to MongoDB Atlas, fallback to local JSON if not available."""
        if MONGO_URI and "mongodb" in MONGO_URI:
            try:
                self.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                # Verify connection
                await self.client.admin.command('ping')
                self.db = self.client.get_database("soulbekbot_db")
                self.users_col = self.db.get_collection("users")
                self.logs_col = self.db.get_collection("requests")
                self.is_connected = True
                logger.info("✅ MongoDB Atlas ga muvaffaqiyatli ulandi!")
                return
            except Exception as e:
                logger.warning(f"⚠️ MongoDB ga ulanib bo'lmadi ({e}). Mahalliy JSON bazaga o'tilmoqda.")
                self.is_connected = False
        else:
            logger.info("ℹ️ MONGO_URI ko'rsatilmagan. Mahalliy JSON baza ishlatiladi.")
            self.is_connected = False

        # Initialize local JSON file if needed
        if not os.path.exists(LOCAL_DB_FILE):
            self._save_local({"users": {}, "requests": []})

    def _load_local(self) -> Dict[str, Any]:
        try:
            if os.path.exists(LOCAL_DB_FILE):
                with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Mahalliy bazani o'qishda xatolik: {e}")
        return {"users": {}, "requests": []}

    def _save_local(self, data: Dict[str, Any]):
        try:
            with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Mahalliy bazaga yozishda xatolik: {e}")

    async def add_or_update_user(self, user_id: int, full_name: str, username: Optional[str] = None):
        """Save or update user in database."""
        now = datetime.now().isoformat()
        user_data = {
            "user_id": user_id,
            "full_name": full_name,
            "username": username or "",
            "last_active": now
        }

        if self.is_connected and self.users_col is not None:
            try:
                await self.users_col.update_one(
                    {"user_id": user_id},
                    {"$set": user_data, "$setOnInsert": {"joined_at": now}},
                    upsert=True
                )
                return
            except Exception as e:
                logger.error(f"MongoDB foydalanuvchi saqlashda xato: {e}")

        # Local fallback
        data = self._load_local()
        uid = str(user_id)
        if uid not in data["users"]:
            user_data["joined_at"] = now
            data["users"][uid] = user_data
        else:
            data["users"][uid]["last_active"] = now
            data["users"][uid]["full_name"] = full_name
            data["users"][uid]["username"] = username or ""
        self._save_local(data)

    async def log_request(self, user_id: int, subject: str, topic: str):
        """Log essay request to database."""
        now = datetime.now().isoformat()
        log_entry = {
            "user_id": user_id,
            "subject": subject,
            "topic": topic,
            "timestamp": now
        }

        if self.is_connected and self.logs_col is not None:
            try:
                await self.logs_col.insert_one(log_entry)
                return
            except Exception as e:
                logger.error(f"MongoDB log saqlashda xato: {e}")

        # Local fallback
        data = self._load_local()
        data["requests"].append(log_entry)
        self._save_local(data)

    async def get_stats(self) -> Dict[str, int]:
        """Get statistics of users and requests."""
        if self.is_connected and self.users_col is not None and self.logs_col is not None:
            try:
                total_users = await self.users_col.count_documents({})
                total_requests = await self.logs_col.count_documents({})
                return {"users": total_users, "requests": total_requests}
            except Exception as e:
                logger.error(f"MongoDB stats xatolik: {e}")

        # Local fallback
        data = self._load_local()
        return {
            "users": len(data.get("users", {})),
            "requests": len(data.get("requests", []))
        }

db = DatabaseManager()
