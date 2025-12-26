import os
import time
import random
import threading
import requests
from flask import Flask
from datetime import datetime
import pytz

# ===============================
# CONFIGURACIÓN (VARIABLES RENDER)
# ===============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ===============================
# ZONA HORARIA COLOMBIA
# ===============================
ZONA_CO = pytz.timezone("America/Bogota")

# ===============================
# FLASK (PULSO 24/7)
# ===============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ===============================
# TELEGRAM HELPERS
# ===============================
def enviar_mensaje(texto, botones=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    if botones:
        payload["reply_markup"] = botones
    requests.post(url, json=payload)

def teclado_vip():
    return {
        "inline_keyboard": [
            [{"text": "🔥 Pedir análisis VIP", "callback_data": "VIP"}]
        ]
    }

# ===============================
# GENERADOR ANÁLISIS VIP
# ===============================
def generar_analisis_vip():
    ahora = datetime.now(ZONA_CO).strftime("%d/%m/%Y %I:%M %p")

    opciones = [
        {
            "mercado": "Más de 2.5 goles",
            "prob": "72%",
            "fundamento": "Alta frecuencia ofensiva, promedio superior a 1.6 goles por partido y defensas con errores recurrentes."
        },
        {
            "mercado": "Menos de 2.5 goles",
            "prob": "68%",
            "fundamento": "Ritmo conservador, partidos cerrados y tendencia histórica de marcadores ajustados."
        },
        {
            "mercado": "Gol en primer tiempo",
            "prob": "75%",
            "fundamento": "Presión temprana constante y registros repetidos de anotación antes del minuto 30."
        }
    ]

    elegido = max(opciones, key=lambda x: int(x["prob"].replace("%","")))

    mensaje = f"""
🔥 <b>ANÁLISIS VIP DE FÚTBOL</b>

🕒 <b>Hora (Colombia):</b> {ahora}

⚽ <b>Pronóstico seleccionado:</b>
👉 <b>{elegido['mercado']}</b>

📊 <b>Probabilidad estimada:</b> {elegido['prob']}

📌 <b>Fundamentación:</b>
{elegido['fundamento']}

━━━━━━━━━━━━━━━━━━━━
Pulsa el botón para pedir otro análisis VIP 👇
"""

    return mensaje

# ===============================
# BOT LOOP
# ===============================
def iniciar_bot():
    offset = None
    enviar_mensaje(
        "🤖 <b>Bot VIP activo</b>\n\nPulsa el botón para recibir un análisis exclusivo.",
        teclado_vip()
    )

    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            params = {"timeout": 100, "offset": offset}
            r = requests.get(url, params=params).json()

            for update in r["result"]:
                offset = update["update_id"] + 1

                if "callback_query" in update:
                    data = update["callback_query"]["data"]
                    if data == "VIP":
                        mensaje = generar_analisis_vip()
                        enviar_mensaje(mensaje, teclado_vip())

        except Exception as e:
            print("Error:", e)

        time.sleep(2)

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    iniciar_bot()
