# 🌱 Diario del Pollice Verde

Una bellissima web app per monitorare e imparare a curare le tue piante, costruita con Flask e SQLite.

## ✨ Funzionalità

- **La Mia Serra**: Dashboard con l'elenco delle tue piante e miniature.
- **Scheda Cura**: Dettagli su irrigazione e cronologia.
- **Pulsante "Annaffiata oggi!"**: Aggiorna la data di ultima irrigazione con un click.
- **Diario Visivo**: Aggiungi note e carica foto per ogni pianta.
- **Timeline della Crescita**: Visualizza cronologicamente i cambiamenti delle tue piante.

## 🛠️ Requisiti Tecnici

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Pillow (per la gestione delle immagini)

## 🚀 Come Eseguire l'App

1. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Avvia l'applicazione**:
   ```bash
   python app.py
   ```

3. **Apri nel browser**:
   Vai su `http://127.0.0.1:5001`

## 📂 Struttura del Progetto

- `app.py`: Logica principale e rotte.
- `models.py`: Modelli del database (Pianta e Nota).
- `templates/`: File HTML con Tailwind CSS.
- `static/uploads/`: Cartella locale dove vengono salvate le foto caricate.
- `instance/plants.db`: Database SQLite (creato automaticamente all'avvio).

## 🎨 Design

L'interfaccia usa una palette ispirata alla natura:
- **Verde Salvia**: Per gli elementi principali e i pulsanti.
- **Toni del Legno**: Per i richiami materici.
- **Bianco Panna**: Per uno sfondo pulito e riposante.
