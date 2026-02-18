import logging
from pathlib import Path
from r5py.util import Config
from common.data import TEMP_DIR
from common.config import setup_logging

R5PY_CACHE = Config().CACHE_DIR
setup_logging()
logger = logging.getLogger("cleaner")

def clean_dir(dir: Path, extensions: list = []):
    for file in dir.iterdir():
        if len(extensions) == 0 or file.suffix in extensions:
            try:
                file.unlink()
                logger.debug(f"Removed file: {file}")
            except PermissionError:
                logger.warning(f"Permissions error encountered when trying to remove file: {file}")
            except Exception:
                logger.exception(f"Unknown error when trying to remove file: {file}")

if __name__ == "__main__":
    logger.info("Starting cleanup")
    clean_dir(TEMP_DIR, [".pbf"])
    logger.info("Cleaned tempory directory")
    clean_dir(R5PY_CACHE, [".pbf", ".p", ".mapdb", ".transport_network"])
    logger.info("Cleaned r5py cache")