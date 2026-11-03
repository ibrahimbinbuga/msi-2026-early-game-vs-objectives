"""Adım 4: Temiz CSV'leri SQLite'a yükle.

Kullanım:  python src/load_db.py   (önce: python src/clean.py)
Girdi:     data/processed/{teams,players,champions}.csv
Çıktı:     data/msi26.db  (tablolar: teams, players, champions)

Her çalıştırmada veritabanı sıfırdan kurulur.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "processed"
DB = ROOT / "data" / "msi26.db"

TABLES = ["teams", "players", "champions"]
INDEXES = [
    "CREATE UNIQUE INDEX ux_teams_team ON teams(team)",
    "CREATE UNIQUE INDEX ux_players_player_team ON players(player, team)",
    "CREATE INDEX ix_players_team ON players(team)",
    "CREATE UNIQUE INDEX ux_champions_champion ON champions(champion)",
]
CHECKS = {
    "teams satır": ("SELECT COUNT(*) FROM teams", 11),
    "players satır": ("SELECT COUNT(*) FROM players", 55),
    "champions satır": ("SELECT COUNT(*) FROM champions", 101),
    "SUM(wins)": ("SELECT SUM(wins) FROM teams", 71),
    "SUM(loses)": ("SELECT SUM(loses) FROM teams", 71),
    "JOIN'de eşleşmeyen oyuncu": (
        "SELECT COUNT(*) FROM players p LEFT JOIN teams t ON p.team = t.team WHERE t.team IS NULL", 0),
    "elder_dragon_rate NULL": ("SELECT COUNT(*) FROM teams WHERE elder_dragon_rate IS NULL", 3),
}


def main() -> None:
    if not SRC.exists():
        raise SystemExit("data/processed/ yok; önce `python src/clean.py` çalıştır.")
    DB.unlink(missing_ok=True)
    with sqlite3.connect(DB) as con:
        print(f"SQLite {sqlite3.sqlite_version} → {DB.relative_to(ROOT)}")
        for name in TABLES:
            df = pd.read_csv(SRC / f"{name}.csv")
            df.to_sql(name, con, index=False)
            print(f"- {name}: {len(df)} satır, {df.shape[1]} sütun yüklendi")
        for sql in INDEXES:
            con.execute(sql)
        print("Kontroller:")
        failed = False
        for label, (sql, expected) in CHECKS.items():
            got = con.execute(sql).fetchone()[0]
            ok = got == expected
            failed |= not ok
            print(f"  {'✅' if ok else '❌'} {label}: {got} (beklenen {expected})")
        types = con.execute("SELECT type, COUNT(*) FROM pragma_table_info('teams') GROUP BY type").fetchall()
        print(f"  teams sütun tipleri: {dict(types)}")
    if failed:
        raise SystemExit("Kontrol başarısız.")


if __name__ == "__main__":
    main()
