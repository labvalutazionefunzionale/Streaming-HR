import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "IL_TUO_TOKEN_QUI"

st.set_page_config(page_title="Moofit Real-Time Monitor", layout="wide")

# Questo comando forza l'app a rinfrescarsi ogni 1000ms (1 secondo)
# È il modo più stabile per vedere i dati live su Streamlit Cloud
st_autorefresh(interval=1000, key="datarefresh")

# --- INIZIALIZZAZIONE MEMORIA ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
if 'running' not in st.session_state:
    st.session_state.running = False

# --- FUNZIONE API (OTTIMIZZATA) ---
def get_bpm():
    url = "https://dev.pulsoid.net/api/v1/data/heart_rate/latest"
    headers = {"Authorization": f"Bearer {PULSOID_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=2)
        if r.status_code == 200:
            data = r.json()
            # Pulsoid fornisce anche il timestamp esatto del battito
            return data.get('data', {}).get('heart_rate')
    except:
        return None
    return None

# --- BARRA LATERALE ---
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
        st.write("---")
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV", data=csv, file_name="sessione_moofit.csv", use_container_width=True)
        if st.button("🗑️ Reset Dati"):
            st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
            st.rerun()

# --- AREA PRINCIPALE ---
st.title("💓 Moofit Live Streaming")

val = get_bpm()
now_str = datetime.now().strftime("%H:%M:%S")

col_metric, col_status = st.columns(2)

if val:
    col_metric.metric("Battito Istantaneo", f"{val} BPM")
    
    if st.session_state.running:
        col_status.success("🔴 REGISTRAZIONE ATTIVA")
        # Evitiamo duplicati: aggiungi solo se l'ultimo battito è diverso o è passato tempo
        new_row = pd.DataFrame({'Orario': [now_str], 'BPM': [val]})
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True).drop_duplicates(subset=['Orario'], keep='last')
    else:
        col_status.warning("⏸️ IN PAUSA")
else:
    col_metric.metric("Battito Istantaneo", "--")
    col_status.error("⚠️ Nessun dato. Verifica l'app Pulsoid sul telefono.")

# --- GRAFICO ---
if not st.session_state.history.empty:
    # Mostra gli ultimi X secondi basati sullo slider
    chart_data = st.session_state.history.tail(window_size).set_index('Orario')
    st.line_chart(chart_data)

    # Analisi HRV SDNN (Stima veloce)
    if len(st.session_state.history) > 10:
        sdnn = np.std(st.session_state.history['BPM'].tail(30))
        st.info(f"Stima Variabilità (SDNN ultimi 30s): {sdnn:.2f} ms")
