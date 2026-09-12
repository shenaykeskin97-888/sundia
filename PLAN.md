# SmartLead AI (SUNDIA SPACE) — Adım Adım Yol Haritası

> ## Durum (12 Eylül 2026)
> | Modül | Durum |
> |-------|-------|
> | A · config.py | ✅ yazıldı, test edildi |
> | B · database.py | ✅ yazıldı, SQL injection testi geçti |
> | C · ai_service.py | ✅ yazıldı, demo modu çalışıyor |
> | D · routes.py | ✅ 5 uç nokta, katman sızıntısı yok |
> | E · fabrika + run.py | ✅ 6 rota kayıtlı |
> | F · uçtan uca test | ✅ 6 testin hepsi geçti |
> | G · Wix kodu | ✅ yazıldı — editörde ID'leri verip yapıştırman kaldı |
> | H · GitHub + Render | ✅ repo push edildi, servis kuruldu |
>
> **Canlı:** https://smartlead-ai-sbly.onrender.com
> **Repo:** https://github.com/FeeFiFoFumM/smartlead-ai
>
> **Eksik iki değer:** `.env` içinde `GROQ_API_KEY` (hâlâ placeholder) ve
> `CORS_ORIGINS` (hâlâ `*`). İkisi girilene kadar sohbet demo modunda çalışır.

Yönergedeki 8 modülün sırası, her modülün **kontrol noktası** ve
o noktayı geçtiğini kanıtlayan **test komutu**.

> Kural: Bir modülün kontrol noktası geçmeden bir sonrakine geçme.
> Yönerge Bölüm 7: *"bir modül çalışmadan diğerine geçmeyin."*

---

## 0 · Oturum Öncesi Hazırlık — ✅ TAMAMLANDI

| # | Madde | Durum |
|---|-------|-------|
| 1 | Python 3.9+ kurulu | ✅ 3.14.7 |
| 2 | Git çalışıyor | ✅ 2.50.1 |
| 3 | Klasör iskeleti hazır | ✅ |
| 4 | venv aktif, `pip install` hatasız | ✅ 5 paket |
| 5 | Duman testi tarayıcıda çalıştı | ✅ HTTP 200 |
| 6 | GitHub + Render + Wix + Groq hesapları | ✅ |
| 7 | Groq API anahtarı `.env` içinde | ✅ |

**Kalan iki madde:**
1. https://console.groq.com → API Keys → `gsk_...` anahtarını kopyala
2. `.env` dosyasında `GROQ_API_KEY=` satırına yapıştır

---

## Gün 1 · Modül A — `config.py`

**Hedef:** Tüm ayarlar tek merkezde, `.env`'den okunuyor.

- [ ] `load_dotenv()` dosyanın en başında
- [ ] `Config` sınıfı: `SECRET_KEY`, `DATABASE_URL`, `GROQ_API_KEY`, `AI_MODEL`, `CORS_ORIGINS`, `PORT`
- [ ] `BUSINESS_CONTEXT` → **kendi işine göre yaz** (projenin tek "konu"ya özel yeri)
- [ ] `DevelopmentConfig` / `ProductionConfig` + `config` sözlüğü

**Kontrol noktası:**
```bash
./venv/bin/python -c "from config import Config; print(Config.GROQ_API_KEY[:8], Config.DATABASE_URL)"
# gsk_xxxx smartlead.db  yazıyorsa tamam
```

---

## Gün 2 · Modül B — `app/database.py`

**Hedef:** SQL sadece bu dosyada. Kayıt ekle + listele çalışıyor.

- [ ] `get_db()` — `row_factory = sqlite3.Row`
- [ ] `init_db(app)` — `CREATE TABLE IF NOT EXISTS leads`
- [ ] `lead_ekle(isim, telefon, mesaj)` — **`?` yer tutucusu**, f-string YASAK
- [ ] `tum_leadler()` — `ORDER BY id DESC`, `dict()`'e çevir

**Kontrol noktası:** Modül F'de test edilecek. Şimdilik: dosyada `f"...SELECT"` veya
`f"...INSERT"` geçmediğini doğrula.
```bash
grep -n 'f"' app/database.py ; grep -n "f'" app/database.py   # çıktı boş olmalı
```

---

## Gün 3–4 · Modül C — `app/services/ai_service.py`

**Hedef:** Yapay zekâ çağrısı sadece bu dosyada.

- [ ] `AIServiceError` sınıfı
- [ ] `_sistem_talimati()` → config'den `BUSINESS_CONTEXT`
- [ ] `_groq_cagir(messages)` → `requests.post`, `timeout=30`, try-except
- [ ] `yanit_uret(mesaj, gecmis)` → mesaj sırası: **system → geçmiş → yeni soru**
- [ ] Anahtar yoksa "Demo modu" metni (çökme yok)
- [ ] Dosya sonunda `ai_service = AIService()`

**Kontrol noktası:** Bu dosyada `flask`, `sqlite3`, `request` geçmemeli.
```bash
grep -nE "sqlite3|from flask import request|render_template" app/services/ai_service.py  # boş olmalı
```

---

## Gün 5 · Modül D — `app/routes.py`

**Hedef:** 5 uç nokta tanımlı, içinde tek satır SQL/AI yok.

| Metod | Yol | Çağırdığı katman | Durum kodu |
|-------|-----|------------------|------------|
| GET | `/` | `render_template` | 200 |
| GET | `/dashboard` | `render_template` | 200 |
| POST | `/api/sohbet` | `ai_service.yanit_uret()` | 200 / 400 / 503 |
| POST | `/api/leads` | `database.lead_ekle()` | 201 / 400 |
| GET | `/api/leads` | `database.tum_leadler()` | 200 |

- [ ] İki blueprint: `api_bp`, `sayfa_bp`
- [ ] Her yanıtta `basari` alanı
- [ ] `AIServiceError` yakalanıp 503 + kibar mesaj

**Kontrol noktası:**
```bash
grep -nEi "SELECT|INSERT|requests\.post|sqlite3" app/routes.py   # çıktı boş olmalı
```

---

## Gün 6 · Modül E — `app/__init__.py` + `run.py`

**Hedef:** Her şey birleşiyor, sunucu hatasız açılıyor.

Sıra: ayarlar → CORS → `init_db()` → blueprint'ler (`url_prefix='/api'`) → `/health` → return

**Kontrol noktası:**
```bash
./venv/bin/python run.py     # hata vermeden açılmalı
```

---

## Gün 7 · Modül F — Uçtan Uca Test  ⭐ *Projenin dönüm noktası*

Bir terminalde sunucuyu başlat: `./venv/bin/python run.py`
Başka bir terminalde:

```bash
# 1) Canlılık
curl -s http://localhost:5001/health

# 2) Sohbet  (yapay zekâdan Türkçe yanıt gelmeli)
curl -s -X POST http://localhost:5001/api/sohbet \
  -H "Content-Type: application/json" \
  -d '{"mesaj":"Merhaba, neler yapabilirsin?","gecmis":[]}'

# 3) Lead kaydet  (201 dönmeli)
curl -s -X POST http://localhost:5001/api/leads \
  -H "Content-Type: application/json" \
  -d '{"isim":"Test Kullanici","telefon":"05551112233","mesaj":"deneme"}'

# 4) Listele  (eklediğin kayıt görünmeli)
curl -s http://localhost:5001/api/leads

# 5) Hata yönetimi  (400 dönmeli, çökmemeli)
curl -s -X POST http://localhost:5001/api/leads \
  -H "Content-Type: application/json" -d '{}'
```

Tarayıcıda `http://localhost:5001/` ve `/dashboard` — hazır test arayüzleri açılır.

**Kontrol noktası:** 5'i de geçtiyse **BACKEND TAMAMEN HAZIR.**

---

## Gün 8 · Modül G — Wix Arayüzü

Önce Wix Editor'de bileşenleri ekleyip **ID** ver, sonra `wix/*.js` kodunu
sayfanın Velo kod paneline yapıştır.

**Arayüz 1 — Karşılama (B2C), Z-Pattern + Glassmorphism**
`#girisKutusu` `#gonderButonu` `#cevapAlani` `#isimGirisi` `#telefonGirisi` `#kaydetButonu` `#formDurumu`

**Arayüz 2 — Yönetim Paneli (B2B), F-Pattern**
`#leadListesi` (Repeater) `#yenileButonu` `#sayac` — satır içi: `#isimText` `#telefonText` `#mesajText` `#tarihText`

⚠️ Repeater'a verilen her nesnede `_id` **zorunlu** ve **string** olmalı.
⚠️ Alan adları backend ile birebir aynı: `mesaj`/`gecmis` → `cevap`, `isim`/`telefon`.

---

## Gün 9 · Modül H — Yayınlama

```bash
git init && git add . && git commit -m "SmartLead AI"
git remote add origin https://github.com/KULLANICI/smartlead-ai.git
git push -u origin main
```

Render → New → Web Service → repoyu bağla:
- **Build:** `pip install -r requirements.txt`
- **Start:** `gunicorn run:app`
- **Environment:** `GROQ_API_KEY`, `SECRET_KEY`, `FLASK_ENV=production`, `CORS_ORIGINS=https://siteniz.wixsite.com`

Sonra `wix/*.js` içindeki `const API = '...'` satırını Render adresinle güncelle.

### ⚠️ Render ücretsiz plan — demoyu bozabilecek iki gerçek

1. **Dosya sistemi kalıcı değil.** Her deploy / restart / uyku sonrası
   `smartlead.db` **sıfırlanır**; kalıcı disk sadece ücretli planda var.
   → Demo kayıtlarını sunum anında canlı ekle, **ya da** Render'ın ücretsiz
   PostgreSQL'ine geç (`database.py` dışında hiçbir dosya değişmez —
   mimarinin karşılığını tam burada alırsın).
2. **15 dakika hareketsiz kalınca servis uykuya geçer**, uyanması ~1 dakika sürer.
   → Sunumdan birkaç dakika önce `/health` adresine gir ve ısıt.

⚠️ **KRİTİK:** GitHub'da `.env` görünüyorsa anahtarı hemen yenile.
```bash
git ls-files | grep -c "^\.env$"   # 0 olmalı
```

**Kontrol noktası:** `https://....onrender.com/health` → `{"durum":"aktif"}` **ve**
Wix sayfası bu adrese bağlanıp çalışıyorsa **PROJE TAMAMLANDI.**

---

## Gün 10 · Teslim

- [ ] GitHub deposu bağlantısı (`.env` hariç)
- [ ] Canlı Render adresi
- [ ] Wix site bağlantısı (iki arayüz)
- [ ] README (bu depoda hazır)
- [ ] Kısa sunum/demo

### Değerlendirme ağırlıkları
| Kriter | Ağırlık | Nerede kazanılır |
|--------|---------|------------------|
| Mimari (SoC) | %30 | SQL sadece `database.py`, AI sadece `ai_service.py` |
| Çalışırlık | %25 | Modül F'nin 5 testi + Wix bağlantısı |
| Kod kalitesi | %15 | Anlamlı isimler, yorumlar |
| Güvenlik | %10 | `?` yer tutucusu, `.env` gizli, CORS |
| Hata yönetimi | %10 | try-except + kibar JSON |
| Yayın + sunum | %10 | Canlıda çalışıyor, kodu açıklayabiliyorsun |
