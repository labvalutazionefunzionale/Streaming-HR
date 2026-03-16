import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pytz
import altair as alt

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit HRV Monitor", layout="wide")

# Refresh automatico ogni 500ms
st_autorefresh(interval=500, key="hr_update")

# --- INIZIALIZZAZIONE MEMORIA ---
if 'history' not in st.session_state:
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
    # 1) Orologio e data in alto a sinistra nella sidebar
    italy_tz = pytz.timezone('Europe/Rome')
    now_italy = datetime.now(italy_tz)
    st.markdown(f"### 🕐 {now_italy.strftime('%H:%M:%S')}")
    st.caption(f"📅 {now_italy.strftime('%d/%m/%Y')}")
    st.write("---")
    
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
        
        # 5) Info aggiuntive
        st.write("---")
        st.info("**Sensore:** armband Moofit  \n**Smartphone app:** Pulsoid  \n**Repository:** GitHub  \n**Web app:** Streamlit" \n**AI tool for coding:** Google Gemini")

# --- DASHBOARD ---
# 2) Nuovo titolo con icona cuore
st.title("📊❤️ Monitoraggio HR e HRV in real time")
st.write("---")

bpm = get_bpm()
current_ts = datetime.now().strftime("%H:%M:%S")

col_val, col_hrv = st.columns(2)

if bpm:
    rr_ms = 60000 / bpm
    col_val.metric("Frequenza Cardiaca", f"{bpm} BPM")
    
    if st.session_state.running:
        if st.session_state.last_timestamp != current_ts:
            sec_elapsed = len(st.session_state.history)
            new_row = pd.DataFrame([{'Secondi': sec_elapsed, 'BPM': bpm, 'RR_ms': rr_ms}])
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
            st.session_state.last_timestamp = current_ts
        
        if len(st.session_state.history) >= 2:
            rolling_data = st.session_state.history['RR_ms'].tail(30)
            sdnn = np.std(rolling_data)
            col_hrv.metric("HRV (SDNN 30s)", f"{sdnn:.2f} ms")
        else:
            col_hrv.info("Inizializzazione HRV...")
    else:
        col_hrv.warning("Registrazione in pausa. Clicca START.")
else:
    col_val.metric("Battito", "--")
    st.error("⚠️ In attesa di segnale...")

# --- GRAFICO AVANZATO (Altair) ---
if not st.session_state.history.empty:
    data_subset = st.session_state.history.tail(window_size)
    
    # Linea principale BPM
    line = alt.Chart(data_subset).mark_line(color='#ff4b4b').encode(
        x=alt.X('Secondi:Q', axis=alt.Axis(grid=True, tickCount=window_size//5, gridDash=[2,2])),
        y=alt.Y('BPM:Q', scale=alt.Scale(domain=[40, 200]))
    )
    
    # 3) Linea di tendenza (regressione)
    trend = line.transform_regression('Secondi', 'BPM').mark_line(strokeDash=[5,5], color='white')
    
    # Rendering del grafico
    st.altair_chart(line + trend, use_container_width=True)
