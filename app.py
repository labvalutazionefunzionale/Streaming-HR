import streamlit as st
import requests
import pandas as pd
import time
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit Pro Monitor", layout="wide")

# --- INIZIALIZZAZIONE MEMORIA ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Orario', 'BPM'])
if 'running' not in st.session_state:
    st.session_state.running = False

# --- BARRA LATERALE ---
with st.sidebar:
    st.header("🎮 Controlli")
    
    # Bottoni Start e Stop
    col_start, col_stop = st.columns(2)
    if col_start.button("▶️ START", use_container_width=True):
        st.session_state.running = True
    if col_stop.button("⏹️ STOP", use_container_width=True):
        st.session_state.running = False
        
    st.write("---")
    
    # Scala Temporale
    st.subheader("⏱️ Visualizzazione")
    window_size = st.slider("Secondi da mostrare nel grafico", 10, 300, 60)
    
    st.write("---")
    
    # Download
    if not st.session_state.history.empty:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", data=csv, file_name="sessione_hrv.csv", use_container_width=True)
        if st.button("🗑️ Reset Dati"):
            st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Orario', 'BPM'])
            st.rerun()

# --- AREA PRINCIPALE ---
st.title("📊 Moofit Pro: Live & HRV Analysis")

col_metric, col_hrv = st.columns(2)
metric_place = col_metric.empty()
hrv_place = col_hrv.empty()

chart_place = st.empty()

def get_bpm():
    url = "https://dev.pulsoid.net/api/v1/data/heart_rate/latest"
    headers = {"Authorization": f"Bearer {PULSOID_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json().get('data', {}).get('heart_rate')
    except:
        return None
    return None

def calculate_hrv(df):
    if len(df) < 10:
        return "Dati insufficienti (min. 10s)"
    # Calcoliamo la SDNN (Standard Deviation of NN intervals)
    # Approssimata dai BPM
    sdnn = np.std(df['BPM'])
    return f"{sdnn:.2f} ms (SDNN stima)"

# --- LOOP DI ESECUZIONE ---
while True:
    if st.session_state.running:
        val = get_bpm()
        
        if isinstance(val, int) and val > 0:
            now_dt = datetime.now()
            now_str = now_dt.strftime("%H:%M:%S")
            
            # Aggiunta dati
            new_row = pd.DataFrame({'Timestamp': [now_dt], 'Orario': [now_str], 'BPM': [val]})
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
            
            # Calcolo metriche
            hrv_val = calculate_hrv(st.session_state.history.tail(window_size))
            
            # Aggiornamento UI
            metric_place.metric("Battito Attuale", f"{val} BPM")
            hrv_place.metric("Variabilità (HRV)", hrv_val)
            
            # Grafico dinamico basato sullo slider
            chart_data = st.session_state.history.set_index('Orario').tail(window_size)
            chart_place.line_chart(chart_data['BPM'])
        else:
            metric_place.warning("Segnale perso o sensore offline...")
    else:
        metric_place.info("Sessione in PAUSA. Clicca START per registrare.")
        if not st.session_state.history.empty:
            chart_data = st.session_state.history.set_index('Orario').tail(window_size)
            chart_place.line_chart(chart_data['BPM'])

    time.sleep(1)
