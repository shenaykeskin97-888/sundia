# Wix Velo — ID'ler ve Olaylar (Modül G referansı)

Wix editörü açıkken bunu yanında tut.

---

## 1 · Önce Dev Mode'u aç

| Editör | Nasıl |
|--------|-------|
| **Wix Editor** | Üst menü → `</>` **Dev Mode** → *Turn on Dev Mode* |
| **Wix Studio** | Sol kenar → `</>` Code → **Start Coding** |

Açmadan ne kod paneli ne de Properties & Events paneli görünür.

---

## 2 · ID'yi Wix'ten "almıyorsun" — sen veriyorsun

Her elemanın hazır bir varsayılan ID'si vardır (`button1`, `input1`, `text3`…).
Sen bunu anlamlı bir isimle değiştirirsin.

1. Elemanı sayfada **seç**
2. **Properties & Events** panelini aç — kod panelinin sağında durur,
   araç çubuğundaki *Properties & Events* düğmesiyle açılıp kapanır
3. En üstteki **ID** alanına yeni adı yaz → `gonderButonu`

**Kurallar**
- ID sayfa içinde **benzersiz** olmalı
- Kodda `#` ile çağrılır: panelde `gonderButonu` → kodda `$w('#gonderButonu')`
- ⚠️ ID'yi sonradan değiştirirsen **kodu elle güncellemen gerekir**; Wix
  senin için düzeltmez, `$w('#eskiAd')` sessizce `undefined` döner

---

## 3 · Bu projede kurulacak elemanlar

### Karşılama sayfası

| Bileşen | Vereceğin ID | Kodda ne yapar |
|---------|--------------|----------------|
| Input | `girisKutusu` | `.value` ile soruyu okur |
| Button | `gonderButonu` | `.onClick()` ile tetikler |
| Text | `cevapAlani` | `.text` ile yanıtı yazar |
| Input | `isimGirisi` | `.value` |
| Input | `telefonGirisi` | `.value` |
| **Dropdown** | `katilimciTipi` | `.options` koddan dolar (çocuk/ergen/yetişkin/kurum) |
| Button | `kaydetButonu` | `.onClick()` |
| Text | `formDurumu` | `.text` ile durum mesajı |

### Yönetim paneli

| Bileşen | Vereceğin ID |
|---------|--------------|
| Repeater | `leadListesi` |
| Button | `yenileButonu` |
| Text | `sayac` |
| Text *(repeater içinde)* | `isimText` `telefonText` `tipText` `mesajText` `tarihText` |

---

## 4 · Tıklamayı yakalamanın iki yolu

### Yol A — Panelden (kodu Wix üretir)

Elemanı seç → Properties & Events → **Event Handlers** → `onClick()` tıkla.
Sayfa koduna şu blok düşer:

```js
$w('#gonderButonu').onClick((event) => {
    // kodunu buraya yaz
});
```

> Panel bu bloğu `$w.onReady()`'nin **dışına** koyar. İstersen içine taşıyabilirsin.

### Yol B — Elle (bu projede kullanacağımız)

```js
$w.onReady(function () {
    $w('#gonderButonu').onClick(soruyuGonder);
});
```

⚠️ Elle yazarken **`$w.onReady()` içinde olmalı.** Dışarıda yazarsan elemanlar
henüz yüklenmemiş olabilir ve hata alırsın.

⚠️ Aynı olay için **ikisini birden yapma** — handler iki kez bağlanır,
tek tıklamada iki istek gider.

---

## 5 · "Hangi elemana tıklandı?" — `event.target.id`

Her handler'a bir `event` nesnesi gelir:

```js
$w('#gonderButonu').onClick((event) => {
    console.log(event.target.id);   // "gonderButonu"
    console.log(event.type);        // "click"
});
```

Tek fonksiyonla birden fazla butonu yönetmek istersen:

```js
function butonaTiklandi(event) {
    if (event.target.id === 'gonderButonu')  soruyuGonder();
    if (event.target.id === 'kaydetButonu')  leadKaydet();
}

$w.onReady(function () {
    $w('#gonderButonu').onClick(butonaTiklandi);
    $w('#kaydetButonu').onClick(butonaTiklandi);
});
```

### Enter tuşu

```js
$w('#girisKutusu').onKeyPress((event) => {
    if (event.key === 'Enter') soruyuGonder();
});
```

---

## 6 · Repeater içindeki tıklama — `event.context.itemId`

Repeater'da aynı buton 20 satırda 20 kez vardır; hepsi **aynı ID'yi** taşır.
Hangi satır olduğunu `event.context.itemId` söyler.

```js
$w('#leadListesi').onItemReady(($item, itemData) => {
    $item('#isimText').text    = itemData.isim;
    $item('#telefonText').text = itemData.telefon;

    // Satır içindeki bir butona tıklanırsa:
    $item('#araButonu').onClick((event) => {
        console.log(event.context.itemId);   // o satırın _id'si
        console.log(itemData.telefon);       // closure'dan direkt erişim
    });
});
```

- `onItemReady` **içinde**: `$item(...)` zaten o satıra kilitli, `itemData` elinde
- `onItemReady` **dışında** bir handler yazdıysan: `$w.at(event.context)` ile
  o satıra kilitli bir seçici alırsın

⚠️ Repeater'a verdiğin her nesnede `_id` **zorunlu** ve **string** olmalı.

---

## 7 · Hızlı hata ayıklama

| Belirti | Sebep |
|---------|-------|
| `$w(...) is not a function` / null | ID yanlış yazılmış ya da `$w.onReady()` dışında çağrılmış |
| Tıklama hiç çalışmıyor | Dev Mode kapalı, ya da handler `onReady` dışında |
| Tek tıkta iki istek | Hem panelden hem elle handler bağlanmış |
| Repeater boş | `_id` eksik veya sayı olarak verilmiş (string olmalı) |
| Kod önizlemede çalışıp canlıda çalışmıyor | Site **Publish** edilmemiş |

`console.log` çıktıları tarayıcının geliştirici konsolunda görünür (F12).

---

## 8 · "Elemanları koddan oluşturabilir miyim?"

**Native Wix elemanları için: hayır.** `$w()` bir **seçicidir**, oluşturucu değil.
`document.createElement` karşılığı yoktur. Editörde var olmayan bir ID'yi
seçemezsin — `$w('#olmayanButon')` sessizce boşa düşer.

### Ama liste/tekrar eden içerik %100 koddan gelir — Repeater

Şablonu **bir kez** editörde kurarsın; kaç satır olacağını ve içeriğini kod belirler.

```js
// Editörde: Repeater içine 1 satırlık şablon koydun (4 Text).
// Kod 20 kayıt verirse 20 satır oluşur — elle 20 kutu sürüklemezsin.

$w('#leadListesi').onItemReady(($item, itemData) => {
    $item('#isimText').text    = itemData.isim;
    $item('#telefonText').text = itemData.telefon;
    $item('#mesajText').text   = itemData.mesaj;
    $item('#tarihText').text   = itemData.tarih;
});

$w('#leadListesi').data = satirlar;   // <- eleman sayısını bu satır belirler
```

### Tam HTML/CSS/JS yazmak istersen — iki kaçış yolu

| Yöntem | Ne verir | Bedeli |
|--------|----------|--------|
| **HTML Component** (iframe embed) | İçine tam HTML/CSS/JS yapıştırırsın; gerçek DOM, `document.createElement` serbest | Sandbox'lı iframe — sayfadaki elemanlara erişemez, iletişim `postMessage()`/`onMessage()` ile; SEO zayıf |
| **Custom Element** (web component) | Aynısı, iframe sandbox'ı olmadan; veri `setAttribute` ile geçer | ⚠️ **Canlı sitede Premium plan + özel domain + reklamsız** şart |

> HTML Component ücretsiz planda çalışır (sadece PDF gömmek Premium ister).
> Custom Element canlıda ücretli — öğrenci projesi için elenir.

### Bu proje için karar

Yönerge Modül G **açıkça Repeater istiyor** (`_id` zorunlu, satır içinde `$item`).
iframe'e kaçarsan o beceriyi göstermemiş olursun.

Toplam sürükle-bırak yükün **16 bileşen, tek seferlik, ~15 dakika**:
karşılama 8 + panel 3 + repeater şablonu içinde 5 Text. Sonrası tamamen kod.
