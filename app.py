import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit Live Remote", layout="wide")

# --- BARRA LATERALE (DOWNLOAD E STATO) ---
with st.sidebar:
    st.header("⚙️ Gestione Dati")
    
    # Inizializzazione dati
    if 'history' not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])
    
    # Bottone di scaricamento (sempre visibile)
    if not st.session_state.history.empty:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 SCARICA DATI CSV",
            data=csv,
            file_name=f"sessione_moofit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime='text/csv',
            use_container_width=True
        )
    else:
        st.info("In attesa di dati per il download...")

    st.write("---")
    status_place = st.empty()

# --- AREA PRINCIPALE ---
st.title("💓 Monitoraggio Cardiaco Moofit")
col_metric, col_chart = st.columns([1, 3])
metric_place = col_metric.empty()
chart_place = col_chart.empty()

def get_bpm():
    url = "https://dev.pulsoid.net/api/v1/data/heart_rate/latest"
    headers = {"Authorization": f"Bearer {PULSOID_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json().get('data', {}).get('heart_rate')
        return f"Errore {r.status_code}"
    except:
        return "Errore Connessione"

# --- LOOP ---
while True:
    val = get_bpm()
    
    if isinstance(val, int) and val > 0:
        status_place.success("📡 Segnale Ricevuto")
        now = datetime.now().strftime("%H:%M:%S")
        
        # Aggiorna DataFrame
        new_row = pd.DataFrame({'Orario': [now], 'BPM': [val]})
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
        
        # Aggiorna UI
        metric_place.metric("BPM Attuale", f"{val}")
        chart_place.line_chart(st.session_state.history.set_index('Orario').tail(50))
    else:
        status_place.warning(f"Stato: {val if val else 'Nessun dato'}")
    
    time.sleep(1)
