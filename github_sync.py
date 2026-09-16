import os
import base64
import urllib.request
import urllib.error
import json
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GitHubSync")

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "soulpaupau2ooo-creator"
REPO = "Soul"
BRANCH = "main"

FILES_TO_SYNC = [
    "bot.py",
    "economics_curriculum.py",
    "database.py",
    "academic_tools.py",
    "multimodal_handler.py",
    "admin_suite.py",
    "backup_manager.py",
    "requirements.txt",
    ".gitignore",
    "README.md",
    "SESSION_STATE.md",
    "tts/__init__.py",
    "tts/service.py",
    "tts/uzbek_normalizer.py",
    "tts/audio_post.py",
    "tts/foreign_words.json",
    "docs/TTS_AUDIT.md",
    "docs/TTS_BENCHMARK.md",
    "docs/TTS.md"
]

def github_request(endpoint: str, method: str = "GET", data: dict = None):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/{endpoint}"
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHubSync-Script"
    }
    if encoded_data:
        headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, data=encoded_data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def sync_all_atomic(commit_msg: str) -> bool:
    """Upload all files in a single atomic Git commit so Render triggers only ONE clean deploy."""
    logger.info(f"🚀 Atomik GitHub sinxronizatsiyasi: {OWNER}/{REPO} ({BRANCH} branch)")
    
    try:
        # 1. Get HEAD commit
        ref_data = github_request(f"git/ref/heads/{BRANCH}")
        latest_commit_sha = ref_data["object"]["sha"]
        logger.info(f"📌 Joriy commit SHA: {latest_commit_sha[:7]}")
        
        # 2. Get tree of HEAD commit
        commit_data = github_request(f"git/commits/{latest_commit_sha}")
        base_tree_sha = commit_data["tree"]["sha"]
        
        # 3. Create blobs for each file
        tree_items = []
        for rel_path in FILES_TO_SYNC:
            if not os.path.exists(rel_path):
                logger.warning(f"⚠️ Fayl topilmadi: {rel_path}")
                continue
                
            with open(rel_path, "rb") as f:
                raw_bytes = f.read()
                
            b64_str = base64.b64encode(raw_bytes).decode("utf-8")
            blob_res = github_request("git/blobs", method="POST", data={
                "content": b64_str,
                "encoding": "base64"
            })
            blob_sha = blob_res["sha"]
            tree_items.append({
                "path": rel_path.replace("\\", "/"),
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })
            logger.info(f"  📄 Blob tayyorlandi: {rel_path} -> {blob_sha[:7]}")
            
        # 4. Create new tree
        new_tree_res = github_request("git/trees", method="POST", data={
            "base_tree": base_tree_sha,
            "tree": tree_items
        })
        new_tree_sha = new_tree_res["sha"]
        logger.info(f"🌳 Yangi Tree SHA: {new_tree_sha[:7]}")
        
        # 5. Create new commit
        new_commit_res = github_request("git/commits", method="POST", data={
            "message": commit_msg,
            "tree": new_tree_sha,
            "parents": [latest_commit_sha]
        })
        new_commit_sha = new_commit_res["sha"]
        logger.info(f"📝 Yangi Commit SHA: {new_commit_sha[:7]}")
        
        # 6. Update branch ref
        github_request(f"git/refs/heads/{BRANCH}", method="PATCH", data={
            "sha": new_commit_sha,
            "force": False
        })
        logger.info(f"✅ Muvaffaqiyatli! Barcha {len(tree_items)} ta fayl YAGONA atomik commitda yuklandi: {new_commit_sha[:7]}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Atomik yuklashda xatolik: {e}")
        return False

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Production atomic release: Soulbekbot v6.2"
    success = sync_all_atomic(msg)
    if not success:
        sys.exit(1)
