# TASK: MSI 2026 — Early Game vs Objective Control

## Bağlam
- Kaggle linki: https://www.kaggle.com/datasets/stuker/league-of-legends-msi-2026
- Lisans: CC BY 4.0 (doğrulandı, LICENSE dosyası). Attribution zorunlu: Eduardo Stückrath, kaynak Oracle's Elixir + Liquipedia.
- Seviye: 2 (SQL + Dashboard)
- Süre bütçesi: 2 hafta, haftada 4-5 saat (toplam ~8-10 saat)

## Ana soru
MSI 2026'da daha çok kazanan takımlar erken oyunda mı öne çıkıyor (gold_diff_15, first_tower_rate), yoksa obje kontrolünde mi (dragon_control_rate, baron_control_rate)?

Yedek sorular:
1. En az 5 maç oynanmış şampiyonlarda pick_ban_rate ile winrate arasında ilişki var mı?
2. Takım kazanma oranıyla en çok hangi rolün gold_diff_10 değeri birlikte hareket ediyor?

## Veri bilgisi
- Dosyalar (doğrulandı):
  - `msi_26_teams.csv`: 11 satır, 30 sütun
  - `msi_26_players.csv`: 55 satır, 29 sütun (5 rol × 11 oyuncu)
  - `msi_26_champions.csv`: 104 satır, 21 sütun
- Toplam maç: 71 (takımlarda sum(games_played)=142, sum(wins)=71). Doğrulandı.
- Anahtar: `teams.team` = `players.team`. Şampiyon tablosunun takım veya oyuncu anahtarı yok, diğer tablolarla JOIN edilemez.
- Bilinen sütunlar: Data_Dictionary.md'deki tüm sütunlar CSV başlıklarıyla eşleşiyor (doğrulandı). Not: sütun adı `loses` (losses değil).
- Bilinen riskler:
  - **Metin olarak oranlar:** teams ve players tablolarında oranlar "65%" biçiminde metin. Sayıya çevrilecek.
  - **elder_dragon_rate:** 3 takımda NaN (Deep Cross Gaming, Team Secret Whales, Top Esports). Büyük ihtimalle "elder çıkmadı" anlamında. 0 ile doldurma, analizden çıkar.
  - **Oynanmamış şampiyonlar:** Kennen, Rek'Sai ve Malphite games_played=0, tüm metrikleri boş. Analizden çıkar.
  - **Float artıkları:** champions tablosunda 15.299999 gibi değerler var. Göstermeden önce yuvarla.
  - **Küçük örneklem:** 11 takım. Korelasyonlar kararsız, tek takım sonucu değiştirebilir.
  - **Rakip gücü yanlılığı:** 6 maçta kalan takımlar (Deep Cross Gaming, FURIA) farklı aşamada farklı rakiplerle oynadı. Takımlar aynı koşullarda karşılaştırılmıyor.
  - **Ters nedensellik:** Baron ve ejder genelde zaten öndeyken alınır. "Obje kontrolü kazandırıyor" demek yanlış olur.
  - **Opak metrikler:** early_game_rating ve mid_late_rating bileşik metrikler, formülü veri sözlüğünde de yok (doğrulama: 2026-11-03, sadece "Composite metric" yazıyor). Ana analizde kullanma, sadece ek bilgi olarak göster.
  - **Şampiyon winrate gürültüsü:** az maçta winrate güvenilmez. Min. 5 maç filtresi uygula (bu filtreyle 63 şampiyon kalıyor; yeniden doğrula).

## Kurallar
1. Önce `DEVLOG.md` ve bu dosyayı oku. Her adımın sonunda `DEVLOG.md`'ye kayıt ekle.
2. İlk adım veriyi doğrulamak: indir (`kaggle datasets download -d stuker/league-of-legends-msi-2026 -p data/ --unzip`), şekli, sütun tiplerini, eksik değerleri, tekrarlı satırları raporla. Ayrıca kontrol et: her oyuncunun games_played değeri takımınınkiyle eşit mi? Bu rapor bu dosyadaki "DOĞRULANMADI" ifadelerini düzeltir.
3. Veri `data/` altında kalır ve git'e girmez (`.gitignore`).
4. Sonuç uydurma. Her sayı kodun çıktısından gelsin. Çalıştırmadığın analizi bulgu diye yazma.
5. Her grafik: başlık, eksen adı, birim, tek cümle okuma notu.
6. Her bulgunun yanına bir sınırlama yaz.
7. Varsayım yaptıysan `DEVLOG.md`'de "Karar ve varsayımlar" altına yaz.
8. Kapsamı büyütme. Ana soru dışında bir şeye 30 dakikadan fazla harcama, "Sonraki adımlar"a not düş.
9. Büyük bir karar gerekiyorsa (veri silme, soruyu değiştirme) dur ve İbrahim'e sor.
10. ML yok. p-değeri ve hipotez testi yok (bu Seviye 3 işi). Analiz betimseldir: sıralama, Spearman korelasyonu, grup ortalamaları. Hiçbir yerde "kazandırır" veya "neden olur" dili kullanma.

## Adımlar
1. [x] Repo iskeleti: `data/`, `notebooks/`, `figures/`, `src/`, `sql/`, `app/`, `requirements.txt`, `.gitignore`
2. [x] Veriyi indir ve doğrula
3. [x] Temizleme (`src/clean.py`): % metinlerini float'a çevir, 0 maçlı şampiyonları çıkar, float'ları yuvarla, `winrate = wins / games_played` türet. Her kararı logla.
4. [x] SQLite yükleme (`src/load_db.py`): `data/msi26.db` içinde `teams`, `players`, `champions` tabloları.
5. [x] Keşifsel analiz (notebook): dağılımlar, takım sıralaması.
6. [x] Ana soru:
   - Erken grup: gold_diff_15, first_tower_rate, first_blood_rate, first_to_three_towers_rate
   - Obje grubu: dragon_control_rate, baron_control_rate, grub_control_rate, first_dragon_rate
   - Her metrik için winrate ile Spearman korelasyonu (n=11, betimsel)
   - İki scatter: gold_diff_15 vs winrate, baron_control_rate vs winrate; her nokta takım adıyla etiketli
   - Tek takımı çıkarınca (leave-one-out) korelasyon ne kadar oynuyor? Kararlılık notu olarak raporla.
7. [x] En iyi 3-5 grafiği `figures/` altına kaydet.
8. [x] 3 bulgu + sınırlamalar + ürün çıkarımı
9. [x] README'yi doldur
10. [x] Kontrol listesi (`05-kalite-kontrol.md`): notebook baştan sona temiz çalışıyor mu?

## Seviyeye özel ek adımlar (Seviye 2)

### SQL soruları (`sql/queries.sql`, her biri yorum satırıyla soru + çıktı özeti)
1. Veri tutarlılığı: SUM(wins) = SUM(loses) = toplam maç sayısı mı?
2. Takımları winrate'e göre sırala (`RANK() OVER`).
3. Takımları winrate'e göre 3 kademeye ayır (`NTILE(3)`), her kademenin ortalama gold_diff_15, first_tower_rate, dragon_control_rate, baron_control_rate değerleri.
4. %50 üstü ve altı winrate'li takımların erken ve obje metrik ortalamaları (`CASE` + `GROUP BY`).
5. Rol bazında: kazanan takımların (winrate > 50%) ve diğerlerinin ortalama gold_diff_10 değeri (`JOIN players-teams`, `GROUP BY position`).
6. Her takımda en yüksek damage_share'e sahip oyuncu (`ROW_NUMBER() OVER (PARTITION BY team)`).
7. Her oyuncunun KDA'sının takım ortalamasından farkı (`AVG() OVER (PARTITION BY team)`), en büyük 10 sapma.
8. Doğrulama: oyuncu kills toplamı / takım kills ile `teams_kill_share` sütunu tutuyor mu?
9. En az 5 maçlı şampiyonlarda pick_ban_rate ilk 10 ve winrate değerleri.
10. "Korkulan ama oynanmayan" şampiyonlar: ban_rate > pick_rate, en az 5 maç.
11. Rol bazında en yüksek ortalama cs_diff_10 ve gold_diff_10 değerine sahip ilk 3 oyuncu (`DENSE_RANK() OVER (PARTITION BY position)`).

### Dashboard (Streamlit, `app/dashboard.py`)
- Sekme 1 **Teams:** metrik seçimli scatter (x: seçilen metrik, y: winrate), takım etiketli. Altında korelasyon tablosu.
- Sekme 2 **Players:** rol ve takım filtresi, KDA / gold_diff_10 / damage_share tablosu ve bar chart.
- Sekme 3 **Champions:** min. maç slider'ı (varsayılan 5), pick_ban_rate vs winrate scatter.
- Dashboard SQLite'tan okur, CSV'den değil. Ekran görüntüsü `figures/dashboard.png` olarak kaydedilir.

## Teslim
- Çalışır notebook, `sql/queries.sql`, `app/dashboard.py`, `figures/`, doldurulmuş `README.md` ve `DEVLOG.md`
- Çıktının sonunda: 3 bulgu, 3 sınırlama, 1 ürün çıkarımı, LinkedIn taslağı için ham notlar
