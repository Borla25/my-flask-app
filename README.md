# 🎵 Harmony Valley Festival - Web Application

Applicazione web per la gestione del festival musicale "Harmony Valley" sviluppata con Flask, SQLite e tecnologie web moderne.

## 📋 Caratteristiche

### ✨ Funzionalità Principali
- **Gestione Utenti**: Registrazione e autenticazione con Flask-Login
- **Due tipi di utenti**: Partecipanti e Organizzatori
- **Gestione Performance**: Creazione, modifica e pubblicazione di performance musicali
- **Sistema Biglietti**: Acquisto di biglietti con diverse tipologie
- **Filtri Avanzati**: Ricerca per giorno, palco e genere musicale
- **Design Responsivo**: Compatibile con desktop, tablet e mobile
- **Upload Immagini**: Gestione immagini per profili e performance

### 🎫 Tipi di Biglietti
- **Giornaliero**: €50 (valido per un giorno)
- **Pass 2 Giorni**: €85 (due giorni consecutivi)
- **Full Pass**: €120 (tutti e tre i giorni)

### 🎤 Palchi Disponibili
- Main Stage
- Secondary Stage
- Experimental Stage

## 🛠 Installazione

### Prerequisiti
- Python 3.8+
- pip (package manager Python)

### Setup
1. **Clona o scarica il progetto**
   ```bash
   # Se hai git
   git clone <repository-url>
   cd harmony-valley-festival
   ```

2. **Crea ambiente virtuale (raccomandato)**
   ```bash
   python -m venv venv
   
   # Su Windows
   venv\Scripts\activate
   
   # Su macOS/Linux
   source venv/bin/activate
   ```

3. **Installa dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Avvia l'applicazione**
   ```bash
   python run.py
   ```

5. **Apri il browser**
   ```
   http://localhost:3000
   ```

## 👥 Account di Test

L'applicazione include account preconfigurati per il testing:

### Organizzatori
- **Email**: marco.rossi@email.com | **Password**: password123
- **Email**: giulia.verdi@email.com | **Password**: password123

### Partecipanti
- **Email**: luca.bianchi@email.com | **Password**: password123
- **Email**: sara.ferrari@email.com | **Password**: password123
- **Email**: andrea.neri@email.com | **Password**: password123

## 📁 Struttura del Progetto

```
harmony-valley-festival/
├── app.py                 # Applicazione Flask principale
├── models.py             # Modelli dati (User)
├── users_dao.py          # Gestione dati utenti
├── performances_dao.py   # Gestione dati performance
├── tickets_dao.py        # Gestione dati biglietti
├── init_db.py           # Inizializzazione database
├── run.py               # Script di avvio
├── requirements.txt     # Dipendenze Python
├── README.md           # Questo file
├── db/
│   ├── init_db.sql     # Schema database
│   └── festival.db     # Database SQLite (creato automaticamente)
├── static/
│   ├── css/
│   │   └── custom.css  # Stili personalizzati
│   └── uploads/        # Immagini caricate (creata automaticamente)
└── templates/
    ├── base.html              # Template base
    ├── home.html              # Homepage
    ├── register.html          # Registrazione
    ├── performance_detail.html # Dettaglio performance
    ├── buy_ticket.html        # Acquisto biglietti
    ├── profile_participant.html # Profilo partecipante
    ├── profile_organizer.html   # Profilo organizzatore
    ├── new_performance.html     # Nuova performance
    └── edit_performance.html    # Modifica performance
```

## 🎯 Utilizzo

### Per i Partecipanti
1. **Registrati** come "Partecipante"
2. **Esplora** le performance pubblicate
3. **Filtra** per giorno, palco o genere
4. **Acquista** il tuo biglietto
5. **Visualizza** i tuoi biglietti nel profilo

### Per gli Organizzatori
1. **Registrati** come "Organizzatore"
2. **Crea** nuove performance (salvate come bozze)
3. **Modifica** le performance non ancora pubblicate
4. **Pubblica** le performance (non più modificabili)
5. **Monitora** le statistiche di vendita

## 🔧 Funzionalità Tecniche

### Validazioni
- **Frontend**: Validazione HTML5 e controlli JavaScript
- **Backend**: Validazione server-side per tutti i form
- **Conflitti**: Controllo automatico sovrapposizioni orari/palchi
- **Unicità**: Un artista per festival, un biglietto per partecipante

### Sicurezza
- **Password**: Hash con Werkzeug
- **File Upload**: Validazione tipi file e nomi sicuri
- **SQL Injection**: Protezione con query parametrizzate
- **Session Management**: Flask-Login per gestione sessioni

### Responsive Design
- **Bootstrap 5**: Framework CSS moderno
- **Mobile First**: Design ottimizzato per tutti i dispositivi
- **Icone**: Font Awesome per icone vettoriali
- **Tema Personalizzato**: Colori e stili del festival

## 🎨 Design e UX

### Palette Colori
- **Primario**: #8B4513 (Marrone Festival)
- **Secondario**: #DEB887 (Beige Armonia)
- **Accent**: #CD853F (Oro Antico)
- **Testo**: #2F4F4F (Grigio Ardesia)

### Caratteristiche UX
- **Navigazione Intuitiva**: Menu chiaro e breadcrumb
- **Feedback Visivo**: Messaggi flash per ogni azione
- **Loading States**: Indicatori di caricamento
- **Animazioni Fluide**: Transizioni CSS per miglior UX

## 📱 Compatibilità

- **Browser**: Chrome 111+, Firefox 110+
- **Dispositivi**: Desktop, Tablet, Mobile
- **Risoluzione**: Responsive da 320px a 1920px+

## 🚀 Deploy su PythonAnywhere

1. **Carica** i file del progetto
2. **Installa** le dipendenze nel console
3. **Configura** WSGI file:
   ```python
   import sys
   path = '/home/yourusername/harmony-valley-festival'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
4. **Configura** static files mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/harmony-valley-festival/static/`

## 📈 Dati di Test Inclusi

L'applicazione include:
- **5 utenti** (2 organizzatori, 3 partecipanti)
- **15+ performance** distribuite nei 3 giorni
- **1 performance non pubblicata** per testing
- **3 biglietti acquistati** di tipologie diverse
- **Immagini placeholder** per le performance

## 🛟 Supporto

Per problemi o domande:
1. Verifica i **log della console** per errori
2. Controlla che tutte le **dipendenze siano installate**
3. Assicurati che la **porta 3000 sia libera**
4. Verifica i **permessi di scrittura** per upload e database

---

**Sviluppato per il corso IAW 2024** 🎓
**Festival Location**: Valle Armonia, Torino 🏔️
**Date Festival**: 12-14 Luglio 2024 📅