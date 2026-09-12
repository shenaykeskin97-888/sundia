/* ============================================================
   MODÜL G — ARAYÜZ 1: Karşılama Sayfası (B2C)
   Wix Editor > sayfayı aç > Kod paneli (Velo) içine yapıştır.
   Bu dosya depoda referans/yedek olarak durur; çalışan kopya Wix'tedir.

   ÖNCE EDİTÖRDE BU BİLEŞENLERİ EKLE VE ID VER
   (Properties & Events paneli > ID alanı):
     #girisKutusu      Input     — ziyaretçinin sorusu
     #gonderButonu     Button    — "Sor"
     #cevapAlani       Text      — yapay zekânın yanıtı
     #isimGirisi       Input     — ad
     #telefonGirisi    Input     — telefon
     #danisanTipi      Dropdown  — çocuk / ergen / yetişkin
     #kaydetButonu     Button    — "Beni arayın"
     #formDurumu       Text      — durum / hata mesajı

   UX: Z-Pattern (logo sol üst, sohbet sağ, form altta),
       sohbet kartına Glassmorphism (buzlu cam) efekti.
   ============================================================ */

import { fetch } from 'wix-fetch';

// Render adresin. SONUNDA / OLMASIN.
const API = 'https://smartlead-ai-sbly.onrender.com';

// Konuşma geçmişi: [{ role: 'user' | 'assistant', content: '...' }]
// Sayfada tutulur; sayfa yenilenince sıfırlanır.
let gecmis = [];

$w.onReady(function () {
    // Olay bağlantıları onReady içinde kurulur —
    // dışarıda kurulursa elemanlar henüz yüklenmemiş olabilir.
    $w('#gonderButonu').onClick(soruyuGonder);

    $w('#girisKutusu').onKeyPress((event) => {
        if (event.key === 'Enter') {
            soruyuGonder();
        }
    });

    $w('#kaydetButonu').onClick(leadKaydet);

    // Dropdown seçeneklerini koddan dolduruyoruz: değerler backend'in
    // beklediği beyaz listeyle (cocuk/ergen/yetiskin) birebir aynı olmalı.
    $w('#danisanTipi').options = [
        { label: 'Çocuk', value: 'cocuk' },
        { label: 'Ergen', value: 'ergen' },
        { label: 'Yetişkin', value: 'yetiskin' }
    ];
    $w('#danisanTipi').placeholder = 'Görüşme kimin için?';

    $w('#cevapAlani').text = 'Merhaba! Size nasıl yardımcı olabilirim?';
    $w('#formDurumu').text = '';
});

/* ---------------------- SOHBET ---------------------- */

async function soruyuGonder() {
    const soru = $w('#girisKutusu').value.trim();

    if (soru === '') {
        $w('#cevapAlani').text = 'Lütfen bir soru yazın.';
        return;
    }

    // Bekleme durumu: kullanıcı bir şey olduğunu görsün,
    // buton kapalı olsun ki iki kez göndermesin.
    $w('#cevapAlani').text = 'Düşünüyorum...';
    $w('#girisKutusu').value = '';
    $w('#gonderButonu').disable();

    try {
        const yanit = await fetch(API + '/api/sohbet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // Alan adları backend'deki routes.py ile BİREBİR aynı olmalı.
            body: JSON.stringify({ mesaj: soru, gecmis: gecmis })
        });

        const veri = await yanit.json();

        if (veri.basari) {
            $w('#cevapAlani').text = veri.cevap;
            // Geçmişi güncelle ki yapay zekâ önceki konuşmayı hatırlasın.
            gecmis.push({ role: 'user', content: soru });
            gecmis.push({ role: 'assistant', content: veri.cevap });
        } else {
            $w('#cevapAlani').text = veri.hata || 'Bir sorun oluştu.';
        }
    } catch (error) {
        // Ağ koptu, sunucu uyanıyor veya CORS engelledi.
        $w('#cevapAlani').text = 'Bağlantı hatası oluştu. Lütfen tekrar deneyin.';
    } finally {
        // Hata olsa da olmasa da butonu geri aç.
        $w('#gonderButonu').enable();
    }
}

/* ------------------- LEAD KAYDETME ------------------- */

async function leadKaydet() {
    const isim = $w('#isimGirisi').value.trim();
    const telefon = $w('#telefonGirisi').value.trim();
    const danisanTipi = $w('#danisanTipi').value;   // '' olabilir — opsiyonel

    if (isim === '' || telefon === '') {
        $w('#formDurumu').text = 'Lütfen isim ve telefon girin.';
        return;
    }

    $w('#formDurumu').text = 'Kaydediliyor...';
    $w('#kaydetButonu').disable();

    try {
        const yanit = await fetch(API + '/api/leads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                isim: isim,
                telefon: telefon,
                danisanTipi: danisanTipi,
                mesaj: ''
            })
        });

        const veri = await yanit.json();

        if (veri.basari) {
            $w('#formDurumu').text = 'Aldık, en kısa sürede sizi arayacağız.';
            $w('#isimGirisi').value = '';
            $w('#telefonGirisi').value = '';
            $w('#danisanTipi').value = '';
        } else {
            $w('#formDurumu').text = veri.hata || 'Kayıt yapılamadı.';
        }
    } catch (error) {
        $w('#formDurumu').text = 'Bağlantı hatası oluştu.';
    } finally {
        $w('#kaydetButonu').enable();
    }
}
