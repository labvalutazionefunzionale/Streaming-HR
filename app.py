import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

PULSEOID_TOKEN = "6f519fde-0ec2-4bc1-a108-8812f6f0c102"

st.set_page_config(page_title="Moofit Live Remote", layout="wide")

st.title("💓 Monitoraggio Cardiaco Moofit (Live)")

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])

def get_bpm():
    url = f"https://pulseoid.net/v1/api/get_actual_heart_rate?access_token={PULSEOID_TOKEN}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            # Pulseoid restituisce il battito o None se il sensore è offline
            return data.get('heart_rate')
        else:
            return f"Errore API: {r.status_code}"
    except Exception as e:
        return f"Errore Connessione: {e}"

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Stato Sensore")
    metric_place = st.empty()
    status_place = st.empty()
    st.write("---")
    if len(st.session_state.history) > 0:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica dati CSV", data=csv, file_name="sessione_moofit.csv", mime='text/csv')

with col2:
    chart_place = st.empty()

while True:
    val = get_bpm()
    
    # Se il valore è un numero (battito ricevuto)
    if isinstance(val, int) and val > 0:
        status_place.success("Segnale Ricevuto ✅")
        now = datetime.now().strftime("%H:%M:%S")
        new_data = pd.DataFrame({'Orario': [now], 'BPM': [val]})
        st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
        
        metric_place.metric("Battito Attuale", f"{val} BPM")
        chart_place.line_chart(st.session_state.history.set_index('Orario').tail(100))
    
    # Se il valore è None o un messaggio d'errore
    else:
        metric_place.metric("Battito Attuale", "--")
        if val is None:
            status_place.warning("Sensore Offline ⚠️ (Assicurati che l'app sul telefono sia su LIVE)")
        else:
            status_place.error(f"Problema: {val}")
    
    time.sleep(1)
