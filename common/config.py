import os
import sys
import tomllib
import logging
from pathlib import Path

# Load config from toml file
with open(Path(__file__).parent.parent / 'config.toml', 'rb') as fp:
    CONFIG = tomllib.load(fp)

# Create log directory if it doesn't exist
LOG_DIR: Path = Path(__file__).parent.parent / CONFIG['logging']['log_dir']
if not(os.path.exists(LOG_DIR)):
    os.mkdir(LOG_DIR)

def setup_logging():
    """
    Helper function to setup logging for a given parent file. 
    Without a call to this at the top of a script, logging will not be enabled.
    Log files take the name of their parent (the Python script run first).
    """
    # Form filename using parent file path
    filename = Path(sys.argv[0]).parent.name + "." + Path(sys.argv[0]).name.split(".")[0] + ".log"
    
    # Setup logging config
    logging.basicConfig(
        filename=LOG_DIR / filename,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
        datefmt="%d-%m-%Y %H:%M:%S",
        level=CONFIG['logging']['level']
    )

    # Ouput start-up message to root logger
    logger = logging.getLogger()
    logger.info("Code started")
    logger.info("Config loaded")