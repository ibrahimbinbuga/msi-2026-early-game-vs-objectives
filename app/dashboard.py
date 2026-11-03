"""MSI 2026 dashboard — reads from SQLite (data/msi26.db), not from CSV.

Run:  streamlit run app/dashboard.py   (after: python src/clean.py && python src/load_db.py)
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB = Path(__file__).resolve().parents[1] / "data" / "msi26.db"

BLUE, ORANGE, INK2 = "#2a78d6", "#eb6834", "#52514e"
EARLY = ["gold_diff_15", "first_tower_rate", "first_blood_rate", "first_to_three_towers_rate"]
OBJ = ["dragon_control_rate", "baron_control_rate", "grub_control_rate", "first_dragon_rate"]
GROUP = {**{m: "Early game" for m in EARLY}, **{m: "Objective control" for m in OBJ}}
LABEL = {
    "gold_diff_15": "Gold diff @15 (gold)", "first_tower_rate": "First tower rate (%)",
    "first_blood_rate": "First blood rate (%)", "first_to_three_towers_rate": "First to 3 towers rate (%)",
    "dragon_control_rate": "Dragon control (%)", "baron_control_rate": "Baron control (%)",
    "grub_control_rate": "Void grub control (%)", "first_dragon_rate": "First dragon rate (%)",
}
PLAYER_METRICS = {"kda": "KDA", "gold_diff_10": "Gold diff @10 (gold)", "damage_share": "Damage share (%)"}
ABBR = {"Bilibili Gaming": "BLG", "Deep Cross Gaming": "DCG", "FURIA": "FUR", "G2 Esports": "G2",
        "Hanwha Life Esports": "HLE", "Karmine Corp": "KC", "LYON": "LYON", "T1": "T1",
        "Team Liquid": "TL", "Team Secret Whales": "TSW", "Top Esports": "TES"}


@st.cache_data
def load(table: str) -> pd.DataFrame:
    with sqlite3.connect(DB) as con:
        return pd.read_sql(f"SELECT * FROM {table}", con)


def spearman(df: pd.DataFrame, x: str, y: str = "winrate") -> float:
    return df[x].corr(df[y], method="spearman")


st.set_page_config(page_title="MSI 2026 — Early game vs objectives", layout="wide")
st.title("MSI 2026 — Early game vs objective control")
st.caption("Descriptive only: 11 teams, Spearman correlations, no causal claims. "
           "Win rate = wins / games played × 100. Rates are percentage points.")

if not DB.exists():
    st.error("data/msi26.db not found. Run `python src/clean.py && python src/load_db.py` first.")
    st.stop()

teams, players, champs = load("teams"), load("players"), load("champions")
teams["abbr"] = teams.team.map(ABBR)

tab_t, tab_p, tab_c = st.tabs(["Teams", "Players", "Champions"])

# ---------------------------------------------------------------- Teams
with tab_t:
    metric = st.selectbox("Metric (x-axis)", EARLY + OBJ, format_func=lambda m: f"{LABEL[m]} — {GROUP[m]}")
    color = BLUE if GROUP[metric] == "Early game" else ORANGE
    fig = px.scatter(teams, x=metric, y="winrate", text="abbr", hover_name="team",
                     hover_data={"games_played": True, "abbr": False},
                     labels={metric: LABEL[metric], "winrate": "Win rate (%)"})
    fig.update_traces(marker=dict(size=13, color=color, line=dict(width=2, color="white")),
                      textposition="top right", textfont=dict(size=12))
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=40, b=10),
                      title=f"{LABEL[metric].split(' (')[0]} vs win rate — Spearman ρ = {spearman(teams, metric):.2f}")
    st.plotly_chart(fig, width="stretch")
    st.caption("Each dot is a team. Win rate also tracks games played (eliminated teams stop playing), "
               "and objectives are often taken by the team already ahead — read as co-movement, not cause.")

    rows = []
    for m in EARLY + OBJ:
        loo = [spearman(teams[teams.team != t], m) for t in teams.team]
        rows.append({"Group": GROUP[m], "Metric": LABEL[m], "Spearman ρ": spearman(teams, m),
                     "One-team-out min": min(loo), "One-team-out max": max(loo)})
    corr = pd.DataFrame(rows).sort_values("Spearman ρ", ascending=False)
    st.subheader("Correlation with win rate (n = 11)")
    st.dataframe(corr.style.format({c: "{:.2f}" for c in corr.columns[2:]}), hide_index=True,
                 width="stretch")

# ---------------------------------------------------------------- Players
with tab_p:
    c1, c2, c3 = st.columns(3)
    roles = c1.multiselect("Role", sorted(players.position.unique()), default=sorted(players.position.unique()))
    team_sel = c2.multiselect("Team", sorted(players.team.unique()), default=sorted(players.team.unique()))
    pm = c3.selectbox("Bar chart metric", list(PLAYER_METRICS), format_func=PLAYER_METRICS.get)
    p = players[players.position.isin(roles) & players.team.isin(team_sel)]
    if p.empty:
        st.info("No players match the filters.")
    else:
        p = p.sort_values(pm, ascending=False)
        fig = px.bar(p, x="player", y=pm, hover_data=["team", "position", "games_played"],
                     labels={pm: PLAYER_METRICS[pm], "player": "Player"},
                     title=f"{PLAYER_METRICS[pm]} by player ({len(p)} players)")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10), xaxis_tickangle=-45)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(p[["player", "team", "position", "games_played", "kda", "gold_diff_10", "damage_share"]]
                     .rename(columns={"games_played": "games", "gold_diff_10": "gold diff @10",
                                      "damage_share": "damage share (%)"}),
                     hide_index=True, width="stretch")

# ---------------------------------------------------------------- Champions
with tab_c:
    max_g = int(champs.games_played.max())
    min_g = st.slider("Minimum games played", 1, max_g, 5)
    c = champs[champs.games_played >= min_g]
    if len(c) < 3:
        st.info("Too few champions at this threshold.")
    else:
        fig = px.scatter(c, x="pick_ban_rate", y="winrate", size="games_played", hover_name="champion",
                         hover_data={"pick_rate": True, "ban_rate": True, "games_played": True},
                         labels={"pick_ban_rate": "Pick + ban rate (%)", "winrate": "Win rate (%)",
                                 "games_played": "Games"})
        fig.update_traces(marker=dict(color=BLUE, opacity=0.75, line=dict(width=1, color="white")))
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=40, b=10),
                          title=f"Pick + ban rate vs win rate — {len(c)} champions with ≥ {min_g} games, "
                                f"Spearman ρ = {spearman(c, 'pick_ban_rate'):.2f}")
        st.plotly_chart(fig, width="stretch")
        st.caption("Win rates on few games are noisy; the default threshold is 5 games. "
                   "Dot size = games played.")

st.divider()
st.caption("Data: *League of Legends MSI 2026 Dataset* by Eduardo Stückrath (Kaggle), from Oracle's Elixir, "
           "validated with Liquipedia. License: CC BY 4.0.")
