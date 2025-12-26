import os
import time
import random
import requests
from datetime import datetime
import pytz

# ==============================
# CONFIGURACIÓN (Render)
# ==============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("Faltan variables de entorno TELEGRAM_TOKEN o CHAT_ID")

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

ZONA_COLOMBIA = pytz.timezone("America/Bogota")

# ==============================
# DATOS SIMULADOS VIP (EJEMPLO)
# ==============================
ANALISIS_VIP = [
    {
        "par": "EUR/USD",
        "direccion": "🟢 ARRIBA (BUY)",
        "probabilidad": 78,
        "fundamento": (
            "Alta frecuencia de presión compradora en los primeros minutos, "
            "ruptura reciente de micro-resistencia y patrón de continuidad alcista."
        )
    },
    {
        "par": "EUR/USD",
        "direccion": "🔴 ABAJO (SELL)",
        "probabilidad": 74,
        "fundamento": (
            "Rechazo fuerte en zona de liquidez superior, "
            "debilidad en el impulso y velas de agotamiento."
        )
    }
]

# ==============================
# FUNCIONES TELEGRAM
# ==============================
def enviar_mensaje(texto, botones=None):
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }

    if botones:
        payload["reply_markup"] = {
            "keyboard": botones,
            "resize_keyboard": True
        }

    requests.post(f"{API_URL}/sendMessage", json=payload)


def obtener_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{API_URL}/getUpdates", params=params)
    return r.json()


# ==============================
# MENSAJES
# ==============================
def mensaje_inicio():
    return (
        "🤖 *BOT DE ANÁLISIS VIP*\n\n"
        "Pulsa el botón para recibir un análisis exclusivo basado en "
        "probabilidad estadística.\n\n"
        "_Análisis informativo. No constituye recomendación de inversión._"
    )


def generar_analisis_vip():
    dato = random.choice(ANALISIS_VIP)
    ahora = datetime.now(ZONA_COLOMBIA).strftime("%d/%m/%Y %I:%M %p")

    return (
        "💎 *ANÁLISIS VIP*\n\n"
        f"📊 *Par:* {dato['par']}\n"
        f"⏰ *Hora (Colombia):* {ahora}\n"
        f"📈 *Señal:* {dato['direccion']}\n"
        f"🎯 *Probabilidad estimada:* {dato['probabilidad']}%\n\n"
        "📌 *Fundamentación:*\n"
        f"{dato['fundamento']}\n\n"
        "_Análisis estadístico informativo. "
        "No constituye recomendación de apuesta._"
    )


# ==============================
# BOT PRINCIPAL
# ==============================
def iniciar_bot():
    print("🤖 Bot VIP iniciado correctamente")
    enviar_mensaje(
        mensaje_inicio(),
        botones=[["📊 Pedir análisis VIP"]]
    )

    offset = None

    while True:
        updates = obtener_updates(offset)

        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1

                if "message" in update:
                    texto = update["message"].get("text", "")

                    if texto in ["/start", "📊 Pedir análisis VIP"]:
                        enviar_mensaje(
                            generar_analisis_vip(),
                            botones=[["📊 Pedir análisis VIP"]]
                        )

        time.sleep(1)


# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    iniciar_bot()

