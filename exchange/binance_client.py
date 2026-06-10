# Copilot prompt:
# "Implement minimal Binance Futures wrapper: get_price(symbol), get_open_positions(), close_position(symbol, side, qty).
# Use requests, retries with exponential backoff, handle HTTP errors and rate limits. Do not include secrets."
import time
import requests
import logging
from typing import List, Dict, Any
from ..config import settings

logger = logging.getLogger("binance_client")

class BinanceAPIError(Exception):
    pass

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.base = "https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com"
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})

    def _request_with_retry(self, method: str, path: str, params: dict = None, json: dict = None, max_retries: int = 3) -> dict:
        backoff = 1.0
        url = f"{self.base}{path}"
        for attempt in range(1, max_retries + 1):
            try:
                r = self.session.request(method, url, params=params, json=json, timeout=10)
                if r.status_code == 429 or r.status_code == 418:
                    # rate limit or banned
                    retry_after = int(r.headers.get("Retry-After", "1"))
                    logger.warning("Rate limited by Binance. Retry after %s", retry_after)
                    time.sleep(retry_after + 1)
                    continue
                if r.status_code >= 400:
                    raise BinanceAPIError(f"{r.status_code}: {r.text}")
                return r.json()
            except requests.RequestException as e:
                logger.warning("Request error: %s; attempt %s/%s", e, attempt, max_retries)
                time.sleep(backoff)
                backoff *= 2
        raise BinanceAPIError("Max retries exceeded")

    def get_price(self, symbol: str) -> float:
        data = self._request_with_retry("GET", "/fapi/v1/premiumIndex", params={"symbol": symbol})
        # premiumIndex endpoint includes markPrice
        return float(data.get("markPrice") or data.get("lastPrice"))

    def get_open_positions(self) -> List[Dict[str, Any]]:
        # positionRisk gives per-symbol position info
        data = self._request_with_retry("GET", "/fapi/v2/positionRisk")
        return data

    def close_position(self, symbol: str, side: str, quantity: float):
        # To close a position, send a market order in the opposite side
        # side: 'BUY' or 'SELL' — to close a long, send SELL market
        side_for_order = "SELL" if side.upper() == "BUY" else "BUY"
        payload = {
            "symbol": symbol,
            "side": side_for_order,
            "type": "MARKET",
            "quantity": quantity
        }
        data = self._request_with_retry("POST", "/fapi/v1/order", json=payload)
        return data
