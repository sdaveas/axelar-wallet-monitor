import os
import sys
import requests
import logging

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your environment variables.")
    sys.exit(1)

def tg_send(text: str) -> None:
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
        if resp.status_code != 200:
            logger.error(f"Telegram send failed: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"Telegram send exception: {e}")
