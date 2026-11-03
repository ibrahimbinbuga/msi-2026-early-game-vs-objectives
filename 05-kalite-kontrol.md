# Kalite Kontrol (Adım 10)

Tarih: 2026-11-03. Kontroller kod çalıştırılarak yapıldı; sonuçlar komut çıktısından.

## Temiz ortamda tekrar üretilebilirlik
Repo'nun `data/`, `figures/`, `reports/` ve `.venv` olmadan bir kopyası alındı, `requirements.txt`'ten sıfır bir sanal ortam kuruldu (Python 3.15.2) ve README'deki komutlar sırayla çalıştırıldı.

| # | Kontrol | Sonuç |
|---|---------|-------|
| 1 | `pip install -r requirements.txt` sıfır ortamda kuruluyor | ✅ (pandas 3.1.0, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, streamlit 1.66.1, plotly 7.1.0) |
| 2 | Kaggle'dan indirme README'deki komutla çalışıyor | ✅ lisans CC BY 4.0 olarak raporlandı |
| 3 | `src/validate.py` çalışıyor | ✅ rapor içerik olarak aynı (tek fark: tabulate'in emoji sütun genişliği, 1 boşluk) |
| 4 | `src/clean.py` çalışıyor, 8 son kontrol geçiyor | ✅ log birebir aynı |
| 5 | `src/load_db.py` çalışıyor, 7 kontrol geçiyor | ✅ 7/7 |
| 6 | `src/run_queries.py`: 11 sorgu çalışıyor | ✅ çıktı birebir aynı |
| 7 | **Notebook baştan sona temiz çalışıyor** (`nbconvert --execute`) | ✅ 0 hata; tüm metin çıktıları repo'daki notebook ile birebir aynı |
| 8 | Notebook 4 grafiği `figures/` altına üretiyor | ✅ 01–04 |
| 9 | Dashboard (Streamlit AppTest): varsayılan açılış, 8 takım metriği, boş rol filtresi, 3 oyuncu metriği, slider 1/5/15/19 | ✅ 0 exception; boş durumlarda bilgi mesajı çıkıyor |
| 10 | Dashboard kullanımdan kalkan parametre uyarısı | ✅ `use_container_width` → `width="stretch"` düzeltildi, uyarı yok |

## İçerik kuralları (TASK.md)
| # | Kural | Durum |
|---|-------|-------|
| 1 | Her sayı kod çıktısından | ✅ Grafik okuma notları f-string ile hesaplanıyor; SQL özetleri `run_queries.py` çıktısından; README sayıları notebook/SQL çıktısıyla karşılaştırıldı |
| 2 | Her grafikte başlık, eksen adı, birim, tek cümle okuma notu | ✅ 4/4 grafik (01–04); dashboard grafiklerinde başlık + eksen + birim + alt not |
| 3 | Her bulgunun yanında sınırlama | ✅ DEVLOG bulgu tablosu ve README |
| 4 | Nedensellik dili yok, p-değeri / ML yok | ✅ "cause / drives / leads to / produces / kazandır / neden olur / p-value" taraması: yalnızca olumsuzlama cümleleri ("not cause", "no p-values") |
| 5 | Varsayımlar DEVLOG'da | ✅ "Karar ve varsayımlar" altında |
| 6 | Veri git'e girmiyor | ✅ `.gitignore`: `data/`, `*.db`, `*.zip` |
| 7 | Dashboard SQLite'tan okuyor | ✅ `data/msi26.db`, CSV okunmuyor |
| 8 | Attribution (CC BY 4.0) | ✅ README "Data" bölümü ve dashboard altbilgisi |

## Bilinen açık noktalar
- `figures/dashboard.png` Playwright + sistem Chrome'u ile çekildi; temiz ortam testinde yeniden çekilmedi (dashboard AppTest ile test edildi).
- Pantheon'un `pick_rate` değeri (12.7) games_played/71 (11.3) ile tutmuyor; analize etkisi yok, olduğu gibi bırakıldı.
- Python 3.15 dışında test edilmedi.
