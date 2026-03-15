import json
import os
import sys
from pathlib import Path

from filter_logic import (
    collect_ids_to_remove,
    filter_by_min_days_until_end,
    filter_by_status,
    subtract_from_list,
)

BASE_URL = "https://api.predict.fun"
SETTINGS_FILE = Path(__file__).parent / ".settings.json"


def _load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {}


def load_market_ids(path: str) -> list[int]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Файл со списком маркетов не найден: {path}")
    text = p.read_text(encoding="utf-8").strip().replace("\n", ",")
    parts = [s.strip() for s in text.split(",") if s.strip()]
    return [int(x) for x in parts]


def cli_main() -> None:
    settings = _load_settings()
    api_key = os.environ.get("PREDICT_FUN_API_KEY") or settings.get("api_key") or ""
    if not api_key:
        print("API-ключ не найден.")
        print("Запустите GUI (python main.py) и введите ключ, либо задайте PREDICT_FUN_API_KEY.")
        return

    market_file = settings.get("market_ids_file") or "last_market_ids.txt"
    market_ids = load_market_ids(market_file)
    if not market_ids:
        print(f"Список маркетов пуст ({market_file})")
        return

    base_url = BASE_URL
    exclude_tag_ids = settings.get("exclude_tag_ids") or []

    if not exclude_tag_ids:
        print("exclude_tag_ids не задан. Результат совпадает с входным списком.")

    ids_to_remove = collect_ids_to_remove(base_url, api_key, exclude_tag_ids)
    result = subtract_from_list(market_ids, ids_to_remove)

    require_status = settings.get("require_status")
    min_days = settings.get("min_days_until_end")

    if min_days is not None and min_days > 0:
        date_fields = ["boostEndsAt", "endDate", "resolutionDate"]
        before = len(result)
        result = filter_by_min_days_until_end(
            base_url, api_key, result, min_days, date_fields, require_status
        )
        print("Исключено по тегам:", len(ids_to_remove))
        print("Исключено по дате/статусу:", before - len(result))
    elif require_status:
        before = len(result)
        result = filter_by_status(base_url, api_key, result, require_status)
        print("Исключено по тегам:", len(ids_to_remove))
        print(f"Исключено по статусу (не {require_status}):", before - len(result))
    else:
        print("Исключено id по тегам:", len(ids_to_remove))
    print("Осталось id:", len(result))

    output_file = settings.get("output_file") or "result.txt"
    Path(output_file).write_text(",".join(str(x) for x in result), encoding="utf-8")
    print("Сохранено в", output_file)


if __name__ == "__main__":
    if "--cli" in sys.argv:
        cli_main()
    else:
        try:
            from gui_main import main as gui_main
            gui_main()
        except Exception as e:
            print("Не удалось запустить окно:", e)
            print("Установите PySide6: pip install PySide6")
            print("Консольный режим: python main.py --cli")
