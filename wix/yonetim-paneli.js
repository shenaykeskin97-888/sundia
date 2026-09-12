/* ============================================================
   MODÜL G — ARAYÜZ 2: Yönetim Paneli (B2B)
   Wix Editor > sayfayı aç > Kod paneli (Velo) içine yapıştır.

   ÖNCE EDİTÖRDE BU BİLEŞENLERİ EKLE VE ID VER:
     #leadListesi    Repeater   — her satır bir müşteri adayı
     #yenileButonu   Button     — listeyi tazele
     #sayac          Text       — "12 kayıt"

   REPEATER SATIR ŞABLONUNUN İÇİNE (4 adet Text):
     #isimText   #telefonText   #tipText   #mesajText   #tarihText

   UX: F-Pattern — en önemli kolon (isim) en solda.
   ============================================================ */

import { fetch } from 'wix-fetch';

// Veritabanındaki kısa değerleri ekranda okunur etikete çevirir.
const ETIKET = { cocuk: 'Çocuk', ergen: 'Ergen', yetiskin: 'Yetişkin' };

// Karşılama sayfasıyla AYNI adres olmalı.
const API = 'https://smartlead-ai-sbly.onrender.com';

$w.onReady(function () {
    $w('#yenileButonu').onClick(leadleriYukle);

    // Satır şablonunu doldurma kuralı. Repeater'a veri verilmeden
    // ÖNCE tanımlanmalı — her satır oluşurken bu fonksiyon çalışır.
    $w('#leadListesi').onItemReady(($item, itemData) => {
        // $item, o satıra kilitlenmiş bir seçicidir.
        // $w('#isimText') deseydik hep ilk satırı hedeflerdik.
        $item('#isimText').text = itemData.isim;
        $item('#telefonText').text = itemData.telefon;
        $item('#tipText').text = itemData.tip;
        $item('#mesajText').text = itemData.mesaj;
        $item('#tarihText').text = itemData.tarih;
    });

    leadleriYukle();
});

async function leadleriYukle() {
    $w('#sayac').text = 'Yükleniyor...';

    try {
        const yanit = await fetch(API + '/api/leads');
        const veri = await yanit.json();

        if (!veri.basari) {
            $w('#sayac').text = 'Kayıtlar alınamadı.';
            return;
        }

        // Backend'in döndürdüğü kayıtları Repeater'ın beklediği biçime çevir.
        // _id ZORUNLU ve STRING olmalı — sayı verirsen Repeater boş kalır.
        const satirlar = veri.leadler.map((lead) => ({
            _id: String(lead.id),
            isim: lead.isim,
            telefon: lead.telefon,
            tip: ETIKET[lead.danisan_tipi] || '-',
            mesaj: lead.mesaj || '-',
            tarih: lead.tarih
        }));

        $w('#leadListesi').data = satirlar;
        $w('#sayac').text = satirlar.length + ' talep';
    } catch (error) {
        $w('#sayac').text = 'Bağlantı hatası oluştu.';
    }
}
