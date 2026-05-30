import subprocess
import os
from datetime import datetime
import structlog

logger = structlog.get_logger()

BACKUP_DIR = os.path.join(os.path.dirname(__file__), "../../../../backups")
DB_CONTAINER = "exyra_mysql"
DB_USER = "exyra"
DB_PASS = "exyra_pass_2024"
DB_NAME = "exyra_meet"


def run_backup(reason: str = "manual") -> dict:
    """Run a MySQL dump backup. Non-blocking — returns immediately with result."""
    os.makedirs(os.path.abspath(BACKUP_DIR), exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exyra_meet_{timestamp}.sql"
    filepath = os.path.abspath(os.path.join(BACKUP_DIR, filename))

    try:
        result = subprocess.run(
            [
                "docker", "exec", DB_CONTAINER,
                "mysqldump",
                f"-u{DB_USER}", f"-p{DB_PASS}",
                "--single-transaction", "--routines", "--triggers",
                DB_NAME,
            ],
            capture_output=True,
            timeout=60,
        )

        if result.returncode == 0 and result.stdout:
            with open(filepath, "wb") as f:
                f.write(result.stdout)

            size_kb = os.path.getsize(filepath) // 1024
            logger.info("Backup created", file=filename, size_kb=size_kb, reason=reason)

            # Keep only last 14 backups
            _cleanup_old_backups()

            return {"success": True, "file": filename, "size_kb": size_kb}
        else:
            logger.warning("Backup skipped (Docker/MySQL not available)", reason=reason)
            return {"success": False, "error": "Docker or MySQL not available"}

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.warning("Backup failed", error=str(e), reason=reason)
        return {"success": False, "error": str(e)}


def _cleanup_old_backups(keep: int = 14):
    backup_dir = os.path.abspath(BACKUP_DIR)
    try:
        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".sql")],
            reverse=True,
        )
        for old in files[keep:]:
            os.remove(os.path.join(backup_dir, old))
    except Exception:
        pass


def list_backups() -> list:
    backup_dir = os.path.abspath(BACKUP_DIR)
    try:
        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith(".sql")],
            reverse=True,
        )
        result = []
        for f in files:
            path = os.path.join(backup_dir, f)
            size_kb = os.path.getsize(path) // 1024
            result.append({"file": f, "size_kb": size_kb})
        return result
    except Exception:
        return []
