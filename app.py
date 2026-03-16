import streamlit as st
import pandas as pd
import json
import websocket
import threading
import time  # <--- Questa è la riga che mancava!
from datetime import datetime

# --- CONFIGURAZIONE ---
# Inserisci il tuo Token tra le virgolette
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"
WS_URL = f"wss://dev.pulsoid.net/api/v1/data/heart_rate/latest?access_token={PULSOID_TOKEN}"

st.set_page_config(page_title="Moofit Real-Time WebSocket", layout="wide")

# --- INIZIALIZZAZIONE MEMORIA ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
if 'running' not in st.session_state:
    st.session_state.running = False
if 'last_bpm' not in st.session_state:
    st.session_state.last_bpm = 0

# --- LOGICA WEBSOCKET ---
# Questa funzione gira "dietro le quinte" e cattura i dati
def on_message(ws, message):
    try:
        data = json.loads(message)
        bpm = data.get('data', {}).get('heart_rate')
        if bpm:
            st.session_state.last_bpm = bpm
            if st.session_state.running:
                now_str = datetime.now().strftime("%H:%M:%S")
                # Usiamo una lista per creare il nuovo DataFrame (più veloce)
                new_row = pd.DataFrame([{'Orario': now_str, 'BPM': bpm}])
                st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
    except Exception as e:
        pass # Ignora errori di parsing momentanei

def run_socket():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()

# Avviamo il thread del WebSocket solo la prima volta
if 'ws_active' not in st.session_state:
    thread = threading.Thread(target=run_socket, daemon=True)
    thread.start()
    st.session_state.ws_active = True

# --- INTERFACCIA UTENTE ---
st.title("⚡ Moofit Native Streaming (WebSocket)")

with st.sidebar:
    st.header("🎮 Controlli")
    col1, col2 = st.columns(2)
    if col1.button("▶️ START", use_container_width=True, type="primary"):
        st.session_state.running = True
    if col2.button("⏹️ STOP", use_container_width=True):
        st.session_state.running = False
    
    st.write("---")
    window_size = st.slider("Secondi nel grafico", 10, 300, 60)
    
    if not st.session_state.history.empty:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", data=csv, file_name="sessione_moofit.csv", use_container_width=True)
        if st.button("🗑️ Reset Dati"):
            st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
            st.rerun()

# Layout Dashboard
c1, c2 = st.columns(2)
c1.metric("Battito Istantaneo", f"{st.session_state.last_bpm} BPM")
status_txt = "🔴 REGISTRAZIONE ATTIVA" if st.session_state.running else "⏸️ IN PAUSA"
c2.subheader(status_txt)

# Grafico
if not st.session_state.history.empty:
    chart_data = st.session_state.history.tail(window_size).set_index('Orario')
    st.line_chart(chart_data['BPM'])

# --- REFRESH AUTOMATICO ---
# Aspettiamo 1 secondo e poi ricarichiamo la pagina per mostrare i nuovi dati
time.sleep(1)
st.rerun()
