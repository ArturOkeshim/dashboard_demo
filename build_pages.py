"""
Сборка статической версии дашборда для GitHub Pages.

Логический поток:
1. Читаем Excel через load_report (как в Streamlit).
2. Сохраняем строки в docs/data.js — браузер потом сам фильтрует и рисует график.
3. На GitHub: Settings → Pages → Source = Deploy from a branch → folder /docs.

Запуск: python build_pages.py
Потом открыть docs/index.html в браузере или выложить репозиторий.
"""
from __future__ import annotations

import json
from pathlib import Path

from load_report import DEFAULT_REPORT, KNOWN_LINES, load_turnover

DOCS_DIR = Path(__file__).resolve().parent / "docs"
DATA_JS = DOCS_DIR / "data.js"


def rows_for_browser(report_path: Path) -> dict:
    """Готовим компактный JSON: только то, что нужно фильтрам и графику."""
    frame = load_turnover(report_path)

    # Берем только нужные колонки — проще и легче файл.
    records = []
    for row in frame.itertuples(index=False):
        records.append(
            {
                "date": row.date.strftime("%Y-%m-%d"),
                "line": row.line,
                "obj": row.obj,
                "item": row.item,
                "amount": float(row.amount),
            }
        )

    # Счета: известные заранее + всё, что встретилось в отчёте.
    lines_from_data = {rec["line"] for rec in records if rec["line"]}
    all_lines = sorted(set(KNOWN_LINES) | lines_from_data)

    return {
        "rows": records,
        "known_lines": list(KNOWN_LINES),
        "all_lines": all_lines,
    }


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    payload = rows_for_browser(DEFAULT_REPORT)

    # # ЗАМЕТКА ДЛЯ ОБУЧЕНИЯ:
    # Браузер не умеет читать .xlsx напрямую. Поэтому Python один раз
    # превращает таблицу в JS-файл, а страница просто подключает его как скрипт.
    js_text = (
        "// Автогенерация: python build_pages.py — руками не править.\n"
        "window.DASHBOARD_DATA = "
        + json.dumps(payload, ensure_ascii=False)
        + ";\n"
    )
    DATA_JS.write_text(js_text, encoding="utf-8")

    print(f"OK: {len(payload['rows'])} rows -> {DATA_JS}")
    print("Open docs/index.html or enable GitHub Pages (folder: /docs).")


if __name__ == "__main__":
    main()
