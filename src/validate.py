"""Adım 2: Ham veriyi doğrula ve markdown rapor üret.

Kullanım:  python src/validate.py
Çıktı:     reports/data_validation.md (ve aynı içerik stdout'a)

Bu betik veriyi DEĞİŞTİRMEZ; sadece okur ve raporlar.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "reports" / "data_validation.md"

FILES = {
    "teams": "msi_26_teams.csv",
    "players": "msi_26_players.csv",
    "champions": "msi_26_champions.csv",
}
KEYS = {"teams": ["team"], "players": ["player", "team"], "champions": ["champion"]}

lines: list[str] = []


def w(s: str = "") -> None:
    lines.append(s)


def md_table(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) if len(df) else "_(boş)_"


def pct_columns(df: pd.DataFrame) -> list[str]:
    """'%' içeren metin sütunları."""
    out = []
    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]) and df[c].dropna().astype(str).str.endswith("%").any():
            out.append(c)
    return out


def dictionary_columns() -> dict[str, list[str]]:
    """Data_Dictionary.md içindeki tablo satırlarından sütun adlarını çıkar."""
    text = (DATA / "Data_Dictionary.md").read_text(encoding="utf-8")
    result, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(msi_26_\w+)\.csv", line)
        if m:
            current = m.group(1).replace("msi_26_", "")
            result[current] = []
            continue
        m = re.match(r"^\|\s*([a-z0-9_]+)\s*\|", line)
        if current and m and m.group(1) != "column":
            result[current].append(m.group(1))
    return result


def main() -> None:
    raw = {k: pd.read_csv(DATA / f) for k, f in FILES.items()}
    dict_cols = dictionary_columns()

    w("# Veri Doğrulama Raporu (Adım 2)")
    w()
    w("Kaynak: Kaggle `stuker/league-of-legends-msi-2026` (CC BY 4.0, Eduardo Stückrath; Oracle's Elixir + Liquipedia).")
    w("Bu rapor `src/validate.py` tarafından üretildi; tüm sayılar kod çıktısıdır.")
    w()

    # ---------- 1. Şekil ----------
    w("## 1. Şekil")
    w(md_table(pd.DataFrame(
        [{"tablo": k, "dosya": FILES[k], "satır": df.shape[0], "sütun": df.shape[1]} for k, df in raw.items()]
    )))
    w()

    # ---------- 2. Sütunlar vs sözlük ----------
    w("## 2. CSV başlıkları vs Data_Dictionary.md")
    for k, df in raw.items():
        csv_cols, dcols = list(df.columns), dict_cols.get(k, [])
        missing_in_csv = [c for c in dcols if c not in csv_cols]
        missing_in_dict = [c for c in csv_cols if c not in dcols]
        same_order = csv_cols == dcols
        w(f"- **{k}**: sözlükte {len(dcols)}, CSV'de {len(csv_cols)} sütun | "
          f"sözlükte olup CSV'de olmayan: {missing_in_csv or 'yok'} | "
          f"CSV'de olup sözlükte olmayan: {missing_in_dict or 'yok'} | sıra aynı: {same_order}")
    w()

    # ---------- 3. Tipler ----------
    w("## 3. Sütun tipleri")
    for k, df in raw.items():
        pcols = pct_columns(df)
        other_obj = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) and c not in pcols]
        w(f"### {k}")
        w(f"- dtype dağılımı: {df.dtypes.astype(str).value_counts().to_dict()}")
        w(f"- '%' içeren metin sütunları ({len(pcols)}): {', '.join(pcols) if pcols else 'yok'}")
        w(f"- Diğer metin sütunları: {', '.join(other_obj) if other_obj else 'yok'}")
        # '%' sütunlarında hepsi '%' ile mi bitiyor? Parse edilebiliyor mu?
        bad = {}
        for c in pcols:
            s = df[c].dropna().astype(str)
            not_pct = s[~s.str.endswith("%")]
            parsed = pd.to_numeric(s.str.rstrip("%"), errors="coerce")
            if len(not_pct) or parsed.isna().any():
                bad[c] = {"'%' ile bitmeyen": len(not_pct), "parse edilemeyen": int(parsed.isna().sum())}
        w(f"- '%' sütunlarında parse sorunu: {bad or 'yok (hepsi temiz parse ediliyor)'}")
        w()

    # ---------- 4. Eksik değerler ----------
    w("## 4. Eksik değerler")
    for k, df in raw.items():
        na = df.isna().sum()
        na = na[na > 0]
        w(f"### {k}: toplam {int(df.isna().sum().sum())} eksik hücre")
        if len(na):
            rows = []
            for c, n in na.items():
                who = df.loc[df[c].isna(), KEYS[k][0]].tolist()
                rows.append({"sütun": c, "eksik": int(n), "satırlar": ", ".join(map(str, who))})
            w(md_table(pd.DataFrame(rows)))
        w()

    # ---------- 5. Tekrarlar ----------
    w("## 5. Tekrarlı satırlar")
    for k, df in raw.items():
        full_dup = int(df.duplicated().sum())
        key_dup = int(df.duplicated(subset=KEYS[k]).sum())
        w(f"- **{k}**: tam tekrar {full_dup} | anahtar ({', '.join(KEYS[k])}) tekrarı {key_dup}")
    p = raw["players"]
    w(f"- players: `player` adı tek başına tekrar: {int(p.duplicated(subset=['player']).sum())}")
    w()

    # ---------- 6. Tutarlılık ----------
    t, c = raw["teams"], raw["champions"]
    w("## 6. Tutarlılık kontrolleri")
    gp, wi, lo = int(t.games_played.sum()), int(t.wins.sum()), int(t.loses.sum())
    w(f"- teams: SUM(games_played)={gp}, SUM(wins)={wi}, SUM(loses)={lo} → toplam maç = {gp // 2} "
      f"(wins == loses: {wi == lo}, games_played/2 == wins: {gp / 2 == wi})")
    bad_wl = t[t.wins + t.loses != t.games_played]
    w(f"- teams: wins + loses ≠ games_played olan takım: {len(bad_wl)}")

    # players ↔ teams
    pt = set(p.team) - set(t.team)
    tp = set(t.team) - set(p.team)
    w(f"- players.team içinde teams'te olmayan: {sorted(pt) or 'yok'} | teams'te olup players'ta olmayan: {sorted(tp) or 'yok'}")
    per_team = p.groupby("team").size()
    w(f"- Takım başına oyuncu sayısı: {per_team.value_counts().to_dict()} (sayı: takım adedi)")
    pos = p.groupby("team").position.apply(lambda s: sorted(s)).astype(str).value_counts()
    w(f"- Pozisyon setleri: {pos.to_dict()}")
    w(f"- Pozisyon dağılımı: {p.position.value_counts().to_dict()}")
    w()

    # games_played eşitliği
    w("### Oyuncu games_played = takım games_played mı?")
    m = p.merge(t[["team", "games_played", "wins"]], on="team", suffixes=("", "_team"))
    mism = m[m.games_played != m.games_played_team]
    w(f"- Eşleşmeyen oyuncu: **{len(mism)} / {len(m)}**")
    if len(mism):
        w(md_table(mism[["player", "team", "position", "games_played", "games_played_team"]]))
    # oyuncu winrate vs takım winrate
    m["team_wr"] = (m.wins / m.games_played_team * 100).round(0)
    m["player_wr"] = pd.to_numeric(m.winrate.astype(str).str.rstrip("%"), errors="coerce")
    wr_bad = m[(m.player_wr - m.team_wr).abs() > 1]
    w(f"- Oyuncu `winrate` ile takım wins/games_played (yuvarlanmış %) farkı >1 puan olan oyuncu: {len(wr_bad)}")
    if len(wr_bad):
        w(md_table(wr_bad[["player", "team", "player_wr", "team_wr"]]))
    w()

    # Kill toplamı
    w("### Oyuncu kills toplamı = takım kills mı?")
    ks = p.groupby("team").kills.sum().rename("player_kills").reset_index().merge(t[["team", "kills"]], on="team")
    ks["fark"] = ks.player_kills - ks.kills
    w(f"- Farkı 0 olmayan takım: {int((ks.fark != 0).sum())} / {len(ks)}")
    if (ks.fark != 0).any():
        w(md_table(ks[ks.fark != 0]))
    w()

    # Şampiyonlar
    w("### Şampiyonlar")
    zero = c[c.games_played == 0]
    w(f"- games_played = 0: {len(zero)} şampiyon → {', '.join(zero.champion)}")
    if len(zero):
        other = [col for col in c.columns if col not in ("champion", "games_played", "pick_rate", "ban_rate", "pick_ban_rate")]
        w(f"  - Bu satırlarda boş olmayan diğer metrik sayısı (pick/ban hariç): {int(zero[other].notna().sum().sum())}")
        nn = zero[other].notna().sum()
        w(f"  - Boş olmayan sütunlar: {nn[nn > 0].index.tolist()} → değerler: {zero[nn[nn > 0].index.tolist()].to_dict('list')}")
        w(f"  - pick_rate/ban_rate/pick_ban_rate: hepsi NaN mı? {bool(zero[['pick_rate','ban_rate','pick_ban_rate']].isna().all().all())} (yani bu şampiyonlar hiç banlanmamış da olabilir; ban bilgisi kayıp)")
    w(f"- games_played ≥ 5: **{int((c.games_played >= 5).sum())}** şampiyon")
    total_picks = int(c.games_played.sum())
    w(f"- SUM(champions.games_played) = {total_picks} (beklenen 10 × {gp // 2} maç = {10 * (gp // 2)})")
    # pick_rate tutarlılığı: games_played / toplam maç
    c_pl = c[c.games_played > 0].copy()
    c_pl["pick_rate_calc"] = (c_pl.games_played / (gp // 2) * 100).round(1)
    pr_bad = c_pl[(c_pl.pick_rate - c_pl.pick_rate_calc).abs() > 0.15]
    w(f"- pick_rate ≈ games_played / {gp // 2} × 100 tutmayan şampiyon: {len(pr_bad)}")
    if len(pr_bad):
        w(md_table(pr_bad[["champion", "games_played", "pick_rate", "pick_rate_calc"]]))
    pb_bad = c[(c.pick_rate + c.ban_rate - c.pick_ban_rate).abs() > 0.15]
    w(f"- pick_rate + ban_rate ≈ pick_ban_rate tutmayan şampiyon: {len(pb_bad)}")
    if len(pb_bad):
        w(md_table(pb_bad[["champion", "pick_rate", "ban_rate", "pick_ban_rate"]]))
    w()

    # ---------- 7. Float artıkları ----------
    w("## 7. Float artıkları (ondalık hanesi > 2)")
    for k, df in raw.items():
        num = df.select_dtypes("number")
        resid = (num - num.round(2)).abs() > 1e-9
        cols = resid.sum()
        cols = cols[cols > 0]
        w(f"- **{k}**: {int(resid.sum().sum())} hücre, {len(cols)} sütun" + (f" ({', '.join(cols.index)})" if len(cols) else ""))
    w()

    # ---------- 8. Değer aralıkları ----------
    w("## 8. Değer aralıkları (aykırı/imkânsız değer taraması)")
    for k, df in raw.items():
        num = df.copy()
        for col in pct_columns(df):
            num[col] = pd.to_numeric(df[col].astype(str).str.rstrip("%"), errors="coerce")
        num = num.select_dtypes("number")
        desc = num.describe().T[["count", "min", "50%", "max"]].round(2).reset_index().rename(columns={"index": "sütun", "50%": "medyan"})
        w(f"### {k}")
        w(md_table(desc))
        rate_cols = [col for col in num.columns if col.endswith(("_rate", "_share", "pickrate", "participation")) or col in ("winrate", "lane_control", "jungle_control")]
        oor = {col: int(((num[col] < 0) | (num[col] > 100)).sum()) for col in rate_cols}
        oor = {k2: v for k2, v in oor.items() if v}
        w(f"- 0–100 aralığı dışında oran değeri: {oor or 'yok'}")
        w()

    # ---------- 9. TASK.md iddialarının durumu ----------
    w("## 9. TASK.md iddialarının kontrolü")
    elder_na = t.loc[t.elder_dragon_rate.isna(), "team"].tolist()
    claims = [
        ("teams 11×30, players 55×29, champions 104×21",
         raw["teams"].shape == (11, 30) and raw["players"].shape == (55, 29) and raw["champions"].shape == (104, 21)),
        ("Toplam 71 maç, sum(games_played)=142, sum(wins)=71", gp == 142 and wi == 71),
        ("Sütun adı `loses`", "loses" in t.columns),
        ("elder_dragon_rate 3 takımda NaN (DCG, TSW, TES)",
         sorted(elder_na) == sorted(["Deep Cross Gaming", "Team Secret Whales", "Top Esports"])),
        ("Kennen, Rek'Sai, Malphite games_played=0",
         sorted(zero.champion) == sorted(["Kennen", "Rek'Sai", "Malphite"])),
        ("≥5 maçlı şampiyon sayısı 63", int((c.games_played >= 5).sum()) == 63),
        ("Her oyuncunun games_played'i takımınınkine eşit", len(mism) == 0),
        ("6 maçta kalan takımlar: Deep Cross Gaming, FURIA",
         sorted(t.loc[t.games_played == 6, "team"]) == ["Deep Cross Gaming", "FURIA"]),
    ]
    w(md_table(pd.DataFrame([{"iddia": a, "sonuç": "✅ doğru" if ok else "❌ yanlış"} for a, ok in claims])))
    w()
    w(f"- 6 maçlı takımlar: {t.loc[t.games_played == 6, 'team'].tolist()}")
    w(f"- games_played dağılımı (takım): {t.set_index('team').games_played.sort_values(ascending=False).to_dict()}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
