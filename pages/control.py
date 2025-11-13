import json
import time
import platform
import streamlit as st
import paho.mqtt.client as paho
from PIL import Image

st.set_page_config(page_title="Control MQTT", page_icon="📡", layout="centered")

# Imagen principal
st.image("meme.png", use_container_width=True)

st.title("📡 Control MQTT")
st.caption(f"Versión de Python: {platform.python_version()}")

BROKER = "broker.mqttdashboard.com"   # ¡Ojo! sin 'http://'
PORT   = 1883
TOPIC  = "cmyk_s"

# ---------------- MQTT callbacks ----------------
def on_publish(client, userdata, mid):
    st.toast("Mensaje publicado ✅", icon="✅")

def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
    except Exception:
        payload = str(message.payload)
    st.info(f"📩 Mensaje recibido en **{message.topic}**: {payload}")

# ---------------- Cliente (persistente) ----------------
def get_client():
    if "mqtt_client" in st.session_state:
        return st.session_state["mqtt_client"]
    client = paho.Client(client_id="JUANDA-21github", clean_session=True)
    client.on_publish = on_publish
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, keepalive=30)
        st.session_state["mqtt_client"] = client
    except Exception as e:
        st.error(f"No se pudo conectar al broker MQTT: {e}")
    return client

client = get_client()

st.write("Usa los botones para enviar comandos ON/OFF y el control deslizante para un valor analógico.")

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 ON", use_container_width=True):
        if client:
            payload = json.dumps({"Act1": "ON"})
            client.publish(TOPIC, payload)
        else:
            st.error("Cliente MQTT no disponible.")

with col2:
    if st.button("🔴 OFF", use_container_width=True):
        if client:
            payload = json.dumps({"Act1": "OFF"})
            client.publish(TOPIC, payload)
        else:
            st.error("Cliente MQTT no disponible.")

st.divider()

value = st.slider("Selecciona el valor analógico", 0.0, 100.0, 50.0)
st.write(f"Valor: **{value:.1f}**")

if st.button("📤 Enviar valor analógico", type="primary"):
    if client:
        payload = json.dumps({"Analog": float(value)})
        client.publish(TOPIC, payload)
    else:
        st.error("Cliente MQTT no disponible.")

st.markdown("---")
st.caption(f"Broker: `{BROKER}` • Topic: `{TOPIC}` • Puerto: `{PORT}`")
