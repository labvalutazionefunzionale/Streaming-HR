import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Moofit Live Remote", layout="wide")

st.title("💓 Monitoraggio Cardiaco Moofit (Live)")

# --- CONFIGURAZIONE ---
# Inserisci qui il tuo token se vuoi che sia fisso, 
# oppure usa la barra laterale per inserirlo live.
token = st.sidebar.text_input("Inserisci Token Pulseoid", type="password")

if not token:
    st.warning("Per favore, inserisci il tuo Token Pulseoid nella barra a sinistra.")
    st.stop()

# --- INIZIALIZZAZIONE DATI ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Orario', 'BPM'])

# --- LOGICA DI RECUPERO ---
def get_bpm(t):
    url = f"https://pulseoid.net/v1/api/get_actual_heart_rate?access_token={t}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()['heart_rate']
    except:
        return None
    return None

# --- LAYOUT DASHBOARD ---
col1, col2 = st.columns([1, 3])

with col1:
    metric_place = st.empty()
    st.write("---")
    # Tasto per scaricare i dati salvati finora
    if len(st.session_state.history) > 0:
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica dati CSV", data=csv, file_name="dati_moofit.csv", mime='text/csv')

with col2:
    chart_place = st.empty()

# --- LOOP INFINITO ---
while True:
    val = get_bpm(token)
    if val:
        now = datetime.now().strftime("%H:%M:%S")
        new_data = pd.DataFrame({'Orario': [now], 'BPM': [val]})
        st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
        
        # Mostra l'ultimo valore gigante
        metric_place.metric("Battito Attuale", f"{val} BPM")
        
        # Aggiorna il grafico (ultimi 100 punti)
        chart_place.line_chart(st.session_state.history.set_index('Orario').tail(100))
    
    time.sleep(1) # Aspetta 1 secondo
