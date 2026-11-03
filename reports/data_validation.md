# Veri Doğrulama Raporu (Adım 2)

Kaynak: Kaggle `stuker/league-of-legends-msi-2026` (CC BY 4.0, Eduardo Stückrath; Oracle's Elixir + Liquipedia).
Bu rapor `src/validate.py` tarafından üretildi; tüm sayılar kod çıktısıdır.

## 1. Şekil
| tablo     | dosya                |   satır |   sütun |
|:----------|:---------------------|--------:|--------:|
| teams     | msi_26_teams.csv     |      11 |      30 |
| players   | msi_26_players.csv   |      55 |      29 |
| champions | msi_26_champions.csv |     104 |      21 |

## 2. CSV başlıkları vs Data_Dictionary.md
- **teams**: sözlükte 30, CSV'de 30 sütun | sözlükte olup CSV'de olmayan: yok | CSV'de olup sözlükte olmayan: yok | sıra aynı: True
- **players**: sözlükte 29, CSV'de 29 sütun | sözlükte olup CSV'de olmayan: yok | CSV'de olup sözlükte olmayan: yok | sıra aynı: True
- **champions**: sözlükte 21, CSV'de 21 sütun | sözlükte olup CSV'de olmayan: yok | CSV'de olup sözlükte olmayan: yok | sıra aynı: True

## 3. Sütun tipleri
### teams
- dtype dağılımı: {'str': 14, 'float64': 10, 'int64': 6}
- '%' içeren metin sütunları (13): gold_spent_difference, first_blood_rate, first_tower_rate, first_to_three_towers_rate, rift_herald_rate, grub_control_rate, first_dragon_rate, dragon_control_rate, elder_dragon_rate, first_baron_rate, baron_control_rate, lane_control, jungle_control
- Diğer metin sütunları: team
- '%' sütunlarında parse sorunu: yok (hepsi temiz parse ediliyor)

### players
- dtype dağılımı: {'str': 13, 'int64': 10, 'float64': 6}
- '%' içeren metin sütunları (10): winrate, counter_pickrate, kill_participation, teams_kill_share, team_deaths_share, first_blood_rate, cs_post_15_share, damage_share, team_damage_post_15_share, gold_share
- Diğer metin sütunları: player, team, position
- '%' sütunlarında parse sorunu: yok (hepsi temiz parse ediliyor)

### champions
- dtype dağılımı: {'float64': 19, 'str': 1, 'int64': 1}
- '%' içeren metin sütunları (0): yok
- Diğer metin sütunları: champion
- '%' sütunlarında parse sorunu: yok (hepsi temiz parse ediliyor)

## 4. Eksik değerler
### teams: toplam 3 eksik hücre
| sütun             |   eksik | satırlar                                           |
|:------------------|--------:|:---------------------------------------------------|
| elder_dragon_rate |       3 | Deep Cross Gaming, Team Secret Whales, Top Esports |

### players: toplam 0 eksik hücre

### champions: toplam 48 eksik hücre
| sütun                    |   eksik | satırlar                  |
|:-------------------------|--------:|:--------------------------|
| pick_rate                |       3 | Kennen, Rek'Sai, Malphite |
| ban_rate                 |       3 | Kennen, Rek'Sai, Malphite |
| pick_ban_rate            |       3 | Kennen, Rek'Sai, Malphite |
| winrate                  |       3 | Kennen, Rek'Sai, Malphite |
| counter_pickrate         |       3 | Kennen, Rek'Sai, Malphite |
| kda                      |       3 | Kennen, Rek'Sai, Malphite |
| kill_participation       |       3 | Kennen, Rek'Sai, Malphite |
| gold_diff_10             |       3 | Kennen, Rek'Sai, Malphite |
| xp_diff_10               |       3 | Kennen, Rek'Sai, Malphite |
| cs_diff_10               |       3 | Kennen, Rek'Sai, Malphite |
| cspm                     |       3 | Kennen, Rek'Sai, Malphite |
| damage_per_minute        |       3 | Kennen, Rek'Sai, Malphite |
| damage_share             |       3 | Kennen, Rek'Sai, Malphite |
| gold_share               |       3 | Kennen, Rek'Sai, Malphite |
| wards_per_minute         |       3 | Kennen, Rek'Sai, Malphite |
| wards_cleared_per_minute |       3 | Kennen, Rek'Sai, Malphite |

## 5. Tekrarlı satırlar
- **teams**: tam tekrar 0 | anahtar (team) tekrarı 0
- **players**: tam tekrar 0 | anahtar (player, team) tekrarı 0
- **champions**: tam tekrar 0 | anahtar (champion) tekrarı 0
- players: `player` adı tek başına tekrar: 0

## 6. Tutarlılık kontrolleri
- teams: SUM(games_played)=142, SUM(wins)=71, SUM(loses)=71 → toplam maç = 71 (wins == loses: True, games_played/2 == wins: True)
- teams: wins + loses ≠ games_played olan takım: 0
- players.team içinde teams'te olmayan: yok | teams'te olup players'ta olmayan: yok
- Takım başına oyuncu sayısı: {5: 11} (sayı: takım adedi)
- Pozisyon setleri: {"['ADC', 'Jungle', 'Middle', 'Support', 'Top']": 11}
- Pozisyon dağılımı: {'ADC': 11, 'Support': 11, 'Top': 11, 'Middle': 11, 'Jungle': 11}

### Oyuncu games_played = takım games_played mı?
- Eşleşmeyen oyuncu: **0 / 55**
- Oyuncu `winrate` ile takım wins/games_played (yuvarlanmış %) farkı >1 puan olan oyuncu: 0

### Oyuncu kills toplamı = takım kills mı?
- Farkı 0 olmayan takım: 0 / 11

### Şampiyonlar
- games_played = 0: 3 şampiyon → Kennen, Rek'Sai, Malphite
  - Bu satırlarda boş olmayan diğer metrik sayısı (pick/ban hariç): 9
  - Boş olmayan sütunlar: ['kills', 'deaths', 'assists'] → değerler: {'kills': [0.0, 0.0, 0.0], 'deaths': [0.0, 0.0, 0.0], 'assists': [0.0, 0.0, 0.0]}
  - pick_rate/ban_rate/pick_ban_rate: hepsi NaN mı? True (yani bu şampiyonlar hiç banlanmamış da olabilir; ban bilgisi kayıp)
- games_played ≥ 5: **63** şampiyon
- SUM(champions.games_played) = 710 (beklenen 10 × 71 maç = 710)
- pick_rate ≈ games_played / 71 × 100 tutmayan şampiyon: 1
| champion   |   games_played |   pick_rate |   pick_rate_calc |
|:-----------|---------------:|------------:|-----------------:|
| Pantheon   |              8 |        12.7 |             11.3 |
- pick_rate + ban_rate ≈ pick_ban_rate tutmayan şampiyon: 1
| champion   |   pick_rate |   ban_rate |   pick_ban_rate |
|:-----------|------------:|-----------:|----------------:|
| Pantheon   |        12.7 |        5.6 |            16.9 |

## 7. Float artıkları (ondalık hanesi > 2)
- **teams**: 0 hücre, 0 sütun
- **players**: 0 hücre, 0 sütun
- **champions**: 132 hücre, 13 sütun (winrate, counter_pickrate, kda, kill_participation, gold_diff_10, xp_diff_10, cs_diff_10, cspm, damage_per_minute, damage_share, gold_share, wards_per_minute, wards_cleared_per_minute)

## 8. Değer aralıkları (aykırı/imkânsız değer taraması)
### teams
| sütun                      |   count |      min |   medyan |     max |
|:---------------------------|--------:|---------:|---------:|--------:|
| games_played               |      11 |     6    |    12    |   21    |
| wins                       |      11 |     0    |     6    |   15    |
| loses                      |      11 |     6    |     6    |    9    |
| average_game_duration      |      11 |    30.4  |    32.8  |   34.7  |
| kills                      |      11 |    67    |   224    |  385    |
| deaths                     |      11 |   117    |   193    |  340    |
| kd                         |      11 |     0.46 |     0.98 |    1.36 |
| combined_kills_per_minute  |      11 |     0.87 |     1.04 |    1.17 |
| gold_percent_rating        |      11 |    -2.26 |    -0.02 |    0.9  |
| gold_spent_difference      |      11 |   -13.6  |     0.3  |    4.6  |
| early_game_rating          |      11 |    31.3  |    47.2  |   63.7  |
| mid_late_rating            |      11 |   -31.5  |     1.3  |   13.8  |
| gold_diff_15               |      11 | -2572    |  -184    | 1399    |
| first_blood_rate           |      11 |    20    |    53    |   71    |
| first_tower_rate           |      11 |     0    |    50    |   76    |
| first_to_three_towers_rate |      11 |     0    |    44    |   75    |
| turret_plates_destroyed    |      11 |    12.3  |    27    |   33    |
| rift_herald_rate           |      11 |    22    |    50    |   70    |
| grub_control_rate          |      11 |    23    |    55    |   63    |
| first_dragon_rate          |      11 |    24    |    56    |   70    |
| dragon_control_rate        |      11 |    30    |    51    |   57    |
| elder_dragon_rate          |       8 |     0    |    25    |  100    |
| first_baron_rate           |      11 |    17    |    44    |   71    |
| baron_control_rate         |      11 |    25    |    47    |   63    |
| lane_control               |      11 |    48.1  |    49.5  |   51.3  |
| jungle_control             |      11 |    43.3  |    49.2  |   52.9  |
| wards_per_minute           |      11 |     3.45 |     3.84 |    4.22 |
| control_wards_per_minute   |      11 |     1.45 |     1.62 |    2.08 |
| wards_cleared_per_minute   |      11 |     1.5  |     1.64 |    1.71 |
- 0–100 aralığı dışında oran değeri: yok

### players
| sütun                     |   count |     min |   medyan |      max |
|:--------------------------|--------:|--------:|---------:|---------:|
| games_played              |      55 |    6    |    12    |    21    |
| winrate                   |      55 |    0    |    40    |    71    |
| counter_pickrate          |      55 |   17    |    50    |   100    |
| kills                     |      55 |    6    |    35    |   175    |
| deaths                    |      55 |   18    |    39    |    82    |
| assists                   |      55 |   18    |    86    |   250    |
| kda                       |      55 |    1.1  |     3.2  |     7.2  |
| kill_participation        |      55 |   44.8  |    65.4  |    82.8  |
| teams_kill_share          |      55 |    3.9  |    20.5  |    45.5  |
| team_deaths_share         |      55 |   11.6  |    20    |    27.5  |
| first_blood_rate          |      55 |    0    |    20    |    67    |
| gold_diff_10              |      55 | -438    |    -7    |   382    |
| xp_diff_10                |      55 | -386    |   -29    |   284    |
| cs_diff_10                |      55 |  -12.2  |    -0.7  |     6.9  |
| cspm                      |      55 |    0.9  |     8    |    10.3  |
| cs_post_15_share          |      55 |    1.9  |    23.4  |    32.4  |
| damage_per_minute         |      55 |  210    |   573    |   965    |
| damage_share              |      55 |    7.2  |    21.7  |    32.3  |
| team_damage_post_15_share |      55 |    5.5  |    20.5  |    36.3  |
| turret_damage_per_game    |      55 |   79    |  4412    | 10479    |
| average_gold_per_minute   |      55 |  125    |   269    |   404    |
| gold_share                |      55 |   10.4  |    20.5  |    29.4  |
| neutral_objectives_stolen |      55 |    0    |     0    |     5    |
| wards_per_minute          |      55 |    0.33 |     0.44 |     2.43 |
| control_wards_per_minute  |      55 |    0.08 |     0.21 |     1.12 |
| wards_cleared_per_minute  |      55 |    0.12 |     0.32 |     0.6  |
- 0–100 aralığı dışında oran değeri: yok

### champions
| sütun                    |   count |     min |   medyan |     max |
|:-------------------------|--------:|--------:|---------:|--------:|
| games_played             |     104 |    0    |     6    |   19    |
| kills                    |     104 |    0    |    12.5  |   86    |
| deaths                   |     104 |    0    |    19.5  |   91    |
| assists                  |     104 |    0    |    43.5  |  217    |
| pick_rate                |     101 |    1.4  |     8.5  |   26.8  |
| ban_rate                 |     101 |    0    |     4.2  |   57.7  |
| pick_ban_rate            |     101 |    1.4  |    14.1  |   71.8  |
| winrate                  |     101 |    0    |    50    |  100    |
| counter_pickrate         |     101 |    0    |    67    |  100    |
| kda                      |     101 |    0.7  |     3.3  |   21.5  |
| kill_participation       |     101 |   39.5  |    63.7  |  100    |
| gold_diff_10             |     101 | -717    |    21.69 | 1143    |
| xp_diff_10               |     101 | -644    |     3    |  639    |
| cs_diff_10               |     101 |  -21.5  |     0    |   20    |
| cspm                     |     101 |    0.7  |     7.9  |   10.6  |
| damage_per_minute        |     101 |  110    |   591    | 1106    |
| damage_share             |     101 |    4.6  |    21.2  |   34    |
| gold_share               |     101 |    9.1  |    21.2  |   31.4  |
| wards_per_minute         |     101 |    0.22 |     0.46 |    2.47 |
| wards_cleared_per_minute |     101 |    0.09 |     0.29 |    0.75 |
- 0–100 aralığı dışında oran değeri: yok

## 9. TASK.md iddialarının kontrolü
| iddia                                              | sonuç   |
|:---------------------------------------------------|:--------|
| teams 11×30, players 55×29, champions 104×21       | ✅ doğru |
| Toplam 71 maç, sum(games_played)=142, sum(wins)=71 | ✅ doğru |
| Sütun adı `loses`                                  | ✅ doğru |
| elder_dragon_rate 3 takımda NaN (DCG, TSW, TES)    | ✅ doğru |
| Kennen, Rek'Sai, Malphite games_played=0           | ✅ doğru |
| ≥5 maçlı şampiyon sayısı 63                        | ✅ doğru |
| Her oyuncunun games_played'i takımınınkine eşit    | ✅ doğru |
| 6 maçta kalan takımlar: Deep Cross Gaming, FURIA   | ✅ doğru |

- 6 maçlı takımlar: ['Deep Cross Gaming', 'FURIA']
- games_played dağılımı (takım): {'T1': 21, 'Hanwha Life Esports': 20, 'Bilibili Gaming': 17, 'LYON': 17, 'G2 Esports': 15, 'Team Liquid': 12, 'Team Secret Whales': 10, 'Karmine Corp': 9, 'Top Esports': 9, 'Deep Cross Gaming': 6, 'FURIA': 6}
