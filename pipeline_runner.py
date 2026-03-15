"""
Пайплайн фильтрации с пошаговым callback для GUI.

Шаги (индексы динамические):
  0        — ожидаем настроек пользователя (управляется GUI)
  1        — загрузка списка
  2..K+1   — получаем маркеты по тегу (по одному шагу на каждый exclude_tag_id)
  K+2      — вычитаем из нашего списка
  K+3      — проверяем дату и статус (из кеша при use_all_markets, иначе запросы)
  K+4      — сохранение
"""
import time
from datetime import date
from pathlib import Path
from typing import Callable

from api_client import fetch_all_markets, fetch_market, fetch_market_ids_by_tag, parse_end_date


StepCallback = Callable[[int, str, str], None]


def load_market_ids_from_file(path: str) -> list[int]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    text = p.read_text(encoding="utf-8").strip().replace("\n", ",")
    parts = [s.strip() for s in text.split(",") if s.strip()]
    return [int(x) for x in parts]


def _check_market_from_data(
    market: dict | None,
    min_days: int | None,
    require_status: str | None,
    date_fields: list[str],
    today: date,
) -> bool:
    """True если маркет проходит фильтры по дате и статусу (данные уже есть)."""
    if market is None:
        return require_status is None
    if require_status:
        actual = (market.get("status") or "").upper()
        if actual != require_status.upper():
            return False
    if min_days is not None and min_days > 0:
        end = parse_end_date(market, date_fields)
        if end is not None and (end - today).days < min_days:
            return False
    return True


def _check_market(
    base_url: str,
    api_key: str,
    market_id: int,
    min_days: int | None,
    require_status: str | None,
    date_fields: list[str],
    today: date,
) -> bool:
    """True если маркет проходит фильтры (запрос к API)."""
    market = fetch_market(base_url, api_key, market_id)
    return _check_market_from_data(market, min_days, require_status, date_fields, today)


def total_steps(exclude_count: int) -> int:
    return 1 + 1 + exclude_count + 1 + 1 + 1


def run_pipeline(
    api_key: str,
    base_url: str,
    market_ids_file: str | None,
    use_all_markets: bool,
    exclude_tag_ids: list[str],
    exclude_tag_names: list[str],
    min_days_until_end: int | None,
    require_status: str | None,
    output_file: str,
    date_field_order: list[str] | None,
    step_callback: StepCallback,
) -> tuple[list[int], str | None]:
    """
    step_callback(step_index, status, detail):
      status  — "running" | "done" | "skip" | "error"
      detail  — текст для отображения рядом с шагом
    """
    base_url = base_url.rstrip("/")
    date_fields = date_field_order or ["boostEndsAt", "endDate", "resolutionDate"]
    K = len(exclude_tag_ids)
    step_load = 1
    step_subtract = 2 + K
    step_filter = 3 + K
    step_save = 4 + K

    try:
        markets_by_id: dict[int, dict] = {}

        # 1 — загрузка списка (из файла или с API)
        step_callback(step_load, "running", "")
        if use_all_markets:
            markets = fetch_all_markets(base_url, api_key)
            markets_by_id = {int(m["id"]): m for m in markets if m.get("id") is not None}
            market_ids = list(markets_by_id.keys())
            step_callback(step_load, "done", f"Загружено {len(market_ids)} маркетов с Predict.fun")
        else:
            if not market_ids_file:
                return [], "Укажите файл со списком маркетов"
            market_ids = load_market_ids_from_file(market_ids_file)
            step_callback(step_load, "done", f"Загружено {len(market_ids)} id из файла")
        if not market_ids:
            return [], "Список маркетов пуст"

        # 2..K+1 — получаем маркеты по каждому тегу
        ids_to_remove: set[int] = set()
        for i, tag_id in enumerate(exclude_tag_ids):
            name = exclude_tag_names[i] if i < len(exclude_tag_names) else tag_id
            step_callback(2 + i, "running", "")
            tag_ids = fetch_market_ids_by_tag(base_url, api_key, tag_id)
            ids_to_remove |= tag_ids
            step_callback(2 + i, "done", f"Найдено {len(tag_ids)} маркетов по {name}")

        # K+2 — вычитаем
        step_callback(step_subtract, "running", "")
        result = [mid for mid in market_ids if mid not in ids_to_remove]
        removed_by_tags = len(market_ids) - len(result)
        step_callback(step_subtract, "done", f"Исключено {removed_by_tags}, осталось {len(result)}")

        # K+3 — проверяем дату и статус (из кеша при use_all_markets, иначе запросы)
        need_filter = (min_days_until_end is not None and min_days_until_end > 0) or require_status
        if need_filter:
            step_callback(step_filter, "running", "")
            today = date.today()
            filtered: list[int] = []
            if use_all_markets and markets_by_id:
                for mid in result:
                    m = markets_by_id.get(mid)
                    if _check_market_from_data(m, min_days_until_end, require_status, date_fields, today):
                        filtered.append(mid)
            else:
                for i, mid in enumerate(result):
                    if i > 0:
                        time.sleep(0.1)
                    if _check_market(base_url, api_key, mid, min_days_until_end, require_status, date_fields, today):
                        filtered.append(mid)
            removed_by_filter = len(result) - len(filtered)
            result = filtered
            parts = []
            if require_status:
                parts.append(f"статус {require_status}")
            if min_days_until_end and min_days_until_end > 0:
                parts.append(f">= {min_days_until_end} дн.")
            step_callback(step_filter, "done", f"Исключено {removed_by_filter} ({', '.join(parts)})")
        else:
            step_callback(step_filter, "skip", "Фильтры не заданы")

        # K+4 — сохраняем
        step_callback(step_save, "running", "")
        Path(output_file).write_text(",".join(str(x) for x in result), encoding="utf-8")
        step_callback(step_save, "done", f"Сохранено {len(result)} id в {output_file}")

        return result, None
    except Exception as e:
        return [], str(e)
