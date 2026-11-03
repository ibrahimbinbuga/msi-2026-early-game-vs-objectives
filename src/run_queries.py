"""Run every query in sql/queries.sql against data/msi26.db and print the results.

Usage:  python src/run_queries.py
Queries are separated by lines starting with "-- Q<n>.".
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "queries.sql"
DB = ROOT / "data" / "msi26.db"


def split_queries(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?m)^(?=-- Q\d+\.)", text)
    out = []
    for part in parts:
        m = re.match(r"-- (Q\d+)\.", part)
        if m:
            out.append((m.group(1), part.strip()))
    return out


def main() -> None:
    pd.set_option("display.width", 200, "display.max_columns", 20, "display.max_colwidth", 80)
    with sqlite3.connect(DB) as con:
        for qid, sql in split_queries(SQL.read_text(encoding="utf-8")):
            title = sql.splitlines()[0]
            print(f"\n{'=' * 100}\n{title}\n{'-' * 100}")
            print(pd.read_sql(sql, con).to_string(index=False))


if __name__ == "__main__":
    main()
