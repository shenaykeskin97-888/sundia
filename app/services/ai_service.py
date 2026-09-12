"""
MODÜL C — Yapay zekâ servisi
============================
Kullanıcı mesajını alıp Groq'a gönderen, yanıtı döndüren servis katmanı.

>>> MİMARİ SÖZLEŞME: YAPAY ZEKÂ ÇAĞRISI YALNIZCA BU DOSYADA. <<<

Dikkat: bu dosyada `flask` importu YOK. Bu katman HTTP'yi, Flask'ı,
veritabanını bilmez — sadece yapay zekâ ile konuşur. Bu izolasyon sayesinde
Groq'tan Gemini'ye geçmek istersek tek bir metodu değiştirmek yeterli olur,
routes.py'nin haberi bile olmaz.
"""

import requests

from config import Config

# Groq, OpenAI ile uyumlu bir arayüz sunar; adres bu yüzden /openai/v1 içerir.
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

ZAMAN_ASIMI = 30   # saniye — servis takılırsa istek sonsuza kadar beklemesin
GECMIS_LIMITI = 10  # son kaç mesaj gönderilsin (token maliyetini sınırlar)
YARATICILIK = 0.7  # 0 = hep aynı yanıt, 1 = çok değişken
MAX_TOKEN = 400    # yanıt uzunluk tavanı — maliyeti ve gevezeliği sınırlar


class AIServiceError(Exception):
    """Yapay zekâ katmanında oluşan hatalar.

    Kendi hata sınıfımızı tanımlıyoruz ki routes.py sadece bunu yakalasın
    ve "AI tarafında bir sorun var" ile "kodda bug var" ayırt edilebilsin.
    """
    pass


class AIService:
    """Groq ile konuşan servis. Dışarıya tek metot açar: yanit_uret()."""

    def _sistem_talimati(self):
        """Yapay zekânın 'kim olduğunu' anlatan metni config'den okur."""
        return Config.BUSINESS_CONTEXT

    def _anahtar_var_mi(self):
        """Gerçek bir Groq anahtarı tanımlı mı?"""
        anahtar = Config.GROQ_API_KEY.strip()
        return bool(anahtar) and anahtar.startswith('gsk_') and 'BURAYA' not in anahtar

    def _groq_cagir(self, messages):
        """Groq API'sine POST atar, modelin ürettiği metni döndürür.

        Dış servis çağrısı her zaman try-except ile sarılır: ağ kopabilir,
        servis yavaşlayabilir, kota dolabilir. Hiçbirinde uygulama çökmemeli.
        """
        basliklar = {
            'Authorization': f'Bearer {Config.GROQ_API_KEY}',
            'Content-Type': 'application/json',
        }
        govde = {
            'model': Config.AI_MODEL,
            'messages': messages,
            'temperature': YARATICILIK,
            'max_tokens': MAX_TOKEN,
        }

        try:
            yanit = requests.post(
                GROQ_URL, json=govde, headers=basliklar, timeout=ZAMAN_ASIMI
            )
            yanit.raise_for_status()
        except requests.exceptions.Timeout:
            raise AIServiceError('Yapay zekâ servisi zamanında yanıt vermedi.')
        except requests.exceptions.HTTPError:
            # Groq'un kendi hata mesajını alalım; anahtar yanlışsa burada belli olur.
            detay = ''
            try:
                detay = yanit.json().get('error', {}).get('message', '')
            except ValueError:
                detay = yanit.text[:200]
            raise AIServiceError(f'Yapay zekâ servisi hata döndürdü: {detay}')
        except requests.exceptions.RequestException as hata:
            raise AIServiceError(f'Yapay zekâ servisine ulaşılamadı: {hata}')

        # Yanıtın beklediğimiz yapıda geldiğini varsaymayalım.
        try:
            return yanit.json()['choices'][0]['message']['content'].strip()
        except (KeyError, IndexError, ValueError):
            raise AIServiceError('Yapay zekâdan beklenmeyen biçimde yanıt geldi.')

    def yanit_uret(self, mesaj, gecmis=None):
        """Dışarıya açılan tek metot: mesaj + geçmiş -> yapay zekâ yanıtı.

        messages dizisinin SIRASI önemlidir:
            1. sistem talimatı  (yapay zekânın kimliği)
            2. geçmiş mesajlar  (konuşmanın akışı)
            3. yeni kullanıcı mesajı
        """
        if not self._anahtar_var_mi():
            # Anahtar yoksa çökme; arayüz anahtarsız da test edilebilsin.
            return (f'Demo modu: "{mesaj}" sorunuzu aldım. '
                    'Gerçek yanıtlar için .env dosyasına GROQ_API_KEY ekleyin.')

        messages = [{'role': 'system', 'content': self._sistem_talimati()}]

        # Geçmişi son N mesajla sınırla — uzun sohbette maliyet ve gecikme büyür.
        for onceki in (gecmis or [])[-GECMIS_LIMITI:]:
            rol = onceki.get('role')
            icerik = onceki.get('content')
            # Sadece beklediğimiz rolleri geçir; bozuk veri modele gitmesin.
            if rol in ('user', 'assistant') and icerik:
                messages.append({'role': rol, 'content': icerik})

        messages.append({'role': 'user', 'content': mesaj})

        return self._groq_cagir(messages)


# Tüm uygulama bu tek örneği paylaşır (her istekte yeni nesne kurmaya gerek yok).
ai_service = AIService()
