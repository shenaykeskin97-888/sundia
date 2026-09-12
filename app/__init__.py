"""
MODÜL E — Uygulama fabrikası
============================
Ayarları, CORS'u, veritabanını ve rotaları bir araya getiren fabrika.

Neden fabrika deseni? Uygulamayı global bir değişken olarak değil, bir
fonksiyonun döndürdüğü nesne olarak kurarız. Böylece testlerde farklı
ayarlarla ikinci bir uygulama örneği oluşturabiliriz.
"""

import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import config


def create_app(ortam=None):
    """Uygulamayı kurar ve döndürür. SIRA ÖNEMLİ."""
    app = Flask(__name__)

    # 1) Ayarları yükle — hangi ortamdayız?
    ortam = ortam or os.environ.get('FLASK_ENV', 'default')
    ayarlar = config.get(ortam, config['default'])
    app.config.from_object(ayarlar)

    # 2) CORS'u aç.
    # Wix farklı bir origin'den (wixsite.com) istek attığı için ŞART.
    # Sadece /api/* yollarını açıyoruz; HTML sayfaları zaten aynı origin.
    CORS(app, resources={r'/api/*': {'origins': ayarlar.cors_listesi()}})

    # 3) Veritabanını hazırla ve bağlantı kapatmayı kaydet.
    from app.database import init_db, kapat_db
    app.teardown_appcontext(kapat_db)   # her istek bitince bağlantıyı kapat
    init_db(app)                        # 'leads' tablosu yoksa oluştur

    # 4) Rotaları kaydet.
    # Import'u burada yapıyoruz: routes.py `from app import database` diyor,
    # yukarıda import etseydik döngüsel import hatası alırdık.
    from app.routes import api_bp, sayfa_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(sayfa_bp)

    # 5) Canlılık kontrolü — Render ve izleme araçları buraya bakar.
    @app.route('/health')
    def health():
        from app.database import get_db
        try:
            get_db().execute('SELECT 1')
            veritabani = 'baglandi'
        except Exception:
            veritabani = 'hata'
        return jsonify({'durum': 'aktif', 'veritabani': veritabani})

    return app
