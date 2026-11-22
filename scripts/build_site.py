"""Генерирует статическую страницу public/index.html с описанием алгоритма."""
import html
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pomodoro import Config, State, schedule  # noqa: E402

LABELS = {
    State.WORK: "Работа",
    State.SHORT_BREAK: "Короткий перерыв",
    State.LONG_BREAK: "Длинный перерыв",
}


def build():
    config = Config()
    rows = []
    elapsed = 0
    for state, minutes in schedule(8, config):
        rows.append(
            f"<tr><td>{html.escape(LABELS[state])}</td><td>{minutes}</td><td>{elapsed}</td></tr>"
        )
        elapsed += minutes

    sha = os.environ.get("GITHUB_SHA", "local")[:7]
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    table_rows = "\n".join(rows)

    page = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Помодоро: логика интервалов</title>
<style>
body {{ font-family: sans-serif; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #999; padding: .3rem .6rem; text-align: left; }}
footer {{ margin-top: 2rem; color: #666; font-size: .9rem; }}
</style>
</head>
<body>
<h1>Таймер «Помодоро»: алгоритм</h1>
<p>Работа ({config.work} мин) → короткий перерыв ({config.short_break} мин).
После каждой {config.sessions_before_long}-й рабочей сессии вместо короткого
наступает длинный перерыв ({config.long_break} мин). После любого перерыва
начинается новая рабочая сессия.</p>
<h2>План на 8 сессий</h2>
<table>
<tr><th>Интервал</th><th>Минут</th><th>Старт (мин от начала)</th></tr>
{table_rows}
</table>
<footer>Сборка {sha}, {built}</footer>
</body>
</html>
"""
    out = ROOT / "public"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"Страница собрана: {out / 'index.html'}")


if __name__ == "__main__":
    build()
