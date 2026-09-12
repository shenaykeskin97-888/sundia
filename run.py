"""
MODÜL E — Giriş noktası
=======================
Bu dosyanın TEK işi fabrikadan uygulamayı alıp çalıştırmaktır.
İçinde başka hiçbir mantık olmaz.

Yerelde:   python run.py       -> http://localhost:5001
Render'da: gunicorn run:app    -> aşağıdaki 'app' değişkenini kullanır
"""

import os

from app import create_app

# gunicorn bu değişkeni arar, o yüzden modül seviyesinde tanımlı olmalı.
app = create_app()

if __name__ == '__main__':
    # macOS'ta 5000 portunu AirPlay Receiver kullanıyor -> varsayılan 5001.
    # Render PORT değişkenini kendisi atadığı için ortamdan okuyoruz.
    app.run(
        debug=app.config['DEBUG'],
        port=int(os.environ.get('PORT', 5001)),
    )
