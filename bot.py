import os
import json
import time
import random
import requests
from datetime import datetime
import pytz

# =========================
# CONFIG (ENV VARS)
# =========================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =========================
# ZONA HORARIA
# =========================
TZ = pytz.timezone("America/Bogota")

# =========================
# LIGAS VIP (filtro)
# =========================
LIGAS_VIP = {
    "Premier League",
    "LaLiga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "UEFA Champions League",
    "Brasileirão Série A",
}

# =========================
# TELEGRAM HELPERS
# =========================
def tg_send(text, with_button=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    if with_button:
        keyboard = {
            "inline_keyboard": [[
                {"text": "🔥 Pedir análisis VIP", "callback_data": "VIP"}
            ]]
        }
        payload["reply_markup"] = json.dumps(keyboard)
    requests.post(url, data=payload, timeout=30)

def tg_answer_callback(cb_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    requests.post(url, data={"callback_query_id": cb_id}, timeout=30)

# =========================
# UTILIDADES
# =========================
def now_col():
    return datetime.now(TZ).strftime("%d/%m/%Y %I:%M %p")

def choice_weighted(items):
    # items: list of (obj, weight)
    total = sum(w for _, w in items)
    r = random.uniform(0, total)
    upto = 0
    for obj, w in items:
        if upto + w >= r:
            return obj
        upto += w
    return items[-1][0]

# =========================
# ANALÍTICA VIP (3 CAPAS)
# =========================
def analizar_primer_tiempo():
    # Capa base
    base = random.randint(55, 62)
    # Ajuste histórico (simulado)
    hist = random.randint(5, 10)
    # Ajuste mixto
    mix = random.randint(2, 5)
    prob = min(85, base + hist + mix)

    escenario = "⏱ Gol en el 1T"
    diagnostico = (
        "Se observa intensidad temprana y presión ofensiva inicial. "
        "Los patrones recientes favorecen llegadas claras antes del descanso."
    )
    return {"escenario": escenario, "prob": prob, "diag": diagnostico}

def analizar_total_goles():
    base = random.randint(52, 60)
    hist = random.randint(4, 9)
    mix = random.randint(2, 5)
    prob = min(82, base + hist + mix)

    escenario = "⚽ Más de 2.5 goles"
    diagnostico = (
        "El contexto apunta a un partido abierto, con promedios ofensivos "
        "consistentes y generación continua de ocasiones."
    )
    return {"escenario": escenario, "prob": prob, "diag": diagnostico}

def analizar_remates():
    base = random.randint(50, 58)
    hist = random.randint(4, 8)
    mix = random.randint(2, 5)
    prob = min(80, base + hist + mix)

    escenario = "🎯 Dominio en remates del equipo más ofensivo"
    diagnostico = (
        "Se espera presión sostenida y mayor volumen de tiros, "
        "indicando control ofensivo prolongado."
    )
    return {"escenario": escenario, "prob": prob, "diag": diagnostico}

def generar_vip():
    # (Simulación de partido y liga VIP)
    liga = random.choice(list(LIGAS_VIP))
    local = random.choice(["Equipo Local", "Local FC", "Atlético Local"])
    visita = random.choice(["Equipo Visitante", "United Visit", "Deportivo Visit"])
    hora = now_col()

    # Ejecutar análisis
    a = analizar_primer_tiempo()
    b = analizar_total_goles()
    c = analizar_remates()

    # Elegir el de MAYOR probabilidad
    ganador = max([a, b, c], key=lambda x: x["prob"])

    mensaje = (
        "🔥 ANÁLISIS VIP AVANZADO – FÚTBOL\n\n"
        f"🏆 Partido: {local} vs {visita}\n"
        f"🏟 Liga: {liga}\n"
        f"⏰ Hora (COL): {hora}\n\n"
        "📊 ESCENARIO CON MAYOR PROBABILIDAD\n\n"
        f"{ganador['escenario']}\n"
        f"Probabilidad estimada: {ganador['prob']}%\n\n"
        "📌 Diagnóstico:\n"
        f"{ganador['diag']}\n"
    )
    return mensaje

# =========================
# LOOP DE ACTUALIZACIONES
# =========================
def listen():
    offset = None
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        res = requests.get(url, params=params, timeout=35).json()

        for upd in res.get("result", []):
            offset = upd["update_id"] + 1

            if "callback_query" in upd:
                cb = upd["callback_query"]
                tg_answer_callback(cb["id"])
                vip_msg = generar_vip()
                tg_send(vip_msg)
                tg_send(" ", with_button=True)

        time.sleep(1)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    tg_send(
        "🔥 BOT VIP DE ANÁLISIS – FÚTBOL\n\nPulsa el botón para recibir el análisis VIP:",
        with_button=True
    )
    listen()
