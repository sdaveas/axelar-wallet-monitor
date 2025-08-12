import requests
import backoff
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from logger import setup_logger

logger = setup_logger(__name__)

AXELAR_LCD = os.getenv("AXELAR_LCD")
if not AXELAR_LCD:
    logger.error("Set AXELAR_LCD to a valid LCD endpoint")
    sys.exit(1)
else:
    logger.info(f"Using AXELAR_LCD: {AXELAR_LCD}")

@backoff.on_exception(backoff.expo, (requests.RequestException,), max_time=120)
def lcd_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = AXELAR_LCD.rstrip("/") + path
    r = requests.get(url, params=params, timeout=20)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        body = None
        try:
            body = r.text
        except Exception:
            body = "\u003cno body\u003e"
        logger.error(f"LCD GET failed: {r.status_code} {body}")
        raise
    return r.json()


def _fetch_txs_for_events(events: List[str], page_limit: int = 50, limit_pages: int = 5) -> List[Dict[str, Any]]:
    # Query /cosmos/tx/v1beta1/txs using repeated "events" params (AND semantics)
    # events: list like ["message.sender='addr'", "tx.height>=123"]
    results: List[Dict[str, Any]] = []
    next_key: Optional[str] = None
    for _ in range(limit_pages):
        query_params: List[Tuple[str, str]] = [("pagination.limit", str(page_limit))]
        for ev in events:
            query_params.append(("events", ev))
        if next_key:
            query_params.append(("pagination.key", next_key))
        data = lcd_get("/cosmos/tx/v1beta1/txs", params=query_params)
        txs = data.get("tx_responses", [])
        results.extend(txs)
        next_key = data.get("pagination", {}).get("next_key")
        if not next_key:
            break
    return results


def page_through_txs_or(clauses: List[str], start_height: Optional[int], page_limit: int = 50, limit_pages: int = 3) -> List[Dict[str, Any]]:
    # Simulate OR across different event clauses by issuing separate queries and merging results
    seen_hashes: set[str] = set()
    merged: List[Dict[str, Any]] = []
    height_ev = f"tx.height>={start_height}" if start_height else None
    for clause in clauses:
        evs = [clause]
        if height_ev:
            evs.append(height_ev)
        txs = _fetch_txs_for_events(evs, page_limit=page_limit, limit_pages=limit_pages)
        for tx in txs:
            h = tx.get("txhash")
            if h and h not in seen_hashes:
                seen_hashes.add(h)
                merged.append(tx)
    return merged


def build_event_clauses(addr: str) -> List[str]:
    return [
        f"transfer.sender='{addr}'",
        f"transfer.recipient='{addr}'",
        # f"message.sender='{addr}'",
        # f"message.signer='{addr}'",
        # f"delegate.delegator_address='{addr}'",
        # f"redelegate.delegator_address='{addr}'",
        # f"unbond.delegator_address='{addr}'",
        # f"unbond.validator_address='{addr}'",
    ]
