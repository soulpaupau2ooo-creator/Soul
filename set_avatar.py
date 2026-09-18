from __future__ import annotations
import json
import logging
import os
import sys
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("set_avatar")


def load_token_from_env(env_path: Path) -> str | None:
    token = os.getenv("BOT_TOKEN")
    if token:
        return token.strip()
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("BOT_TOKEN="):
                    val = stripped.split("=", 1)[1].strip()
                    if val:
                        return val
    return None


def set_bot_profile_photo(photo_path: Path, env_path: Path) -> bool:
    if not photo_path.exists():
        logger.error(f"Avatar file not found: {photo_path}")
        return False

    token = load_token_from_env(env_path)
    if not token:
        logger.error("BOT_TOKEN could not be found in environment or .env file.")
        return False

    url = f"https://api.telegram.org/bot{token}/setMyProfilePhoto"
    logger.info(f"Uploading avatar from {photo_path.name} to Telegram Bot API...")
    try:
        with open(photo_path, "rb") as photo_file:
            files = {"bot_profile_jpg": ("avatar.jpg", photo_file, "image/jpeg")}
            payload = {
                "photo": json.dumps({
                    "type": "static",
                    "photo": "attach://bot_profile_jpg"
                })
            }
            resp = requests.post(url, data=payload, files=files, timeout=30)
            d = resp.json()
            if resp.status_code == 200 and d.get("ok"):
                logger.info("Avatar successfully updated on Telegram!")
                return True
            else:
                desc = d.get("description", "Unknown error")
                logger.error(f"Failed to update avatar: {desc}")
                return False
    except Exception as e:
        logger.error(f"Network/Execution error: {e}")
        return False


def main() -> None:
    base = Path(__file__).resolve().parent
    env_file = base / ".env"
    avatar_path = base / "bot_avatar.jpg"
    if len(sys.argv) > 1:
        avatar_path = Path(sys.argv[1]).resolve()
    success = set_bot_profile_photo(avatar_path, env_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
