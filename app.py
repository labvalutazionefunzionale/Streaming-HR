import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit HRV Pro", layout="wide")

# Refresh automatico ogni 500ms per catturare ogni variazione dell'API
st_autorefresh(interval=500, key="hr_update")

# --- INIZIALIZZAZIONE ---
if 'history' not in st.session_state:
    # Salviamo sia i BPM che gli intervalli RR per l'analisi
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM', 'RR_ms'])
if 'running' not in st.session_state:
    st.session_state.running = False

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
    window_size = st.slider("Secondi nel grafico", 10, 300, 60)
    
    if not st.session_state.history.empty:
        st.write("---")
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", data=csv, file_name="sessione_moofit.csv", use_container_width=True)
        if st.button("🗑️ Reset Dati"):
            st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM', 'RR_ms'])
            st.session_state.running = False
            st.rerun()

# --- DASHBOARD ---
st.title("📊 Monitoraggio Moofit & Analisi HRV")

bpm = get_bpm()
now_str = datetime.now().strftime("%H:%M:%S")

col_val, col_hrv = st.columns(2)

if bpm:
    # Calcolo istantaneo dell'intervallo R-R in ms
    rr_ms = 60000 / bpm
    
    col_val.metric("Frequenza Cardiaca", f"{bpm} BPM")
    
    if st.session_state.running:
        # Registra il dato solo se in START e se il secondo è cambiato
        if st.session_state.history.empty or st.session_state.history.iloc[-1]['Orario'] != now_str:
            new_row = pd.DataFrame([{'Orario': now_str, 'BPM': bpm, 'RR_ms': rr_ms}])
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
        
        # Analisi HRV (SDNN sugli intervalli RR)
        if len(st.session_state.history) > 10:
            # Calcoliamo la deviazione standard degli intervalli R-R (SDNN)
            sdnn = np.std(st.session_state.history['RR_ms'].tail(30))
            col_hrv.metric("HRV (SDNN 30s)", f"{sdnn:.2f} ms")
        else:
            col_hrv.info("Raccolta dati per HRV...")
    else:
        col_hrv.warning("Registrazione in pausa")
else:
    col_val.metric("Battito", "--")
    st.error("⚠️ Nessun dato da Pulsoid. Controlla che il Moofit sia connesso all'app sul telefono.")

# --- GRAFICO ---
if not st.session_state.history.empty:
    # Mostriamo i BPM nel grafico per facilità di lettura
    chart_data = st.session_state.history.tail(window_size).set_index('Orario')
    st.line_chart(chart_data['BPM'])
