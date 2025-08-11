#!/usr/bin/env python3
import os
import sys
import time
from alert import tg_send 
from data import get_height, update_height
from dotenv import load_dotenv
from lcd import page_through_txs_or, build_event_clauses
from utils import create_mintscan_url
from .logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

WALLET_ADDRESS = os.getenv("AXELAR_WALLET")
if not WALLET_ADDRESS:
    logger.error("Set AXELAR_WALLET to a bech32 address (axelar1...)")
    sys.exit(1)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))

def monitor_loop():
    height = get_height()

    logger.info(f"Monitoring {WALLET_ADDRESS} on Axelar. Starting from height: {height}")

    while True:
        try:
            clauses = build_event_clauses(WALLET_ADDRESS)
            txs = page_through_txs_or(clauses, start_height=height, page_limit=1, limit_pages=1)
            txs.sort(key=lambda t: int(t.get("height", 0)))
            for tx in txs:
                txhash = tx.get("txhash")
                tg_send(create_mintscan_url(txhash))

        except Exception as e:
            logger.error(f"poll error: {e}")

        time.sleep(POLL_INTERVAL)
        height = update_height()
        logger.info(f"Updated height: {height}")
