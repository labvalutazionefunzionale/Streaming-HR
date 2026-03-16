import streamlit as st
import pandas as pd
import json
import websocket
from datetime import datetime
import threading

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"
WS_URL = f"wss://dev.pulsoid.net/api/v1/data/heart_rate/latest?access_token={PULSOID_TOKEN}"

st.set_page_config(page_title="Moofit Real-Time WebSocket", layout="wide")

# --- INIZIALIZZAZIONE ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
if 'running' not in st.session_state:
    st.session_state.running = False
if 'last_bpm' not in st.session_state:
    st.session_state.last_bpm = 0

# --- LOGICA WEBSOCKET IN BACKGROUND ---
# Usiamo un thread separato per ascoltare il flusso continuo senza bloccare l'interfaccia
def on_message(ws, message):
    data = json.loads(message)
    bpm = data.get('data', {}).get('heart_rate')
    if bpm:
        st.session_state.last_bpm = bpm
        if st.session_state.running:
            now_str = datetime.now().strftime("%H:%M:%S")
            new_row = pd.DataFrame({'Orario': [now_str], 'BPM': [bpm]})
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

def start_ws():
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
    ws.run_forever()

# Avvia il thread se non è già attivo
if 'ws_thread' not in st.session_state:
    st.session_state.ws_thread = threading.Thread(target=start_ws, daemon=True)
    st.session_state.ws_thread.start()

# --- INTERFACCIA ---
with st.sidebar:
    st.header("🎮 Controlli Real-time")
    col1, col2 = st.columns(2)
    if col1.button("▶️ START", use_container_width=True, type="primary"):
        st.session_state.running = True
    if col2.button("⏹️ STOP", use_container_width=True):
        st.session_state.running = False
    
    window_size = st.slider("Secondi da mostrare", 10, 300, 60)
    
    if not st.session_state.history.empty:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", data=csv, file_name="sessione_live.csv", use_container_width=True)
        if st.button("🗑️ Reset"):
            st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
            st.rerun()

# --- DASHBOARD ---
st.title("⚡ Moofit Native Streaming (WebSocket)")

c1, c2 = st.columns(2)
c1.metric("Battito Istantaneo", f"{st.session_state.last_bpm} BPM")
state_text = "🔴 REGISTRAZIONE ATTIVA" if st.session_state.running else "⏸️ IN PAUSA"
c2.write(f"### Stato: {state_text}")

chart_place = st.empty()

# Aggiornamento grafico
if not st.session_state.history.empty:
    display_df = st.session_state.history.tail(window_size)
    chart_place.line_chart(display_df.set_index('Orario')['BPM'])

# Auto-refresh dell'interfaccia ogni secondo per mostrare i dati arrivati via WS
time.sleep(1)
st.rerun()
