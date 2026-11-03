# DEVLOG: MSI 2026 — Early Game vs Objective Control

Durum: Tamamlandı (Adım 1–10). Public repo: https://github.com/ibrahimbinbuga/msi-2026-early-game-vs-objectives
Başlangıç: 2026-11-03

## Karar ve varsayımlar
- 2026-11-03 | Seviye 2 seçildi | 3 ilişkili tablo var; n=11 takım hipotez testi için yetersiz
- 2026-11-03 | p-değeri ve ML yok, analiz betimsel | Örneklem çok küçük, kapsam şişmesin
- 2026-11-03 | early_game_rating ve mid_late_rating ana analizde yok | Bileşik metrik, formülü bilinmiyor
- 2026-11-03 | Şampiyon analizinde min. 5 maç filtresi | Az maçta winrate gürültülü
- 2026-11-03 | Doğrulama raporu `reports/data_validation.md` altında, `src/validate.py` ile üretiliyor | İskelette rapor klasörü yoktu; tek ek klasör, tekrar üretilebilir olsun diye
- 2026-11-03 | Yerel ortam `.venv/` (Python 3.15, pandas 3.1); `.gitignore`'da | Sistem Python'unda pandas yoktu
- 2026-11-03 | elder_dragon_rate NaN ≠ 0 kabul edildi | FURIA'da 0% var, 3 takımda NaN; yani NaN "elder hiç çıkmadı", 0% "çıktı ama rakip aldı" demek (varsayım, kaynakta yazmıyor)
- 2026-11-03 | Oranlar yüzde puanı (0–100) ölçeğinde tutuldu, 0–1'e çevrilmedi | champions zaten 0–100; üç tablo aynı ölçekte olsun. TASK'taki `winrate = wins / games_played` bu yüzden ×100 ile türetildi
- 2026-11-03 | '%' sütunları açıkça float'a çevrildi | "65%" → int64 → SQLite INTEGER olur; SQL'de tam sayı bölmesi riski. Sayım sütunları (wins, games_played...) INTEGER kaldı: SQL'de oran hesaplarken `1.0 *` ile çarp
- 2026-11-03 | Tüm float'lar 2 ondalığa yuvarlandı (temizlemede) | Sadece champions'ta 132 hücre etkilendi; 2 ondalık analiz için kayıpsız
- 2026-11-03 | Temiz veri `data/processed/`, DB `data/msi26.db` | İkisi de `data/` altında, git'e girmez
- 2026-11-03 | Repo'ya dönük çıktılar (notebook, grafikler, README) İngilizce; DEVLOG ve reports/ Türkçe | README şablonu İngilizce, portföy/LinkedIn için
- 2026-11-03 | Grafik renkleri: erken grup mavi #2a78d6, obje grubu turuncu #eb6834 | dataviz referans paletinin ilk 2 slotu (renk körlüğü dahil tüm çiftlerde doğrulanmış)
- 2026-11-03 | Ek kararlılık kontrolü: 6 maçlı iki takım (DCG, FURIA) birlikte çıkarılınca ρ | TASK'taki rakip gücü riski için; tek takım çıkarma bunu yakalamıyor
- 2026-11-03 | Grup karşılaştırması için ortalama ρ verildi ama ana yorum metrik bazında | 4 korelasyonun ortalaması kaba özet; gruptaki tek metrik ortalamayı sürüklüyor
- 2026-11-03 | "Erken" oyun süresine göre yorumlanıyor (İbrahim'in yönlendirmesi) | Ortalama maç 32.5 dk (maç ağırlıklı); 15. dakika maçın ~%46'sı (takıma göre %43–49), yani başlangıç değil yaklaşık orta nokta
- 2026-11-03 | first_to_three_towers_rate erken oyun kanıtı sayılmıyor, ayrı raporlanıyor; gruplar TASK'taki gibi kaldı | Veride zamanı yok; gold_diff_15 tek zaman damgalı metrik. Her metriğe "timing_in_data" etiketi eklendi (fixed: minute 15 / untimed event / whole-game share)
- 2026-11-03 | Pantheon pick_rate tutarsızlığı (12.7 vs hesaplanan 11.3) olduğu gibi bırakılacak, notlanacak | Tek satır, ana soruyu etkilemiyor; ana kaynağı değiştirmek yerine raporlamak

## Kayıtlar

### 2026-11-03 | Adım 1: Repo iskeleti
- Yapılan: `data/ notebooks/ figures/ src/ sql/ app/` oluşturuldu (boşlar `.gitkeep` ile), `requirements.txt`, `.gitignore` (data/, *.db, .venv, checkpoints), `.venv` kuruldu.
- Bulunan: Proje henüz git reposu değil (`git init` yapılmadı, İbrahim'e bırakıldı).
- Sorun: Sistem Python'unda pandas yok → `.venv`.
- Süre: ~5 dk
- Sonraki: Adım 2

### 2026-11-03 | Adım 2: Veriyi indir ve doğrula
- Yapılan: Kaggle'dan indirildi (`data/`), `src/validate.py` yazıldı → `reports/data_validation.md`.
- Bulunan: TASK.md'deki 8 iddianın 8'i doğrulandı (şekiller, 71 maç, `loses`, elder NaN takımları, 0 maçlı 3 şampiyon, ≥5 maçlı 63 şampiyon, oyuncu games_played = takım games_played 55/55, 6 maçlı takımlar DCG + FURIA). Ek kontroller: oyuncu kills toplamı = takım kills (11/11), oyuncu winrate = takım wins/games (55/55), SUM(champions.games_played)=710 = 10×71.
- Sorun: Pantheon'da pick_rate 12.7 ama games_played/71 = 11.3 (ve pick+ban ≠ pick_ban). Teams tablosunda `winrate` sütunu yok, türetilecek. Pandas 3'te metin sütunları `object` değil `str` dtype; betik buna göre düzeltildi.
- Süre: ~20 dk
- Sonraki: Adım 3 (`src/clean.py`)

### 2026-11-03 | Adım 3: Temizleme
- Yapılan: `src/clean.py` → `data/processed/*.csv`, log `reports/cleaning_log.md`. teams 13 + players 10 '%' sütunu float'a; 0 maçlı 3 şampiyon çıkarıldı (101 kaldı); float'lar 2 ondalık; `teams.winrate` türetildi (`loses`'tan sonra, teams artık 31 sütun).
- Bulunan: Winrate sıralaması T1 71.43 > HLE 65.00 > BLG = LYON 64.71 > TL 50.00 > G2 40.00 > KC = TES 33.33 > TSW 30.00 > DCG = FURIA 0.00. Beraberlikler var (BLG/LYON, KC/TES, DCG/FURIA) → Spearman'da ortalama sıra kullanılacak. 8 son kontrolün 8'i geçti.
- Sorun: İlk sürümde '%' sütunları int64 kalıyordu, float'a zorlandı.
- Süre: ~15 dk
- Sonraki: Adım 4

### 2026-11-03 | Adım 4: SQLite yükleme
- Yapılan: `src/load_db.py` → `data/msi26.db` (teams 11, players 55, champions 101 satır). Anahtarlara unique index: teams(team), players(player, team), champions(champion).
- Bulunan: 7 kontrolün 7'si geçti (satır sayıları, SUM(wins)=SUM(loses)=71, JOIN'de eşleşmeyen oyuncu 0, elder NULL 3). SQLite 3.54.1, window fonksiyonları çalışıyor.
- Sorun: yok
- Süre: ~10 dk
- Sonraki: Adım 5 (keşifsel analiz notebook'u)

### 2026-11-03 | Adım 5–7: Keşif, ana soru, grafikler
- Yapılan: `notebooks/analysis.ipynb` (SQLite'tan okur; Bölüm A keşif, Bölüm B ana soru). `jupyter nbconvert --execute` ile baştan sona hatasız çalıştı (0 hata). 4 grafik `figures/` altında: 01_team_winrate, 02_spearman_by_metric, 03_gold15_vs_winrate, 04_baron_vs_winrate. Her grafikte başlık, eksen+birim, okuma notu var; notlardaki sayılar f-string ile koddan geliyor.
- Bulunan (hepsi betimsel, n=11):
  - Spearman ρ (winrate ile): first_to_three_towers 0.95, baron_control 0.87, gold_diff_15 0.85, first_tower 0.55, dragon_control 0.48, grub_control 0.32, first_blood 0.14, first_dragon −0.17.
  - Tek takım çıkarma: ilk üçü her durumda ≥ 0.80 (aralıklar 0.93–0.97, 0.83–0.91, 0.80–0.95). first_blood (−0.15…0.40) ve first_dragon (−0.33…0.05) işaret değiştiriyor.
  - Grup ortalaması ρ: erken 0.62, obje 0.37 (kaba özet).
  - DCG+FURIA çıkarılınca (n=9): first_tower 0.55 → 0.18, first_blood 0.14 → 0.77. Kırılgan.
  - Metrikler örtüşüyor: gold_diff_15 ~ first_to_three_towers 0.90, first_to_three_towers ~ baron 0.81.
  - **winrate ~ games_played ρ = 0.96**: format etkisi (elenen takım daha az oynuyor, farklı rakiplerle).
  - gold_diff_15 en etkili takım KC (+544 gold, %33 winrate); KC çıkınca ρ 0.95.
- Sorun: 02 grafiğinde lejant bir satırın üstüne biniyordu, düzeltildi.
- Süre: ~45 dk
- Sonraki: Adım 8 (3 bulgu + sınırlamalar), sonra SQL ve dashboard

### 2026-11-03 | Adım 6 ek: Oyun süresi bağlamı
- Yapılan: Notebook'a B1b bölümü eklendi (oyun süresi, 15. dakikanın maçtaki payı, süre ile metriklerin ρ'su, metrik zamanlama etiketi). B5 yorumu güncellendi. Notebook yeniden baştan sona çalıştı, 0 hata.
- Bulunan: Ortalama süre takım bazında 30.4–34.7 dk, maç ağırlıklı 32.5 dk. Süre ile winrate ρ = 0.07; süre ile 8 metriğin hiçbiri arasında |ρ| > 0.29 yok. Yani sonuçlar kısa/uzun oyun farkından gelmiyor.
- Sorun: Olay metriklerinin (ilk kule, ilk 3 kule, ilk kan, ilk ejder) zamanı veride yok.
- Süre: ~15 dk

### 2026-11-03 | Adım 8 + Seviye 2: Bulgular, SQL, dashboard
- Yapılan: 3 bulgu + sınırlama + ürün çıkarımı (aşağıda). `sql/queries.sql` 11 sorgu, her birinde soru + gerçek çıktı özeti; `src/run_queries.py` hepsini çalıştırıyor. `app/dashboard.py` (Streamlit, SQLite'tan okur): Teams / Players / Champions sekmeleri; üçü de hatasız render edildi (Playwright, sayfada exception 0, konsol hatası 0). `figures/dashboard.png` kaydedildi.
- Bulunan: Q8: teams_kill_share = oyuncu kills / takım kills × 100 (55/55, maks fark 0.05). Q10: ban_rate > pick_rate olan 20 şampiyon. Q6: 11 takımın 8'inde en yüksek damage share ADC'de. Dashboard: ≥5 maçlı şampiyonlarda pick_ban ~ winrate ρ = 0.45.
- Sorun: Headless Chrome Streamlit'i render olmadan çekiyordu → Playwright (sistem Chrome'u) ile render beklenerek çekildi. Q4/Q5'te TL tam %50, "<= 50%" grubuna kondu (SQL yorumunda yazıyor).
- Süre: ~45 dk

### 2026-11-03 | Adım 9–10: README ve kalite kontrol
- Yapılan: README dolduruldu (özet, 3 bulgu, sınırlamalar, ürün çıkarımı, dashboard, veri, yöntem, tekrar üretim). `05-kalite-kontrol.md`: repo'nun verisiz kopyası + sıfırdan kurulan ortamda tüm hat README komutlarıyla çalıştırıldı.
- Bulunan: Notebook 0 hata, metin çıktıları birebir aynı; SQL çıktısı ve temizleme logu birebir aynı; dashboard AppTest'te 0 exception. Nedensellik dili taraması temiz.
- Sorun: Streamlit `use_container_width` uyarısı → `width="stretch"`.
- Süre: ~30 dk

### 2026-11-03 | Eksik tamamlama
- Yapılan: README "Reproduce" bloğuna Kaggle indirme komutu ve API token notu eklendi (önceden blok tek başına çalıştırılınca veri yok hatası verirdi). Notebook'a B6 (yedek sorular, Spearman + kararlılık) eklendi; 02 grafiğinde "First to 3 towers" satırına "timing not in data" notu eklendi. Notebook yeniden çalıştı, 0 hata.
- Bulunan: Şampiyon ρ eşiğe duyarlı (0.25–0.45); varsayılan 5 maç eşiği en yüksek değeri veriyor, README'de belirtildi.
- Süre: ~15 dk

## Veri kalite notları
- Satır/sütun: teams 11×30, players 55×29, champions 104×21. Başlıklar Data_Dictionary.md ile birebir ve aynı sırada.
- Eksik değerler: teams 3 hücre (elder_dragon_rate: DCG, TSW, TES). players 0. champions 48 hücre = 3 şampiyon (Kennen, Rek'Sai, Malphite) × 16 sütun; bu satırlarda kills/deaths/assists = 0, pick/ban oranları dahil diğer her şey NaN.
- Tekrarlı satırlar: 0 (tam satır ve anahtar bazında, üç tabloda da).
- Metin oranlar: teams 13 sütun, players 10 sütun "%" metni; hepsi temiz parse ediliyor. champions'ta % metni yok (zaten sayı).
- Float artıkları: sadece champions, 132 hücre / 13 sütun.
- Aykırı değerler: 0–100 dışı oran yok. Dikkat: DCG gold_diff_15 = -2572 (medyan -184), first_tower_rate = 0%; tek takım korelasyonu sürükleyebilir → leave-one-out şart. elder_dragon_rate sadece 0/50/100 gibi kaba değerler alıyor (8 takım).
- Tutarsızlık: Pantheon pick_rate 12.7 (beklenen 11.3).
- Silinen/değiştirilen: champions'tan 3 satır (Kennen, Rek'Sai, Malphite; 0 maç). 23 '%' sütunu float'a çevrildi. champions'ta 132 hücre 2 ondalığa yuvarlandı. teams'e `winrate` eklendi. Başka hiçbir şey değişmedi; elder NaN'ları korundu.

## Bulgular (analiz bittikten sonra doldurulur)
| # | Bulgu | Kanıt (sayı/grafik) | Sınırlama |
|---|-------|---------------------|-----------|
| 1 | Maçın yaklaşık ortasında (15. dk ≈ 32.5 dk'lık ortalama maçın %46'sı) altında önde olan takımlar daha yüksek winrate'e sahip. | gold_diff_15 ~ winrate ρ = 0.85, tek takım çıkarınca 0.80–0.95; >%50 takımlar ort. +713, diğerleri −934 (SQL Q4). `figures/03_gold15_vs_winrate.png` | n = 11; winrate ~ games_played ρ = 0.96 (elenen takım farklı rakiplerle daha az oynadı); KC (+544, %33) istisna. |
| 2 | Baron kontrolü de aynı güçte birlikte hareket ediyor ama "önde olma" metrikleriyle büyük ölçüde örtüşüyor; ayrı bir sinyal gibi görünmüyor. | baron ~ winrate ρ = 0.87 (0.83–0.91); baron ~ first_to_three_towers ρ = 0.81, ~ gold_diff_15 0.64. `figures/04_baron_vs_winrate.png` | Ters nedensellik: Baron çoğunlukla zaten öndeki takım tarafından alınır. Takım ortalamaları maç içi sırayı göstermiyor. |
| 3 | Tek seferlik "ilk" olaylar kazananları ayırt etmiyor: ilk kan ve ilk ejder zayıf, işareti kararsız; ilk kule kırılgan. | first_blood ρ = 0.14 (−0.15…0.40), first_dragon −0.17 (−0.33…0.05); first_tower 0.55 → DCG+FURIA çıkınca 0.18. `figures/02_spearman_by_metric.png` | Olayların zamanı veride yok; oranlar 6–21 maçlık kaba ortalamalar, tek maç sonucu oynatabilir. |

Ana soruya cevap: Ne "erken oyun" ne "obje kontrolü" blok halinde öne çıkıyor (grup ort. ρ 0.62 vs 0.37, ama tek metrikler sürüklüyor). Kazanan takımları ayıran, maç ortasına kadar kurulan **kalıcı üstünlük** (altın@15, ilk 3 kule, Baron); tek seferlik "ilk" olaylar değil. Oyun süresi bu ilişkilere karışmıyor (|ρ| ≤ 0.29).

Yedek soru 1 (notebook B6): ≥5 maçlı 63 şampiyonda pick_ban_rate ~ winrate ρ = 0.45; eşik 3/5/8/10 maç için 0.27/0.45/0.41/0.25, yani eşiğe duyarlı ve 5 en yüksek değeri veriyor. Yedek soru 2 (notebook B6): rol bazında gold_diff_10 ~ takım winrate ρ: ADC 0.88 (tek takım çıkarınca 0.84–0.95), Top 0.57, Jungle 0.38, Mid 0.14, Support 0.00. SQL Q5 grup farkıyla tutarlı (en büyük fark ADC'de, 396.6).

## Ürün çıkarımı
Bir takım/maç analitiği ürünü (yayın grafiği, scouting paneli) "takım formu" göstergesi olarak tek seferlik "ilk" istatistiklerini (ilk kan, ilk ejder) öne çıkarmamalı; belirli bir dakikadaki altın farkı gibi kalıcı üstünlük metrikleri bu veride kazananlarla çok daha tutarlı birlikte hareket ediyor. (Betimsel, 11 takım; A/B ya da maç bazında doğrulanmadı.)

## Ne öğrendim
- "Erken oyun" tanımı oyun süresine bağlı: 32.5 dk'lık maçta 15. dakika aslında orta nokta. Metriğin zaman damgası olup olmadığı, hangi gruba ait olduğundan daha önemli.
- n = 11'de tek bir korelasyon yanıltıcı; tek takım çıkarma ve 6 maçlı takımları çıkarma kontrolleri ilk kule gibi "orta güçte" görünen metriklerin kırılgan olduğunu gösterdi.
- Turnuva formatı (elenen takım az oynar) winrate'i oynanan maç sayısıyla neredeyse aynı yapıyor (ρ = 0.96); bu, takım bazlı esports verisinde her analizin arka planında duran bir yanlılık.

## Sonraki adımlar (kapsam dışı kalanlar)
- first_to_three_towers_rate'in zamanı veride yok; maç bazında veriyle (olay dakikaları) gerçek fazı belirlenebilir. Şimdilik "erken–orta, zamanı bilinmiyor" olarak ayrı raporlanıyor.
- Maç bazında veri (Oracle's Elixir ham maç verisi) olsa "öndeyken obje alma" ayrıştırılabilirdi; bu veri setinde yok.

## LinkedIn için ham notlar
- Açılış cümlesi (bulgu ile başla): "MSI 2026'da kazanan takımları ilk kan ya da ilk ejder değil, maçın ortasına kadar kurdukları altın farkı ayırıyordu (15. dakika altın farkı ile winrate arasında Spearman ρ = 0.85, 11 takım)."
- Öne çıkan grafik: `figures/02_spearman_by_metric.png` (8 metrik, her biri tek takım çıkarma aralığıyla)
- Tek cümlelik ders: Küçük örneklemde korelasyonun kendisi kadar, bir takım çıkınca ne kadar oynadığı da raporlanmalı.
- Ek notlar: 15. dakika ≈ maçın %46'sı; Baron kontrolü de ρ = 0.87 ama "önde olma" ile örtüşüyor; ilk kan ρ = 0.14 ve işareti kararsız; SQL (window fonksiyonları) + Streamlit dashboard; veri: Eduardo Stückrath, Kaggle, CC BY 4.0 (etiketle/kaynak ver).
