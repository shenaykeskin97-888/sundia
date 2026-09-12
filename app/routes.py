"""
MODÜL D — Rotalar (kontrolcü katmanı)
=====================================
Gelen HTTP isteklerini karşılar, DOĞRULAR ve doğru katmana yönlendirir.

>>> MİMARİ SÖZLEŞME: BURADA SQL VE YAPAY ZEKÂ KODU YOK. <<<
Bu dosyanın tek işi: isteği al -> kontrol et -> database.py veya
ai_service.py çağır -> sonucu JSON'a çevir. Başka hiçbir iş yapmaz.

KRİTİK — alan adları frontend ile BİREBİR aynı olmalı:
    sohbet : gelen {mesaj, gecmis}                        -> dönen {basari, cevap}
    lead   : gelen {isim, telefon, katilimciTipi, mesaj}    -> dönen {basari, id}
Bir harf farkı bağlantıyı koparır.
"""

from flask import Blueprint, jsonify, render_template, request

from app import database
from app.services.ai_service import AIServiceError, ai_service

# İki ayrı blueprint: biri JSON API için, biri HTML sayfalar için.
# create_app() api_bp'yi '/api' önekiyle kaydeder.
api_bp = Blueprint('api', __name__)
sayfa_bp = Blueprint('sayfa', __name__)

MAX_MESAJ_UZUNLUGU = 1000   # token maliyeti ve kötüye kullanıma karşı
MAX_ISIM_UZUNLUGU = 100
MAX_TELEFON_UZUNLUGU = 30

# Bu projeye özel: SUNDIA SPACE çocuk, ergen, yetişkin gruplarına ve
# kurumlara (şirket, okul, anaokulu) program sunuyor.
# Beyaz liste kullanıyoruz — frontend'den gelen serbest metni olduğu gibi kaydetmiyoruz.
GECERLI_KATILIMCI_TIPLERI = ('cocuk', 'ergen', 'yetiskin', 'kurum')


def _hata(mesaj, kod):
    """Tek tip hata yanıtı üretir — her uç nokta aynı biçimi döndürsün."""
    return jsonify({'basari': False, 'hata': mesaj}), kod


# ============================ SAYFALAR ============================

@sayfa_bp.route('/')
def karsilama():
    """Karşılama sayfası (yerel test arayüzü)."""
    return render_template('index.html')


@sayfa_bp.route('/dashboard')
def dashboard():
    """Yönetim paneli (yerel test arayüzü)."""
    return render_template('dashboard.html')


# ============================== API ===============================

@api_bp.route('/sohbet', methods=['POST'])
def sohbet():
    """Ziyaretçinin mesajını yapay zekâya iletir."""
    veri = request.get_json(silent=True) or {}
    mesaj = (veri.get('mesaj') or '').strip()
    gecmis = veri.get('gecmis') or []

    # --- Doğrulama ---
    if not mesaj:
        return _hata('Mesaj boş olamaz.', 400)
    if len(mesaj) > MAX_MESAJ_UZUNLUGU:
        return _hata(f'Mesaj en fazla {MAX_MESAJ_UZUNLUGU} karakter olabilir.', 400)
    if not isinstance(gecmis, list):
        return _hata('Geçmiş bir liste olmalı.', 400)

    # --- Yapay zekâ katmanına devret ---
    # Dış servis çağrısı her zaman try-except ile sarılır.
    try:
        cevap = ai_service.yanit_uret(mesaj, gecmis)
    except AIServiceError as hata:
        # 503 = "servis şu an kullanılamıyor" — sorun bizim kodumuzda değil.
        return _hata(str(hata), 503)

    return jsonify({'basari': True, 'cevap': cevap})


@api_bp.route('/leads', methods=['POST'])
def lead_kaydet():
    """Yeni müşteri adayını kaydeder."""
    veri = request.get_json(silent=True) or {}
    isim = (veri.get('isim') or '').strip()
    telefon = (veri.get('telefon') or '').strip()
    mesaj = (veri.get('mesaj') or '').strip() or None
    katilimci_tipi = (veri.get('katilimciTipi') or '').strip().lower() or None

    # --- Doğrulama ---
    if not isim or not telefon:
        return _hata('İsim ve telefon zorunludur.', 400)
    if len(isim) > MAX_ISIM_UZUNLUGU:
        return _hata(f'İsim en fazla {MAX_ISIM_UZUNLUGU} karakter olabilir.', 400)
    if len(telefon) > MAX_TELEFON_UZUNLUGU:
        return _hata(f'Telefon en fazla {MAX_TELEFON_UZUNLUGU} karakter olabilir.', 400)
    if katilimci_tipi is not None and katilimci_tipi not in GECERLI_KATILIMCI_TIPLERI:
        return _hata('Katılımcı tipi çocuk, ergen, yetişkin veya kurum olmalıdır.', 400)

    # --- Veri katmanına devret ---
    yeni_id = database.lead_ekle(isim, telefon, mesaj, katilimci_tipi)

    # 201 = "yeni kaynak oluşturuldu"
    return jsonify({'basari': True, 'id': yeni_id}), 201


@api_bp.route('/leads', methods=['GET'])
def leadleri_getir():
    """Tüm müşteri adaylarını döndürür."""
    leadler = database.tum_leadler()
    return jsonify({'basari': True, 'leadler': leadler})
