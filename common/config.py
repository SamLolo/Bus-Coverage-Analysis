import os
import sys
import tomllib
import logging
from pathlib import Path

with open(Path(__file__).parent.parent / 'config.toml', 'rb') as fp:
    CONFIG = tomllib.load(fp)
    
LOG_DIR: Path = Path(__file__).parent.parent / CONFIG['logging']['log_dir']
if not(os.path.exists(LOG_DIR)):
    os.mkdir(LOG_DIR)

filename = Path(sys.argv[0]).parent.name + "." + Path(sys.argv[0]).name.split(".")[0] + ".log"
logging.basicConfig(
    filename=LOG_DIR / filename,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
    datefmt="%d-%m-%Y %H:%M:%S",
    level=CONFIG['logging']['level']
)

logger = logging.getLogger()
logger.info("Code started")
logger.info("Config loaded")