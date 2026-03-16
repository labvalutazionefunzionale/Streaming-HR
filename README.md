# 📊 Moofit HRV Monitor 💓

![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

Questa applicazione web consente il monitoraggio in tempo reale della **Frequenza Cardiaca (HR)** e della **Variabilità Cardiaca (HRV)** utilizzando i dati provenienti da sensori **Moofit** tramite l'ecosistema **Pulsoid** e web app customizzata **Streamlit** 

---

## 🚀 Funzionalità principali

- **Streaming in tempo reale**: Connessione diretta con l'API di Pulsoid per dati HR ad alta frequenza
- **Analisi HRV esemplificativa**: 
  - Calcolo della metrica **RMSSD** (Root Mean Square of Successive Differences).
  - Finestra mobile di **30 secondi** per il monitoraggio live.
  - Report globale (Media BPM e RMSSD totale) al termine della sessione.
- **Report della sessione (Media BPM e RMSSD totale) allo STOP**
- **Grafica Interattiva**: Visualizzazione dinamica con linea di tendenza tramite libreria *Altair*
- **Esportazione Dati**: Download immediato della sessione in formato `.csv` per analisi successive
- **Scala Temporale Relativa**: Il grafico mostra il tempo trascorso dall'inizio della registrazione

---

## 🛠️ Requisiti Tecnici

L'app è sviluppata in **Python** e richiede le seguenti librerie (incluse in `requirements.txt`):
* `streamlit`: Framework per l'interfaccia web.
* `pandas` & `numpy`: Elaborazione dati e calcoli statistici.
* `altair`: Visualizzazione dati avanzata.
* `streamlit-autorefresh`: Gestione del refresh dinamico.

---

## 📖 Come iniziare

1. **Configurazione Pulsoid**:
   - Assicurati che il tuo Moofit sia collegato all'app Pulsoid sul telefono.
   - Ottieni il tuo **Access Token** dal sito [Pulsoid.net](https://pulsoid.net).
2. **Setup dell'App**:
   - Inserisci il token nel file `app.py`.
   - Carica i file su GitHub e collega il repository a **Streamlit Cloud**.
3. **Utilizzo**:
   - Clicca **START** per iniziare la registrazione.
   - Dopo 30 secondi apparirà il valore RMSSD live.
   - Clicca **STOP** per visualizzare il riepilogo finale e scaricare il CSV.

---

## 🔬 Note Metodologiche

### RMSSD (Root Mean Square of Successive Differences)
Il calcolo dell'HRV si basa sulla trasformazione dei BPM in intervalli **R-R (ms)**:
$$RR_{ms} = \frac{60000}{BPM}$$
L'RMSSD viene calcolato come la radice quadrata della media dei quadrati delle differenze tra battiti successivi. È la metrica gold-standard per valutare l'attività del sistema nervoso parasimpatico in finestre temporali brevi.

---

## 🎓 Crediti
**Sviluppato da:** Danilo Bondi  
**Affiliazioni:** * Università degli Studi "G. d'Annunzio" Chieti-Pescara (**UDA**)
* Università degli Studi dell'Aquila (**UnivAq**)

**AI Support:** Progettato con l'ausilio di Gemini (Google AI).

![Logo UDA](logo%20UDA.png)
![Logo UnivAq](Logo%20UnivAq.png)
