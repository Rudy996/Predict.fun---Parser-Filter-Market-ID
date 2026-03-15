import time
from datetime import date

from api_client import fetch_market, fetch_market_ids_by_tag, parse_end_date


def collect_ids_to_remove(
    base_url: str,
    api_key: str,
    exclude_tag_ids: list[str],
) -> set[int]:
    """Собрать все market id из ответов по каждому exclude_tag_id."""
    ids_to_remove: set[int] = set()
    for tag_id in exclude_tag_ids:
        ids_to_remove |= fetch_market_ids_by_tag(base_url, api_key, tag_id)
    return ids_to_remove


def subtract_from_list(market_ids: list[int], ids_to_remove: set[int]) -> list[int]:
    """Вернуть market_ids без тех id, что в ids_to_remove (порядок сохраняем)."""
    remove = ids_to_remove
    return [mid for mid in market_ids if mid not in remove]


def _market_matches_status(market: dict | None, required_status: str | None) -> bool:
    if required_status is None or required_status == "":
        return True
    if market is None:
        return False
    return (market.get("status") or "").upper() == required_status.upper()


def filter_by_status(
    base_url: str,
    api_key: str,
    market_ids: list[int],
    required_status: str,
) -> list[int]:
    """Оставить только маркеты с указанным статусом (например REGISTERED)."""
    result: list[int] = []
    for i, mid in enumerate(market_ids):
        if i > 0:
            time.sleep(0.15)
        market = fetch_market(base_url, api_key, mid)
        if _market_matches_status(market, required_status):
            result.append(mid)
    return result


def filter_by_min_days_until_end(
    base_url: str,
    api_key: str,
    market_ids: list[int],
    min_days: int,
    date_field_order: list[str],
    required_status: str | None = None,
) -> list[int]:
    """Оставить только маркеты, у которых до даты окончания >= min_days дней и при необходимости статус совпадает."""
    today = date.today()
    result: list[int] = []
    for i, mid in enumerate(market_ids):
        if i > 0:
            time.sleep(0.15)
        market = fetch_market(base_url, api_key, mid)
        if market is None:
            if required_status is None:
                result.append(mid)
            continue
        if not _market_matches_status(market, required_status):
            continue
        end = parse_end_date(market, date_field_order)
        if end is None:
            result.append(mid)
            continue
        days_left = (end - today).days
        if days_left >= min_days:
            result.append(mid)
    return result
