import logging
import os
from logging.handlers import RotatingFileHandler

# Configuración del Directorio de Logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "cpsl_system.log")

# Configurar formateador unificado
formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(module)-15s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Evitar handlers duplicados si se instancia varias veces
    if not logger.handlers:
        # Handler para Consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler para Archivo Rotativo (Máximo 5MB por archivo, conserva 3 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Logger por defecto
log = get_logger("CPSL_CORE")
