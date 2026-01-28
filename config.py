import os
import sys
import tomllib
import logging
from pathlib import Path

with open('config.toml', 'rb') as fp:
    CONFIG = tomllib.load(fp)
    
log_dir = Path(__file__).parent / CONFIG['logging']['log_dir']
if not(os.path.exists(log_dir)):
    os.mkdir(log_dir)

filename = Path(sys.argv[0]).name
logging.basicConfig(
    filename=f"{log_dir}/{filename.split(".")[0]}.log",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
    datefmt="%d-%m-%Y %H:%M:%S",
    level=CONFIG['logging']['level']
)

logger = logging.getLogger()
logger.info("Code started")
logger.info("Config loaded")