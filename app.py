import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAZIONE ---
PULSOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit Live Remote", layout="wide")

st.title("💓 Monitoraggio Cardiaco Moofit (Live)")

# Inizializzazione dati nella sessione
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])

def get_bpm():
    # Nuovo endpoint ufficiale dalla documentazione
    url = "https://dev.pulsoid.net/api/v1/data/heart_rate/latest"
    
    # L'autenticazione ora va negli headers
    headers = {
        "Authorization": f"Bearer {PULSOID_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            json_data = r.json()
            # La nuova struttura è: {"data": {"heart_rate": 80}, ...}
            return json_data.get('data', {}).get('heart_rate')
        elif r.status_code == 403:
            return "Errore: Token non valido (403)"
        elif r.status_code == 412:
            return "In attesa di dati... (Assicurati che l'app sia LIVE)"
        else:
            return f"Errore API: {r.status_code}"
    except Exception as e:
        return f"Errore Connessione: {e}"

# --- INTERFACCIA ---
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Stato Real-time")
    metric_place = st.empty()
    status_place = st.empty()
    st.write("---")
    if len(st.session_state.history) > 0:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica CSV Sessione", data=csv, file_name="sessione_moofit.csv", mime='text/csv')

with col2:
    chart_place = st.empty()

# --- LOOP DI AGGIORNAMENTO ---
while True:
    val = get_bpm()
    
    if isinstance(val, int):
        status_place.success("Segnale Ricevuto ✅")
        now = datetime.now().strftime("%H:%M:%S")
        
        # Aggiungi dato alla cronologia
        new_data = pd.DataFrame({'Orario': [now], 'BPM': [val]})
        st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
        
        # Aggiorna visualizzazione
        metric_place.metric("Battito Attuale", f"{val} BPM")
        # Mostra gli ultimi 100 secondi di grafico
        chart_place.line_chart(st.session_state.history.set_index('Orario').tail(100))
    else:
        metric_place.metric("Battito Attuale", "--")
        status_place.info(f"Stato: {val}")
    
    time.sleep(1) # Pulsoid consiglia di non scendere sotto i 500ms
