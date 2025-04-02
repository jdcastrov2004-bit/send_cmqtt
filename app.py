import streamlit as st
import paho.mqtt.client as paho
import json
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Control MQTT",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #004d99;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .status-connected {
        padding: 5px 10px;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        text-align: center;
    }
    .status-disconnected {
        padding: 5px 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
        text-align: center;
    }
    .control-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .message-box {
        height: 200px;
        overflow-y: auto;
        background-color: #f1f1f1;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Variables globales
message_received = ""
message_history = []
connected = False

# Inicializar variables en session state si no existen
if 'message_history' not in st.session_state:
    st.session_state.message_history = []
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = False

# Funciones de callback MQTT
def on_connect(client, userdata, flags, rc):
    """Callback cuando se conecta al broker"""
    if rc == 0:
        st.session_state.connection_status = True
        st.success("Conectado al broker MQTT")
    else:
        st.session_state.connection_status = False
        st.error(f"Error de conexión al broker, código: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback cuando se desconecta del broker"""
    st.session_state.connection_status = False
    if rc != 0:
        st.error("Desconexión inesperada del broker MQTT")

def on_publish(client, userdata, mid):
    """Callback cuando se publica un mensaje"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    message_info = {"time": timestamp, "type": "enviado", "content": "Mensaje publicado correctamente"}
    st.session_state.message_history.append(message_info)

def on_message(client, userdata, message):
    """Callback cuando se recibe un mensaje"""
    global message_received
    timestamp = datetime.now().strftime("%H:%M:%S")
    message_received = str(message.payload.decode("utf-8"))
    message_info = {"time": timestamp, "type": "recibido", "content": message_received}
    st.session_state.message_history.append(message_info)

# Función para inicializar cliente MQTT
def initialize_mqtt_client():
    """Inicializa y retorna un cliente MQTT configurado"""
    client = paho.Client(client_id=st.session_state.client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_message = on_message
    return client

# Función para conectar al broker MQTT
def connect_to_broker():
    """Conecta al broker MQTT con los parámetros actuales"""
    try:
        client = initialize_mqtt_client()
        client.connect(st.session_state.broker, st.session_state.port, 60)
        client.loop_start()
        return client
    except Exception as e:
        st.error(f"Error al conectar: {str(e)}")
        return None

# Función para publicar mensaje
def publish_message(topic, payload):
    """Publica un mensaje en el tópico especificado"""
    try:
        client = initialize_mqtt_client()
        client.connect(st.session_state.broker, st.session_state.port, 60)
        message = json.dumps(payload)
        result = client.publish(topic, message)
        client.disconnect()
        return result.rc == 0
    except Exception as e:
        st.error(f"Error al publicar: {str(e)}")
        return False

# Sidebar para configuración
st.sidebar.markdown("<h2 style='text-align: center;'>Configuración</h2>", unsafe_allow_html=True)

# Configuración del broker
with st.sidebar.expander("Configuración de Conexión", expanded=True):
    # Inicializar valores en session_state si no existen
    if 'broker' not in st.session_state:
        st.session_state.broker = "broker.mqttdashboard.com"
    if 'port' not in st.session_state:
        st.session_state.port = 1883
    if 'client_id' not in st.session_state:
        st.session_state.client_id = "GIT-HUB"
    
    # Campos de entrada para configuración
    broker_input = st.text_input("Broker MQTT", value=st.session_state.broker)
    port_input = st.number_input("Puerto", value=st.session_state.port, min_value=1, max_value=65535)
    client_id_input = st.text_input("ID de Cliente", value=st.session_state.client_id)
    
    # Actualizar session_state con los nuevos valores
    if broker_input != st.session_state.broker:
        st.session_state.broker = broker_input
    if port_input != st.session_state.port:
        st.session_state.port = port_input
    if client_id_input != st.session_state.client_id:
        st.session_state.client_id = client_id_input

# Botón para conectar/desconectar
if st.sidebar.button("Conectar al Broker"):
    client = connect_to_broker()
    if client:
        st.sidebar.success("Conexión iniciada")
    else:
        st.sidebar.error("Error al conectar")

# Información de estado
st.sidebar.markdown("### Estado de la Conexión")
if st.session_state.connection_status:
    st.sidebar.markdown(f"<div class='status-connected'>Conectado a {st.session_state.broker}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div class='status-disconnected'>Desconectado</div>", unsafe_allow_html=True)

# Título principal
st.markdown("<h1 class='main-header'>Sistema de Control MQTT</h1>", unsafe_allow_html=True)

# Contenido principal
col1, col2 = st.columns(2)

# Panel de control digital
with col1:
    st.markdown("<h2 class='section-header'>Control Digital</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='control-card'>", unsafe_allow_html=True)
        
        # Control ON/OFF con botones mejorados
        st.markdown("### Control de Dispositivo")
        on_col, off_col = st.columns(2)
        
        with on_col:
            if st.button("ENCENDER", key="btn_on", use_container_width=True):
                payload = {"Act1": "ON"}
                if publish_message("cmqtt_s", payload):
                    st.success("Comando ON enviado")
        
        with off_col:
            if st.button("APAGAR", key="btn_off", use_container_width=True):
                payload = {"Act1": "OFF"}
                if publish_message("cmqtt_s", payload):
                    st.success("Comando OFF enviado")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Panel de control analógico
with col2:
    st.markdown("<h2 class='section-header'>Control Analógico</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='control-card'>", unsafe_allow_html=True)
        
        # Control con slider
        st.markdown("### Control de Valor Analógico")
        analog_value = st.slider('Ajustar valor', 0.0, 100.0, 50.0, 0.1)
        st.markdown(f"Valor seleccionado: **{analog_value}**")
        
        if st.button("ENVIAR VALOR", key="btn_analog", use_container_width=True):
            payload = {"Analog": float(analog_value)}
            if publish_message("cmqtt_a", payload):
                st.success(f"Valor {analog_value} enviado correctamente")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Monitoreo de mensajes
st.markdown("<h2 class='section-header'>Monitor de Mensajes</h2>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='control-card'>", unsafe_allow_html=True)
    
    # Tópico para suscripción
    sub_topic = st.text_input("Tópico para suscripción", "Sensores")
    if st.button("Suscribirse", key="btn_subscribe"):
        try:
            client = initialize_mqtt_client()
            client.connect(st.session_state.broker, st.session_state.port, 60)
            client.subscribe(sub_topic)
            client.loop_start()
            st.success(f"Suscrito al tópico: {sub_topic}")
        except Exception as e:
            st.error(f"Error al suscribirse: {str(e)}")
    
    # Mostrar historial de mensajes
    st.markdown("### Historial de Mensajes")
    
    # Crear una caja de mensajes
    message_container = st.container()
    with message_container:
        st.markdown("<div class='message-box'>", unsafe_allow_html=True)
        for msg in st.session_state.message_history:
            if msg["type"] == "enviado":
                st.markdown(f"<small>{msg['time']}</small> ➡️ {msg['content']}", unsafe_allow_html=True)
            else:
                st.markdown(f"<small>{msg['time']}</small> ⬅️ {msg['content']}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Botón para limpiar historial
    if st.button("Limpiar Historial", key="btn_clear"):
        st.session_state.message_history = []
        st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Información del sistema
st.markdown("""
<div style='text-align: center; margin-top: 30px; color: #6c757d;'>
    <small>Sistema de Control MQTT v1.0 | Desarrollado con Streamlit y Paho MQTT</small>
</div>
""", unsafe_allow_html=True)
