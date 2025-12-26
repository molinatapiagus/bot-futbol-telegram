import requests
import json
import random
import time
from datetime import datetime
import pytz

# ================= CONFIGURACIÓN =================

TELEGRAM_TOKEN = "7845349417:AAFE_sOJWSZAHsZkuBL-tBv400APUXhTrD4"
CHAT_ID = "5721262552"
FOOTBALL_DATA_TOKEN = "1d2a00ad2c3444f19fbbccb445d92721"

ZONA_COLOMBIA = pytz.timezone("America/Bogota")

LIGAS_PERMITIDAS = [
    "Premier League",
    "Serie A",
    "Bundesliga",
    "Primera Division",
    "Ligue 1",
    "Campeonato Brasileiro Série A",
    "UEFA Champions League"
]

# ================= FUNCIONES TELEGRAM =================

def enviar_mensaje(texto, boton=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    if boton:
        teclado = {
            "inline_keyboard": [
                [{"text": "📊 Pedir predicción", "callback_data": "PEDIR"}]
            ]
        }
        data["reply_markup"] = json.dumps(teclado)

    requests.post(url, data=data)

def responder_callback(callback_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    requests.post(url, data={"callback_query_id": callback_id})

# ================= API FÚTBOL =================

def obtener_partidos():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}
    return requests.get(url, headers=headers).json()

def hora_colombia(fecha_utc):
    fecha = datetime.fromisoformat(fecha_utc.replace("Z", "+00:00"))
    return fecha.astimezone(ZONA_COLOMBIA).strftime("%d/%m/%Y %I:%M %p")

def generar_prediccion():
    datos = obtener_partidos()
    partidos = [
        p for p in datos.get("matches", [])
        if p["competition"]["name"] in LIGAS_PERMITIDAS
    ]

    if not partidos:
        return "❌ No hay partidos disponibles en este momento."

    partido = random.choice(partidos)

    return (
        "📊 PREDICCIÓN\n\n"
        f"🏆 Liga: {partido['competition']['name']}\n"
        f"⏰ Hora: {hora_colombia(partido['utcDate'])}\n"
        f"⚽ Partido: {partido['homeTeam']['name']} vs {partido['awayTeam']['name']}\n\n"
        f"👉 Mejor opción: {partido['homeTeam']['name']} gana o empata"
    )

# ================= ESCUCHAR BOTONES =================

def escuchar():
    offset = None
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        r = requests.get(url, params=params).json()

        for u in r.get("result", []):
            offset = u["update_id"] + 1

            if "callback_query" in u:
                callback_id = u["callback_query"]["id"]

                responder_callback(callback_id)

                texto = generar_prediccion()
                enviar_mensaje(texto)

                # 🔁 BOTÓN NUEVO SIEMPRE ABAJO
                enviar_mensaje(
                    "Pulsa el botón para pedir otra predicción:",
                    boton=True
                )

        time.sleep(1)

# ================= MAIN =================

if __name__ == "__main__":
    print("🤖 Bot activo y estable")
    enviar_mensaje(
        "⚽ BOT DE PREDICCIONES DE FÚTBOL\n\nPulsa el botón para comenzar:",
        boton=True
    )
    escuchar()
