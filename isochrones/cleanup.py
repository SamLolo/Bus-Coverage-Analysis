import logging
from pathlib import Path
from r5py.util import Config
from common.data import TEMP_DIR
from common.config import setup_logging

# Get path of r5py cache directory
R5PY_CACHE = Config().CACHE_DIR

# Start logging
setup_logging()
logger = logging.getLogger("cleaner")

def clean_dir(dir: Path, extensions: list = []):
    """
    Removes all files within a given directory. Optionally, a list of file extensions can be included
    to control which files are deleted. The directory itself is not removed.

    Args:
        dir (pathlib.Path): The directory to remove files from.
        extensions (list, optional): A list of strings representing file extensions to delete. Defaults to [].
    """
    for file in dir.iterdir():
        if len(extensions) == 0 or file.suffix in extensions:
            try:
                file.unlink()
                logger.debug(f"Removed file: {file}")
            except PermissionError:
                logger.warning(f"Permissions error encountered when trying to remove file: {file}")
            except Exception:
                logger.exception(f"Unknown error when trying to remove file: {file}")

# Clean both directories when run directly
if __name__ == "__main__":
    logger.info("Starting cleanup")
    clean_dir(TEMP_DIR, [".pbf"])
    logger.info("Cleaned tempory directory")
    clean_dir(R5PY_CACHE, [".pbf", ".p", ".mapdb", ".transport_network"])
    logger.info("Cleaned r5py cache")