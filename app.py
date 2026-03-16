import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pytz

# --- CONFIGURAZIONE ---
# Il tuo Token inserito direttamente
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit HRV Monitor", layout="wide")

# Refresh automatico ogni 500ms per la massima reattività
st_autorefresh(interval=500, key="hr_update")

# --- INIZIALIZZAZIONE MEMORIA ---
if 'history' not in st.session_state:
    # Salviamo Secondi relativi, BPM e Intervalli RR
    st.session_state.history = pd.DataFrame(columns=['Secondi', 'BPM', 'RR_ms'])
if 'running' not in st.session_state:
    st.session_state.running = False
if 'last_timestamp' not in st.session_state:
    st.session_state.last_timestamp = ""

def get_bpm():
    url = "https://dev.pulsoid.net/api/v1/data/heart_rate/latest"
    headers = {"Authorization": f"Bearer {PULSOID_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=1)
        if r.status_code == 200:
            return r.json().get('data', {}).get('heart_rate')
    except:
        return None
    return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎮 Controlli Sessione")
    c1, c2 = st.columns(2)
    if c1.button("▶️ START", use_container_width=True, type="primary"):
        st.session_state.running = True
    if c2.button("⏹️ STOP", use_container_width=True):
        st.session_state.running = False
    
    st.write("---")
    window_size = st.slider("Secondi da vedere nel grafico", 10, 300, 60)
    
    if not st.session_state.history.empty:
        st.write("---")
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", data=csv, file_name="sessione_moofit_hrv.csv", use_container_width=True)
        if st.button("🗑️ Reset Dati"):
            st.session_state.history = pd.DataFrame(columns=['Secondi', 'BPM', 'RR_ms'])
            st.session_state.last_timestamp = ""
            st.session_state.running = False
            st.rerun()

# --- DASHBOARD ---
st.title("📊 Analisi HRV Moofit")

# --- ITALIAN TIME CLOCK ---
italy_tz = pytz.timezone('Europe/Rome')
current_time_italy = datetime.now(italy_tz).strftime("%H:%M:%S")
current_date_italy = datetime.now(italy_tz).strftime("%d/%m/%Y")

col_clock, col_empty = st.columns([1, 3])
col_clock.markdown(f"### 🕐 {current_time_italy}")
col_clock.caption(f"Orario italiano - {current_date_italy}")

st.write("---")

bpm = get_bpm()
current_ts = datetime.now().strftime("%H:%M:%S")

col_val, col_hrv = st.columns(2)

if bpm:
    # Calcolo istantaneo intervallo R-R: 60000 / BPM
    rr_ms = 60000 / bpm
    col_val.metric("Frequenza Cardiaca", f"{bpm} BPM")
    
    if st.session_state.running:
        # Registra il dato solo se il secondo è cambiato (1Hz)
        if st.session_state.last_timestamp != current_ts:
            # Il conteggio dei secondi parte da 0 (lunghezza attuale del dataframe)
            sec_elapsed = len(st.session_state.history)
            
            new_row = pd.DataFrame([{'Secondi': sec_elapsed, 'BPM': bpm, 'RR_ms': rr_ms}])
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
            st.session_state.last_timestamp = current_ts
        
        # --- LOGICA HRV (SDNN su 30 secondi) ---
        if len(st.session_state.history) >= 2:
            # Calcoliamo la SDNN sugli ultimi 30 record (30 secondi)
            rolling_data = st.session_state.history['RR_ms'].tail(30)
            sdnn = np.std(rolling_data)
            col_hrv.metric("HRV (SDNN 30s)", f"{sdnn:.2f} ms")
            
            # Nota: L'HRV si aggiorna ad ogni nuovo dato ricevuto basandosi 
            # sempre sulla finestra degli ultimi 30 secondi registrati.
        else:
            col_hrv.info("Inizializzazione HRV...")
    else:
        col_hrv.warning("Registrazione in pausa. Clicca START.")
else:
    col_val.metric("Battito", "--")
    st.error("⚠️ In attesa di segnale... Verifica che l'app Pulsoid sia aperta sul telefono.")

# --- GRAFICO ---
if not st.session_state.history.empty:
    # Usiamo 'Secondi' come asse X (partendo da 0)
    chart_data = st.session_state.history.tail(window_size).set_index('Secondi')
    st.line_chart(chart_data['BPM'])
