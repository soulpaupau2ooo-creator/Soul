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
        self.settings_col = None
        self.is_connected = False

    async def connect(self):
        """Connect to MongoDB Atlas, fallback to local JSON if not available."""
        if MONGO_URI and "mongodb" in MONGO_URI:
            try:
                self.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                await self.client.admin.command('ping')
                self.db = self.client.get_database("soulbekbot_db")
                self.users_col = self.db.get_collection("users")
                self.logs_col = self.db.get_collection("requests")
                self.settings_col = self.db.get_collection("settings")
                self.is_connected = True
                logger.info("✅ MongoDB Atlas ga muvaffaqiyatli ulandi!")
                return
            except Exception as e:
                logger.warning(f"⚠️ MongoDB ga ulanib bo'lmadi ({e}). Mahalliy JSON bazaga o'tilmoqda.")
                self.is_connected = False
        else:
            logger.info("ℹ️ MONGO_URI ko'rsatilmagan. Mahalliy JSON baza ishlatiladi.")
            self.is_connected = False

        if not os.path.exists(LOCAL_DB_FILE):
            self._save_local({"users": {}, "requests": [], "backup_state": {}})

    def _load_local(self) -> Dict[str, Any]:
        try:
            if os.path.exists(LOCAL_DB_FILE):
                with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Mahalliy bazani o'qishda xatolik: {e}")
        return {"users": {}, "requests": [], "backup_state": {}}

    def _save_local(self, data: Dict[str, Any]):
        try:
            with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Mahalliy bazaga yozishda xatolik: {e}")

    async def add_or_update_user(self, user_id: int, full_name: str, username: Optional[str] = None):
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

        data = self._load_local()
        uid = str(user_id)
        if uid not in data.get("users", {}):
            user_data["joined_at"] = now
            if "users" not in data:
                data["users"] = {}
            data["users"][uid] = user_data
        else:
            data["users"][uid]["last_active"] = now
            data["users"][uid]["full_name"] = full_name
            data["users"][uid]["username"] = username or ""
        self._save_local(data)

    async def log_request(self, user_id: int, subject: str, topic: str):
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

        data = self._load_local()
        if "requests" not in data:
            data["requests"] = []
        data["requests"].append(log_entry)
        self._save_local(data)

    async def get_stats(self) -> Dict[str, int]:
        if self.is_connected and self.users_col is not None and self.logs_col is not None:
            try:
                total_users = await self.users_col.count_documents({})
                total_requests = await self.logs_col.count_documents({})
                return {"users": total_users, "requests": total_requests}
            except Exception as e:
                logger.error(f"MongoDB stats xatolik: {e}")

        data = self._load_local()
        return {
            "users": len(data.get("users", {})),
            "requests": len(data.get("requests", []))
        }

    async def get_backup_state(self) -> Dict[str, Any]:
        """Get backup channel and last sent message ID."""
        if self.is_connected and self.settings_col is not None:
            try:
                doc = await self.settings_col.find_one({"key": "backup_state"})
                if doc:
                    return doc.get("value", {})
            except Exception as e:
                logger.error(f"MongoDB backup_state olishda xato: {e}")

        data = self._load_local()
        return data.get("backup_state", {})

    async def update_backup_state(self, channel: Optional[str] = None, last_message_id: Optional[int] = None):
        """Update backup channel and/or last sent message ID."""
        current = await self.get_backup_state()
        if channel is not None:
            current["channel"] = channel
        if last_message_id is not None:
            current["last_message_id"] = last_message_id
        current["updated_at"] = datetime.now().isoformat()

        if self.is_connected and self.settings_col is not None:
            try:
                await self.settings_col.update_one(
                    {"key": "backup_state"},
                    {"$set": {"key": "backup_state", "value": current}},
                    upsert=True
                )
                return
            except Exception as e:
                logger.error(f"MongoDB backup_state saqlashda xato: {e}")

        data = self._load_local()
        data["backup_state"] = current
        self._save_local(data)

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user details."""
        if self.is_connected and self.users_col is not None:
            try:
                return await self.users_col.find_one({"user_id": user_id})
            except Exception as e:
                logger.error(f"Error fetching user {user_id}: {e}")
        data = self._load_local()
        return data.get("users", {}).get(str(user_id))

    async def set_user_language(self, user_id: int, lang: str):
        """Update user interface language."""
        if self.is_connected and self.users_col is not None:
            try:
                await self.users_col.update_one({"user_id": user_id}, {"$set": {"lang": lang}}, upsert=True)
                return
            except Exception as e:
                logger.error(f"Error setting lang: {e}")
        data = self._load_local()
        uid = str(user_id)
        if uid in data.get("users", {}):
            data["users"][uid]["lang"] = lang
            self._save_local(data)

    async def get_user_language(self, user_id: int) -> str:
        """Get user interface language."""
        user = await self.get_user(user_id)
        if user and "lang" in user:
            return user["lang"]
        return "uz"

    async def add_referral(self, inviter_id: int, new_user_id: int) -> bool:
        """Add referral point if user is newly invited."""
        if inviter_id == new_user_id:
            return False
            
        inviter = await self.get_user(inviter_id)
        if not inviter:
            return False

        if self.is_connected and self.users_col is not None:
            try:
                # Check if already referred
                new_user = await self.users_col.find_one({"user_id": new_user_id})
                if new_user and new_user.get("referred_by"):
                    return False
                await self.users_col.update_one({"user_id": new_user_id}, {"$set": {"referred_by": inviter_id}}, upsert=True)
                await self.users_col.update_one({"user_id": inviter_id}, {"$inc": {"referral_count": 1, "points": 10}}, upsert=True)
                return True
            except Exception as e:
                logger.error(f"Error adding referral: {e}")
                return False
                
        data = self._load_local()
        n_uid = str(new_user_id)
        i_uid = str(inviter_id)
        if n_uid in data.get("users", {}) and data["users"][n_uid].get("referred_by"):
            return False
        if i_uid in data.get("users", {}):
            if "referral_count" not in data["users"][i_uid]:
                data["users"][i_uid]["referral_count"] = 0
                data["users"][i_uid]["points"] = 0
            data["users"][i_uid]["referral_count"] += 1
            data["users"][i_uid]["points"] += 10
            if n_uid in data.get("users", {}):
                data["users"][n_uid]["referred_by"] = inviter_id
            self._save_local(data)
            return True
        return False

    async def is_banned(self, user_id: int) -> bool:
        """Check if user is in blacklist."""
        user = await self.get_user(user_id)
        return bool(user and user.get("is_banned"))

    async def set_ban_status(self, user_id: int, is_banned: bool):
        """Ban or unban user."""
        if self.is_connected and self.users_col is not None:
            try:
                await self.users_col.update_one({"user_id": user_id}, {"$set": {"is_banned": is_banned}}, upsert=True)
                return
            except Exception as e:
                logger.error(f"Error setting ban status: {e}")
        data = self._load_local()
        uid = str(user_id)
        if uid in data.get("users", {}):
            data["users"][uid]["is_banned"] = is_banned
            self._save_local(data)

db = DatabaseManager()
