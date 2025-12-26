import os
import random
import time
import requests
from datetime import datetime
import pytz

# ================= CONFIGURACIÓN =================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

ZONA_COLOMBIA = pytz.timezone("America/Bogota")

BOT_NAME = "ANÁLISIS VIP – FÚTBOL"

# ================= DATOS SIMULADOS / ESTADÍSTICOS =================
PARTIDOS = [
    {
        "liga": "Premier League",
        "partido": "Manchester United vs Newcastle",
        "hora": "03:00 PM"
    },
    {
        "liga": "LaLiga",
        "partido": "Barcelona vs Real Sociedad",
        "hora": "04:00 PM"
    },
    {
        "liga": "Eliminatorias Mundial 2026",
        "partido": "Colombia vs Uruguay",
        "hora": "07:00 PM"
    },
    {
        "liga": "Mundial 2026 – Proyección",
        "partido": "Brasil vs Alemania",
        "hora": "08:00 PM"
    }
]

MERCADOS = [
    {
        "nombre": "Más de 2.5 goles",
        "fundamento": "Promedios goleadores elevados, presión ofensiva sostenida y antecedentes recientes con marcadores amplios."
    },
    {
        "nombre": "Gol en primer tiempo",
        "fundamento": "Alta frecuencia de anotaciones tempranas y ritmo ofensivo desde el inicio."
    },
    {
        "nombre": "Ambos equipos anotan",
        "fundamento": "Defensas vulnerables y registros consistentes de gol por ambas escuadras."
    },
    {
        "nombre": "Gana o empata el favorito",
        "fundamento": "Superioridad estadística, mayor posesión promedio y mejor rendimiento reciente."
    }
]

# ================= FUNCIONES TELEGRAM =================
def enviar_mensaje(texto, boton=True):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }

    if boton:
        data["reply_markup"] = {
            "keyboard": [[{"text": "📊 Pedir análisis VIP"}]],
            "resize_keyboard": True
        }

    requests.post(url, json=data)

# ================= ANÁLISIS VIP =================
def generar_analisis_vip():
    partido = random.choice(PARTIDOS)
    mercado = random.choice(MERCADOS)
    probabilidad = random.randint(68, 79)

    ahora = datetime.now(ZONA_COLOMBIA).strftime("%d/%m/%Y %I:%M %p")

    mensaje = f"""
💎 <b>{BOT_NAME}</b>

🏆 <b>Liga:</b> {partido['liga']}
⏰ <b>Hora (Colombia):</b> {partido['hora']}
⚽ <b>Partido:</b> {partido['partido']}

🎯 <b>Pronóstico con mayor probabilidad:</b>
👉 {mercado['nombre']}

📈 <b>Probabilidad estimada:</b> {probabilidad}%

📌 <b>Fundamentación:</b>
{mercado['fundamento']}

🗓 <i>Generado:</i> {ahora}
    """

    return mensaje

# ================= LOOP PRINCIPAL =================
def escuchar_bot():
    enviar_mensaje("🤖 Bot VIP activo.\nPulsa el botón para recibir un análisis exclusivo.")

    last_update_id = None

    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"timeout": 100, "offset": last_update_id}
        resp = requests.get(url, params=params).json()

        if "result" in resp:
            for update in resp["result"]:
                last_update_id = update["update_id"] + 1

                if "message" in update:
                    texto = update["message"].get("text", "")

                    if "Pedir análisis VIP" in texto:
                        analisis = generar_analisis_vip()
                        enviar_mensaje(analisis)

        time.sleep(2)

# ================= INICIO =================
if __name__ == "__main__":
    escuchar_bot()


