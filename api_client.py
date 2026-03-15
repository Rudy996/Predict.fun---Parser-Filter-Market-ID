import re
from datetime import date, datetime
from typing import Any

import requests


def fetch_market(base_url: str, api_key: str, market_id: int) -> dict[str, Any] | None:
    """GET /v1/markets/{id}. Возвращает data маркета или None при ошибке."""
    url = f"{base_url.rstrip('/')}/v1/markets/{market_id}"
    resp = requests.get(url, headers={"x-api-key": api_key}, timeout=30)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if not data.get("success"):
        return None
    return data.get("data")


def parse_end_date(market: dict[str, Any], date_field_order: list[str]) -> date | None:
    """Из объекта маркета извлечь дату окончания (первое найденное поле из списка)."""
    for field in date_field_order:
        raw = market.get(field)
        if raw is None or raw == "":
            continue
        if isinstance(raw, date):
            return raw
        if isinstance(raw, datetime):
            return raw.date()
        s = str(raw).strip()
        if not s:
            continue
        try:
            dt = datetime.fromisoformat(re.sub(r"Z$", "+00:00", s))
            return dt.date()
        except (ValueError, TypeError):
            continue
    return None


def fetch_all_markets(base_url: str, api_key: str) -> list[dict[str, Any]]:
    """
    Запросы GET /v1/markets без фильтров, с пагинацией.
    Возвращает список полных объектов маркетов (id, status, boostEndsAt и т.д.).
    """
    markets: list[dict[str, Any]] = []
    url = f"{base_url.rstrip('/')}/v1/markets"
    headers = {"x-api-key": api_key}
    params: dict = {"first": "100"}
    after: str | None = None

    while True:
        if after is not None:
            params["after"] = after
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError("API returned success=false")
        items = data.get("data") or []
        markets.extend(items)
        cursor = data.get("cursor")
        if not cursor:
            break
        after = cursor
        params = {"first": "100"}

    return markets


def fetch_market_ids_by_tag(base_url: str, api_key: str, tag_id: str) -> set[int]:
    """
    Запросы GET /v1/markets?tagIds=tag_id с пагинацией.
    Возвращает множество market id из всех страниц.
    """
    ids: set[int] = set()
    url = f"{base_url.rstrip('/')}/v1/markets"
    headers = {"x-api-key": api_key}
    params: dict = {"first": "100", "tagIds": tag_id}
    after: str | None = None

    while True:
        if after is not None:
            params["after"] = after
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError("API returned success=false")
        items = data.get("data") or []
        for m in items:
            mid = m.get("id")
            if mid is not None:
                ids.add(int(mid))
        cursor = data.get("cursor")
        if not cursor:
            break
        after = cursor
        params = {"first": "100", "tagIds": tag_id}

    return ids
