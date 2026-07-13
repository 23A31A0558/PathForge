# backend/ai/logger.py

import logging
import sys
from pathlib import Path

# Setup logging
log_file = Path(__file__).resolve().parent.parent / "ai_generation.log"
logger = logging.getLogger("ai_generation")
logger.setLevel(logging.INFO)

# Avoid adding multiple handlers if re-imported
if not logger.handlers:
    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
