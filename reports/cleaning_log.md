# Temizleme Logu (Adım 3)

`src/clean.py` tarafından üretildi.

## Girdi
- teams: 11 satır × 30 sütun
- players: 55 satır × 29 sütun
- champions: 104 satır × 21 sütun

## 1. '%' metinleri → float
- **teams**: 13 '%' sütunu float'a çevrildi (0–100 ölçeği): gold_spent_difference, first_blood_rate, first_tower_rate, first_to_three_towers_rate, rift_herald_rate, grub_control_rate, first_dragon_rate, dragon_control_rate, elder_dragon_rate, first_baron_rate, baron_control_rate, lane_control, jungle_control
- **players**: 10 '%' sütunu float'a çevrildi (0–100 ölçeği): winrate, counter_pickrate, kill_participation, teams_kill_share, team_deaths_share, first_blood_rate, cs_post_15_share, damage_share, team_damage_post_15_share, gold_share
- **champions**: 0 '%' sütunu float'a çevrildi (0–100 ölçeği): yok

## 2. 0 maçlı şampiyonlar
- Çıkarılan: 3 satır → Kennen, Rek'Sai, Malphite
- Kalan: 101 şampiyon

## 3. Float yuvarlama
- **teams**: float sütunlar 2 ondalığa yuvarlandı, değişen hücre: 0
- **players**: float sütunlar 2 ondalığa yuvarlandı, değişen hücre: 0
- **champions**: float sütunlar 2 ondalığa yuvarlandı, değişen hücre: 132

## 4. Türetilen sütun: teams.winrate
- `winrate = wins / games_played × 100` (yüzde puanı), `loses` sütunundan sonra eklendi.
| team                |   games_played |   wins |   loses |   winrate |
|:--------------------|---------------:|-------:|--------:|----------:|
| T1                  |             21 |     15 |       6 |     71.43 |
| Hanwha Life Esports |             20 |     13 |       7 |     65    |
| Bilibili Gaming     |             17 |     11 |       6 |     64.71 |
| LYON                |             17 |     11 |       6 |     64.71 |
| Team Liquid         |             12 |      6 |       6 |     50    |
| G2 Esports          |             15 |      6 |       9 |     40    |
| Karmine Corp        |              9 |      3 |       6 |     33.33 |
| Top Esports         |              9 |      3 |       6 |     33.33 |
| Team Secret Whales  |             10 |      3 |       7 |     30    |
| Deep Cross Gaming   |              6 |      0 |       6 |      0    |
| FURIA               |              6 |      0 |       6 |      0    |

## 5. Korunan eksik değerler
- teams.elder_dragon_rate: 3 NaN korundu (Deep Cross Gaming, Team Secret Whales, Top Esports)
- players: eksik değer yok
- champions: eksik değer yok

## 6. Son kontroller
- ✅ teams'te metin sütunu sadece `team`
- ✅ players'ta metin sütunları sadece player/team/position
- ✅ champions'ta metin sütunu sadece `champion`
- ✅ SUM(teams.wins) = 71
- ✅ players.winrate ≈ teams.winrate (±1 puan)
- ✅ champions'ta games_played ≥ 1 ve 101 satır
- ✅ champions'ta games_played ≥ 5: 63 satır
- ✅ champions'ta NaN yok

## Çıktı
- `data/processed/teams.csv`: 11 satır × 31 sütun
- `data/processed/players.csv`: 55 satır × 29 sütun
- `data/processed/champions.csv`: 101 satır × 21 sütun
