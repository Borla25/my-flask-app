# 🎵 Madness Festival - Web Application

Applicazione web per la gestione del festival musicale "Madness Festival" sviluppata con Flask, SQLite e tecnologie web moderne.

## 📋 Caratteristiche

### ✨ Funzionalità Principali

- **Gestione Utenti**: Registrazione e autenticazione con Flask-Login
- **Due tipi di utenti**: Partecipanti e Organizzatori
- **Gestione Performance**: Creazione, modifica e pubblicazione di performance musicali
- **Sistema Biglietti**: Acquisto di biglietti con diverse tipologie e controllo disponibilità
- **Filtri Avanzati**: Ricerca per giorno, palco e genere musicale
- **Design Responsivo**: Compatibile con desktop, tablet e mobile
- **Upload Immagini**: Gestione immagini obbligatorie per performance

### 🎫 Tipi di Biglietti

- **Giornaliero**: €50 (valido per un giorno specifico)
- **Pass 2 Giorni**: €90 (due giorni consecutivi con sconto €10)
- **Full Pass**: €130 (tutti e tre i giorni con sconto €20)

### 🎤 Palchi Disponibili

- Main Stage (Capacità: 1000)
- Secondary Stage (Capacità: 500)
- Experimental Stage (Capacità: 200)

## 👥 Credenziali di Test

L'applicazione include account preconfigurati per il testing:

### 🎼 Organizzatori

- **Email**: `marco.rossi@email.com` | **Password**: `password123`
- **Email**: `giulia.verdi@email.com` | **Password**: `password123`

### 🎫 Partecipanti  

- **Email**: `luca.bianchi@email.com` | **Password**: `password123`
- **Email**: `sara.ferrari@email.com` | **Password**: `password123`
- **Email**: `andrea.neri@email.com` | **Password**: `password123`

## 📁 Struttura del Progetto

```
FestivalBrainrot/
├── app.py                 # Applicazione Flask principale
├── models.py             # Modelli dati (User)
├── users_dao.py          # Gestione dati utenti
├── performances_dao.py   # Gestione dati performance  
├── tickets_dao.py        # Gestione dati biglietti
├── stages_dao.py         # Gestione dati palchi
├── db/
│   ├── festival.db       # Database SQLite
├── static/
│   ├── style.css         # Stili personalizzati
│   └── uploads/          # Immagini performance caricate
└── templates/
    ├── base.html                # Template base
    ├── home.html                # Homepage con filtri
    ├── register.html            # Registrazione
    ├── edit_performance.html    # Modifica bozza performance
    ├── buy_ticket.html          # Acquisto biglietti
    ├── profile_participant.html # Profilo partecipante
    ├── profile_organizer.html   # Profilo organizzatore
    ├── new_performance.html     # Nuova performance
    └── performance_detail.html  # Dettagli performance
```

## 🎯 Istruzioni per Testare l'Applicazione

### 🎫 Come Partecipante

1. **Registrati** come "Partecipante"
2. **Esplora** le performance pubblicate nella homepage
3. **Usa i filtri** per trovare performance per:
   - Giorno (Venerdì 12, Sabato 13, Domenica 14 Luglio)
   - Palco (Main Stage, Secondary Stage, Experimental Stage)
   - Genere (Rock, Pop, Jazz, Electronic, Folk, Hip-Hop, Classical, Blues)
4. **Clicca** su una performance per vedere i dettagli
5. **Vai su "Biglietti"** nel menu per acquistare
6. **Scegli** il tipo di biglietto (attenzione alle regole):
   - Non puoi comprare più biglietti se hai già un pass multi-giorno
   - Non puoi comprare pass multi-giorno se hai biglietti giornalieri
   - Non puoi comprare per giorni già coperti
7. **Controlla** i tuoi biglietti nel "Profilo"

### 🎼 Come Organizzatore

1. **Accedi** con account test: `marco.rossi@email.com`
2. **Dashboard Organizzatore**: Vedi statistiche vendite e tue performance
3. **Crea Performance**:
   - Clicca "Nuova Performance"
   - **IMPORTANTE**: L'immagine è obbligatoria per la pubblicazione
   - Compila tutti i campi (artista, giorno, orario, durata, palco, genere)
   - La performance viene salvata come BOZZA
4. **Gestisci Performance**:
   - **Modifica**: Solo bozze non pubblicate
   - **Pubblica**: Controllo automatico conflitti orari/palco
   - **Elimina**: Solo bozze non pubblicate
5. **Vedi Statistiche**: Vendite totali, per tipo biglietto, per giorno

## 🔧 Funzionalità da Testare

### ✅ Validazioni Automatiche

- **Conflitti Orari**: Prova a pubblicare due performance stesso palco/orario
- **Artista Unico**: Ogni artista può avere solo una performance
- **Capacità Giornaliera**: Massimo 200 partecipanti per giorno
- **Regole Biglietti**: Sistema previene acquisti non validi

### ✅ Upload Immagini

- **Performance**: Obbligatoria per pubblicazione (JPG, PNG, GIF, WebP)
- **Validazione**: Formato e dimensioni controllate

### ✅ Responsive Design

- **Desktop**: Layout a 3 colonne per performance
- **Tablet**: Layout a 2 colonne  
- **Mobile**: Layout a 1 colonna con menu hamburger

## 🎨 Design e UX

### 🎨 Palette Colori Festival

- **Gradiente Header**: Dal viola al blu per atmosfera festival
- **Card Performance**: Ombre moderne con bordi arrotondati
- **Biglietti**: Colori distintivi per ogni tipologia
- **Badge**: Colori semantici per palchi, giorni, generi

### ✨ Caratteristiche UX

- **Feedback Immediato**: Messaggi flash per ogni azione
- **Stati Interattivi**: Hover e focus visibili
- **Loading States**: Indicatori durante operazioni
- **Validazione Real-time**: Controlli istantanei sui form

## 📅 Date Festival

**Madness Festival 2025**

- **📍 Luogo**: Colle Tung Tung, Torino
- **📅 Date**: 12-14 Luglio 2025
- **🎫 Capacità**: 200 partecipanti/giorno

## 🚀 Deploy

🌐 **L'applicazione è visibile online all'indirizzo:**

```
https://borla25.pythonanywhere.com/
```

## 📊 Dati di Test Inclusi

Il database include:

- **5 utenti** (2 organizzatori, 3 partecipanti)
- **18 performance** distribuite nei 3 giorni del festival
- **3 bozze** per testare pubblicazione/modifica
- **Biglietti acquistati** di diverse tipologie
- **3 palchi** con capacità diverse
