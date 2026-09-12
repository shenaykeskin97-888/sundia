"""
MODÜL B — Veri katmanı
======================
SQLite ile çalışan, müşteri adaylarını (lead) kaydeden ve listeleyen katman.

>>> MİMARİ SÖZLEŞME: SQL YALNIZCA BU DOSYADA. <<<
routes.py içinde tek bir SELECT/INSERT bile görünmemeli.
Bu ayrım sayesinde yarın SQLite'tan PostgreSQL'e geçmek istersek
sadece bu dosyayı değiştiririz, projenin geri kalanı hiç bilmez.
"""

import sqlite3

from flask import current_app, g


def get_db():
    """İstek boyunca tek bir SQLite bağlantısı döndürür.

    Flask'ın `g` nesnesi her HTTP isteği için ayrı ayrı oluşur.
    Bağlantıyı orada saklayarak aynı istek içinde tekrar tekrar
    bağlantı açmayı önleriz.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE_URL'])
        # row_factory sayesinde satırlara indeksle (satir[0]) değil
        # sütun adıyla (satir['isim']) erişebiliriz — kod çok daha okunaklı.
        g.db.row_factory = sqlite3.Row
    return g.db


def kapat_db(hata=None):
    """İstek bitince bağlantıyı kapatır.

    create_app() bunu teardown_appcontext'e bağlar. Kapatmazsak
    her istekte bir bağlantı açık kalır ve zamanla kaynak sızar.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """'leads' tablosunu yoksa oluşturur.

    create_app() içinden, uygulama bağlamı (app context) açıkken çağrılır.
    IF NOT EXISTS sayesinde her açılışta güvenle çalıştırılabilir.
    """
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                isim         TEXT NOT NULL,
                telefon      TEXT NOT NULL,
                katilimci_tipi TEXT,        -- cocuk | ergen | yetiskin | kurum
                mesaj        TEXT,
                tarih        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
        kapat_db()


def lead_ekle(isim, telefon, mesaj=None, katilimci_tipi=None):
    """Yeni müşteri adayını kaydeder, eklenen kaydın id'sini döndürür.

    katilimci_tipi: bu projeye özel sütun — 'cocuk', 'ergen', 'yetiskin'
    veya 'kurum'. SUNDIA doğru program grubuna yönlendirebilsin diye tutuyoruz.

    GÜVENLİK: Değerler SQL metnine ASLA doğrudan eklenmez.
        YANLIŞ:  f"INSERT INTO leads (isim) VALUES ('{isim}')"
        DOĞRU :  "INSERT INTO leads (isim) VALUES (?)", (isim,)
    Kullanıcı isim alanına  '); DROP TABLE leads; --  yazarsa,
    ? yer tutucusu bunu SQL komutu değil düz metin olarak ele alır.
    Bu, SQL Injection'a karşı zorunlu korumadır.
    """
    db = get_db()
    imlec = db.execute(
        "INSERT INTO leads (isim, telefon, katilimci_tipi, mesaj) VALUES (?, ?, ?, ?)",
        (isim, telefon, katilimci_tipi, mesaj),
    )
    db.commit()
    return imlec.lastrowid


def tum_leadler():
    """Tüm kayıtları en yeniden eskiye, sözlük listesi olarak döndürür.

    sqlite3.Row nesnesi JSON'a çevrilemez; dict()'e dönüştürmek
    zorundayız ki routes.py jsonify() ile döndürebilsin.
    """
    db = get_db()
    satirlar = db.execute(
        "SELECT id, isim, telefon, katilimci_tipi, mesaj, tarih "
        "FROM leads ORDER BY id DESC"
    ).fetchall()
    return [dict(satir) for satir in satirlar]
