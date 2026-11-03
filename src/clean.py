"""Adım 3: Ham CSV'leri temizle.

Kullanım:  python src/clean.py
Girdi:     data/msi_26_{teams,players,champions}.csv
Çıktı:     data/processed/{teams,players,champions}.csv
Log:       reports/cleaning_log.md (aynı içerik stdout'a)

Kararlar (gerekçeleri DEVLOG.md "Karar ve varsayımlar"da):
- "%" metinleri float'a çevrilir, ölçek YÜZDE PUANI (0–100) olarak kalır.
  champions tablosu zaten bu ölçekte; üç tablo tutarlı olsun diye.
- teams.winrate = wins / games_played × 100 türetilir (yüzde puanı).
- games_played = 0 olan şampiyonlar çıkarılır.
- Tüm float sütunlar 2 ondalığa yuvarlanır (15.299999 → 15.3).
- elder_dragon_rate'teki NaN'lar KORUNUR (0 ile doldurulmaz).
- Başka satır silinmez, başka değer değiştirilmez.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data"
OUT = ROOT / "data" / "processed"
LOG = ROOT / "reports" / "cleaning_log.md"

FILES = {
    "teams": "msi_26_teams.csv",
    "players": "msi_26_players.csv",
    "champions": "msi_26_champions.csv",
}
ROUND = 2

log: list[str] = []


def w(s: str = "") -> None:
    log.append(s)


def convert_pct(df: pd.DataFrame, name: str) -> pd.DataFrame:
    df = df.copy()
    cols = [
        c for c in df.columns
        if pd.api.types.is_string_dtype(df[c]) and df[c].dropna().astype(str).str.endswith("%").any()
    ]
    for c in cols:
        before_na = int(df[c].isna().sum())
        # float'a zorla: "65%" → int64 olur, SQLite'ta INTEGER → tam sayı bölmesi riski
        df[c] = pd.to_numeric(df[c].astype(str).str.strip().str.rstrip("%"), errors="coerce").astype(float)
        after_na = int(df[c].isna().sum())
        if after_na != before_na:
            raise ValueError(f"{name}.{c}: parse sırasında {after_na - before_na} yeni NaN oluştu")
    w(f"- **{name}**: {len(cols)} '%' sütunu float'a çevrildi (0–100 ölçeği): {', '.join(cols) if cols else 'yok'}")
    return df


def round_floats(df: pd.DataFrame, name: str) -> pd.DataFrame:
    df = df.copy()
    fcols = df.select_dtypes("float").columns
    changed = int(((df[fcols] - df[fcols].round(ROUND)).abs() > 1e-9).sum().sum())
    df[fcols] = df[fcols].round(ROUND)
    w(f"- **{name}**: float sütunlar {ROUND} ondalığa yuvarlandı, değişen hücre: {changed}")
    return df


def main() -> None:
    raw = {k: pd.read_csv(RAW / f) for k, f in FILES.items()}
    w("# Temizleme Logu (Adım 3)")
    w()
    w("`src/clean.py` tarafından üretildi.")
    w()
    w("## Girdi")
    for k, df in raw.items():
        w(f"- {k}: {df.shape[0]} satır × {df.shape[1]} sütun")
    w()

    w("## 1. '%' metinleri → float")
    clean = {k: convert_pct(df, k) for k, df in raw.items()}
    w()

    w("## 2. 0 maçlı şampiyonlar")
    c = clean["champions"]
    zero = c[c.games_played == 0]
    clean["champions"] = c[c.games_played > 0].reset_index(drop=True)
    w(f"- Çıkarılan: {len(zero)} satır → {', '.join(zero.champion)}")
    w(f"- Kalan: {len(clean['champions'])} şampiyon")
    w()

    w("## 3. Float yuvarlama")
    clean = {k: round_floats(df, k) for k, df in clean.items()}
    w()

    w("## 4. Türetilen sütun: teams.winrate")
    t = clean["teams"]
    t.insert(t.columns.get_loc("loses") + 1, "winrate", (t.wins / t.games_played * 100).round(ROUND))
    clean["teams"] = t
    w("- `winrate = wins / games_played × 100` (yüzde puanı), `loses` sütunundan sonra eklendi.")
    w(t[["team", "games_played", "wins", "loses", "winrate"]].sort_values("winrate", ascending=False).to_markdown(index=False))
    w()

    w("## 5. Korunan eksik değerler")
    for k, df in clean.items():
        na = df.isna().sum()
        na = na[na > 0]
        if len(na):
            for col, n in na.items():
                key = df.columns[0]
                w(f"- {k}.{col}: {int(n)} NaN korundu ({', '.join(df.loc[df[col].isna(), key])})")
        else:
            w(f"- {k}: eksik değer yok")
    w()

    w("## 6. Son kontroller")
    t, p, ch = clean["teams"], clean["players"], clean["champions"]
    checks = {
        "teams'te metin sütunu sadece `team`": [c for c in t.columns if pd.api.types.is_string_dtype(t[c])] == ["team"],
        "players'ta metin sütunları sadece player/team/position":
            [c for c in p.columns if pd.api.types.is_string_dtype(p[c])] == ["player", "team", "position"],
        "champions'ta metin sütunu sadece `champion`":
            [c for c in ch.columns if pd.api.types.is_string_dtype(ch[c])] == ["champion"],
        "SUM(teams.wins) = 71": int(t.wins.sum()) == 71,
        "players.winrate ≈ teams.winrate (±1 puan)":
            bool((p.merge(t[["team", "winrate"]], on="team", suffixes=("", "_t"))
                  .eval("abs(winrate - winrate_t)") <= 1).all()),
        "champions'ta games_played ≥ 1 ve 101 satır": bool((ch.games_played >= 1).all()) and len(ch) == 101,
        "champions'ta games_played ≥ 5: 63 satır": int((ch.games_played >= 5).sum()) == 63,
        "champions'ta NaN yok": int(ch.isna().sum().sum()) == 0,
    }
    for name, ok in checks.items():
        w(f"- {'✅' if ok else '❌'} {name}")
    if not all(checks.values()):
        raise SystemExit("Son kontrollerden biri başarısız; log'a bak.")
    w()

    OUT.mkdir(parents=True, exist_ok=True)
    w("## Çıktı")
    for k, df in clean.items():
        path = OUT / f"{k}.csv"
        df.to_csv(path, index=False)
        w(f"- `{path.relative_to(ROOT)}`: {df.shape[0]} satır × {df.shape[1]} sütun")

    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
