-- MSI 2026 — SQL questions (SQLite, data/msi26.db)
-- Run all:  python src/run_queries.py
-- Rates are percentage points (0–100). Count columns are INTEGER: multiply by 1.0 before dividing.
-- Each query: question + summary of the output (filled in from the actual run).

-- Q1. Consistency: is SUM(wins) = SUM(loses) = total number of matches?
-- Output: 71 wins = 71 losses = 71 matches → consistent = 1.
SELECT SUM(wins)                AS total_wins,
       SUM(loses)               AS total_losses,
       SUM(games_played) / 2    AS total_matches,
       SUM(wins) = SUM(loses) AND SUM(wins) = SUM(games_played) / 2 AS consistent
FROM teams;

-- Q2. Rank teams by win rate (RANK() OVER).
-- Output: T1 #1 (71.4%), HLE #2 (65.0%), BLG and LYON tied #3 (64.7%); RANK leaves gaps after ties (7, 7, 9, 10, 10). DCG and FURIA last at 0%.
SELECT RANK() OVER (ORDER BY winrate DESC) AS rnk,
       team, games_played, wins, loses,
       ROUND(winrate, 1) AS winrate
FROM teams
ORDER BY rnk, team;

-- Q3. Split teams into 3 tiers by win rate (NTILE(3)); average early/objective metrics per tier.
-- Ties are broken by team name so the split is deterministic.
-- Output: Tier 1 (T1, HLE, BLG, LYON): avg winrate 66.5%, gold@15 +713, baron 56.8%. Tier 3 (TSW, DCG, FURIA): 10.0%, gold@15 −1782, first tower 6.7%. Among the rate columns, dragon control varies least across tiers (53.0 → 46.8 → 44.7).
WITH tiers AS (
    SELECT *, NTILE(3) OVER (ORDER BY winrate DESC, team) AS tier
    FROM teams
)
SELECT tier,
       COUNT(*)                          AS n_teams,
       GROUP_CONCAT(team, ', ')          AS teams,
       ROUND(AVG(winrate), 1)            AS avg_winrate,
       ROUND(AVG(gold_diff_15), 0)       AS avg_gold_diff_15,
       ROUND(AVG(first_tower_rate), 1)   AS avg_first_tower,
       ROUND(AVG(dragon_control_rate), 1) AS avg_dragon_control,
       ROUND(AVG(baron_control_rate), 1) AS avg_baron_control
FROM tiers
GROUP BY tier
ORDER BY tier;

-- Q4. Teams above 50% win rate vs the rest (CASE + GROUP BY): early and objective metric averages.
-- Team Liquid is exactly 50% and falls in the "<= 50%" group.
-- Output: > 50% (4 teams) vs <= 50% (7 teams): gold@15 +713 vs −934, first to 3 towers 64.5 vs 28.4, baron 56.8 vs 39.0. First dragon is the only metric where the lower group is higher (50.0 vs 51.7).
SELECT CASE WHEN winrate > 50 THEN '> 50%' ELSE '<= 50%' END AS winrate_group,
       COUNT(*)                                   AS n_teams,
       ROUND(AVG(gold_diff_15), 0)                AS gold_diff_15,
       ROUND(AVG(first_tower_rate), 1)            AS first_tower,
       ROUND(AVG(first_blood_rate), 1)            AS first_blood,
       ROUND(AVG(first_to_three_towers_rate), 1)  AS first_to_3_towers,
       ROUND(AVG(dragon_control_rate), 1)         AS dragon_control,
       ROUND(AVG(baron_control_rate), 1)          AS baron_control,
       ROUND(AVG(grub_control_rate), 1)           AS grub_control,
       ROUND(AVG(first_dragon_rate), 1)           AS first_dragon
FROM teams
GROUP BY winrate_group
ORDER BY winrate_group DESC;

-- Q5. By role: average gold_diff_10 of players on teams with win rate > 50% vs the rest (JOIN + GROUP BY).
-- Output: Players on > 50% teams have a higher gold_diff_10 in every role. Gap largest for ADC (+173.8 vs −222.9, gap 396.6), smallest for Middle (73.3).
SELECT p.position,
       ROUND(AVG(CASE WHEN t.winrate > 50 THEN p.gold_diff_10 END), 1)  AS gd10_winning_teams,
       ROUND(AVG(CASE WHEN t.winrate <= 50 THEN p.gold_diff_10 END), 1) AS gd10_other_teams,
       ROUND(AVG(CASE WHEN t.winrate > 50 THEN p.gold_diff_10 END)
           - AVG(CASE WHEN t.winrate <= 50 THEN p.gold_diff_10 END), 1) AS gap
FROM players p
JOIN teams t ON t.team = p.team
GROUP BY p.position
ORDER BY gap DESC;

-- Q6. Player with the highest damage_share on each team (ROW_NUMBER() OVER PARTITION BY team).
-- Output: ADC leads damage share on 8 of 11 teams; Middle on G2 (Caps), BLG (Knight), DCG (HongSuo). Highest: Peyz (T1) 32.3%.
WITH ranked AS (
    SELECT team, player, position, damage_share,
           ROW_NUMBER() OVER (PARTITION BY team ORDER BY damage_share DESC, player) AS rn
    FROM players
)
SELECT team, player, position, damage_share
FROM ranked
WHERE rn = 1
ORDER BY damage_share DESC;

-- Q7. Each player's KDA minus their team's average KDA (AVG() OVER PARTITION BY team); 10 largest deviations.
-- Output: Largest gaps: Knight (BLG) +2.46 above team avg, Zeka (HLE) +2.10, Bin (BLG) −1.84. The 7 positive gaps are all mid laners or ADCs; the 3 negative ones are all top laners.
WITH dev AS (
    SELECT player, team, position, kda,
           ROUND(AVG(kda) OVER (PARTITION BY team), 2)       AS team_avg_kda,
           ROUND(kda - AVG(kda) OVER (PARTITION BY team), 2) AS kda_vs_team
    FROM players
)
SELECT *
FROM dev
ORDER BY ABS(kda_vs_team) DESC, player
LIMIT 10;

-- Q8. Validation: does player kills / team kills match the teams_kill_share column?
-- Output: 55/55 players match within 0.1 pt (max abs diff 0.05 pt) → the column is player kills / team kills × 100.
WITH chk AS (
    SELECT p.player, p.team, p.teams_kill_share,
           ROUND(100.0 * p.kills / t.kills, 1)                     AS computed_share,
           ABS(p.teams_kill_share - 100.0 * p.kills / t.kills)     AS abs_diff
    FROM players p
    JOIN teams t ON t.team = p.team
)
SELECT COUNT(*)                                   AS n_players,
       SUM(abs_diff <= 0.1)                       AS within_0_1_pt,
       SUM(abs_diff > 0.1)                        AS off_by_more,
       ROUND(MAX(abs_diff), 3)                    AS max_abs_diff_pt
FROM chk;

-- Q9. Champions with >= 5 games: top 10 by pick_ban_rate, with their win rate.
-- Output: Vi (71.8%), Jayce (67.6%), Orianna (64.8%) most contested. Win rates of the top 10 range 33% (Nautilus) to 80% (Akali, only 5 games).
SELECT champion, games_played, pick_rate, ban_rate, pick_ban_rate, winrate
FROM champions
WHERE games_played >= 5
ORDER BY pick_ban_rate DESC, champion
LIMIT 10;

-- Q10. "Feared but not played": ban_rate > pick_rate, at least 5 games.
-- Output: 20 champions with ban_rate > pick_rate. Biggest gaps: Akali (+38.1 pt, 5 games), Jayce (+36.6), Vi (+35.2), Orianna (+31.0).
SELECT champion, games_played, pick_rate, ban_rate,
       ROUND(ban_rate - pick_rate, 1) AS ban_minus_pick, winrate
FROM champions
WHERE games_played >= 5 AND ban_rate > pick_rate
ORDER BY ban_minus_pick DESC, champion;

-- Q11. Per role: top 3 players by gold_diff_10 and by cs_diff_10 (DENSE_RANK() OVER PARTITION BY position).
-- A player is listed if they are top 3 on either metric.
-- Output: ADC: Peyz (T1) #1 on both. Top: Canna (KC) #1 gold@10, Bin (BLG) #1 cs@10. Gold and CS leads do not always line up (e.g. ON, BLG support: gold #2, CS #10; Caps: CS #1, gold #7).
WITH r AS (
    SELECT position, player, team, gold_diff_10, cs_diff_10,
           DENSE_RANK() OVER (PARTITION BY position ORDER BY gold_diff_10 DESC) AS gd10_rank,
           DENSE_RANK() OVER (PARTITION BY position ORDER BY cs_diff_10 DESC)   AS cs10_rank
    FROM players
)
SELECT position, player, team, gold_diff_10, gd10_rank, cs_diff_10, cs10_rank
FROM r
WHERE gd10_rank <= 3 OR cs10_rank <= 3
ORDER BY position, gd10_rank, cs10_rank;
