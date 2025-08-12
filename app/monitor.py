#!/usr/bin/env python3
import os
import sys
import time
from alert import tg_send 
from data import update_height, get_latest_height_from_chain, read_height_from_file
from dotenv import load_dotenv
from lcd import page_through_txs_or, build_event_clauses
from utils import create_mintscan_url
from logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

WALLET_ADDRESS = os.getenv("AXELAR_WALLET")
if not WALLET_ADDRESS:
    logger.error("Set AXELAR_WALLET to a bech32 address (axelar1...)")
    sys.exit(1)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))

def monitor_loop():
    old_height = read_height_from_file()
    new_height = get_latest_height_from_chain()

    logger.info(f"Monitoring {WALLET_ADDRESS} on Axelar. Starting from height: {old_height}")

    while True:
        try:
            clauses = build_event_clauses(WALLET_ADDRESS)

            logger.debug(f"Built event clauses: {clauses} - from {old_height} to {new_height}")

            txs = page_through_txs_or(clauses, start_height=old_height, end_height=new_height, page_limit=1, limit_pages=1)
            txs.sort(key=lambda t: int(t.get("height", 0)))
            for tx in txs:
                txhash = tx.get("txhash")
                tg_send(create_mintscan_url(txhash))

        except Exception as e:
            logger.error(f"poll error: {e}")

        new_height += 1
        update_height(new_height)
        logger.info(f"Updating height storage: {new_height}")

        old_height = new_height
        new_height = get_latest_height_from_chain()

        time.sleep(POLL_INTERVAL)

