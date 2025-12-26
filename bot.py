import requests
import json
import random
import time
from datetime import datetime
import pytz
import os

# ==================================================
# CONFIGURACIÓN (RENDER USA VARIABLES DE ENTORNO)
# ==================================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
FOOTBALL_DATA_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN")

# ==================================================
# ZONA HORARIA COLOMBIA
# ==================================================

ZONA_COLOMBIA = pytz.timezone("America/Bogota")

# ==================================================
# LIGAS PERMITIDAS
# ==================================================

LIGAS_PERMITIDAS = [
    "Premier League",
    "Serie A",
    "Bundesliga",
    "Primera Division",
    "Ligue 1",
    "Campeonato Brasileiro Série A",
    "UEFA Champions League"
]

# ==================================================
# FUNCIONES TELEGRAM
# ==================================================

def enviar_mensaje(texto, boton=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    if boton:
        teclado = {
            "inline_keyboard": [
                [
                    {
                        "text": "📊 Pedir predicción",
                        "callback_data": "PEDIR"
                    }
                ]
            ]
        }
        data["reply_markup"] = json.dumps(teclado)

    requests.post(url, data=data)


def responder_callback(callback_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    requests.post(url, data={"callback_query_id": callback_id})

# ==================================================
# API FÚTBOL
# ==================================================

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

    liga = partido["competition"]["name"]
    local = partido["homeTeam"]["name"]
    visitante = partido["awayTeam"]["name"]
    hora = hora_colombia(partido["utcDate"])

    return (
        "📊 PREDICCIÓN DE FÚTBOL\n\n"
        f"🏆 Liga: {liga}\n"
        f"⏰ Hora (Colombia): {hora}\n"
        f"⚽ Partido: {local} vs {visitante}\n\n"
        f"👉 Mejor opción: {local} gana o empata"
    )

# ==================================================
# ESCUCHAR BOTONES (SIN BUCLES)
# ==================================================

def escuchar():
    offset = None

    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        respuesta = requests.get(url, params=params).json()

        for update in respuesta.get("result", []):
            offset = update["update_id"] + 1

            if "callback_query" in update:
                callback_id = update["callback_query"]["id"]

                responder_callback(callback_id)

                # Enviar predicción
                texto = generar_prediccion()
                enviar_mensaje(texto)

                # Enviar botón nuevo abajo
                enviar_mensaje(
                    "Pulsa el botón para pedir otra predicción:",
                    boton=True
                )

        time.sleep(1)

# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":
    print("🤖 Bot activo y estable (Render ready)")
    enviar_mensaje(
        "⚽ BOT DE PREDICCIONES DE FÚTBOL\n\nPulsa el botón para comenzar:",
        boton=True
    )
    escuchar()

