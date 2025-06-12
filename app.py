from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datetime import date, datetime, timedelta
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 # Added for check_database
from PIL import Image

import performances_dao, users_dao, tickets_dao
from models import User
import stages_dao

# Constants
PERFORMANCE_IMG_WIDTH = 400
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Festival configuration
FESTIVAL_NAME = "Madness Festival"
FESTIVAL_LOCATION = "Colle Tung Tung, Torino"
FESTIVAL_DATES = {
    'venerdi': date(2025, 7, 12),    # ← 2025 invece di 2024
    'sabato': date(2025, 7, 13),     # ← 2025 invece di 2024
    'domenica': date(2025, 7, 14)    # ← 2025 invece di 2024
}
MAX_DAILY_CAPACITY = 200
GENRES = ["Rock", "Pop", "Jazz", "Electronic", "Folk", "Hip-Hop", "Classical", "Blues"]

# Create the application
app = Flask(__name__)
app.config["SECRET_KEY"] = "HarmonyValleyFestival2025SecretKey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, prefix, max_width=None, min_height=None, max_height=None):
    """Save and resize uploaded image - CON VALIDAZIONE ALTEZZA E PROPORZIONI"""
    if file and allowed_file(file.filename):
        filename = file.filename
        timestamp = int(datetime.now().timestamp())
        new_filename = f"{prefix}_{timestamp}.webp"
        
        img = Image.open(file)
        
        # ✅ NUOVO: Controlla altezza minima
        if min_height and img.height < min_height:
            return None, f"L'immagine deve essere alta almeno {min_height}px (attuale: {img.height}px)"
        
        # ✅ NUOVO: Controlla altezza massima
        if max_height and img.height > max_height:
            return None, f"L'immagine non può essere più alta di {max_height}px (attuale: {img.height}px)"
        
        # ✅ NUOVO: Controlla proporzioni (formato panoramico)
        aspect_ratio = img.width / img.height
        if aspect_ratio < 0.8:  # Troppo verticale
            return None, f"L'immagine è troppo stretta (proporzioni {aspect_ratio:.2f}). Usa un formato più panoramico."
        
        # Ridimensiona sempre per web
        if max_width and img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            
            # ✅ NUOVO: Controlla che dopo il resize sia ancora valida
            if min_height and new_height < min_height:
                return None, f"Dopo il ridimensionamento l'immagine sarebbe troppo bassa ({new_height}px < {min_height}px)"
            
            if max_height and new_height > max_height:
                return None, f"Dopo il ridimensionamento l'immagine sarebbe troppo alta ({new_height}px > {max_height}px)"
            
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        filepath = f"{app.config['UPLOAD_FOLDER']}/{new_filename}"
        img.save(filepath, "WebP", quality=60, optimize=True)
        
        return new_filename, None
    
    return None, "File non valido"

def validate_performance_timing(stage, day, start_time, duration, exclude_id=None):
    """Validate that a performance doesn't conflict with existing ones"""
    try:
        # Controlla che l'orario di inizio sia valido
        start_dt = datetime.strptime(start_time, "%H:%M")
        
        # Controlla che la durata sia ragionevole (30-180 minuti)
        duration_int = int(duration)
        if duration_int < 30 or duration_int > 180:
            return False, "La durata deve essere tra 30 e 180 minuti"
        
        # Controlla conflitti con altre performance
        if exclude_id:
            has_conflict = performances_dao.check_conflict_exclude(stage, day, start_time, duration_int, exclude_id)
        else:
            has_conflict = performances_dao.check_conflict(stage, day, start_time, duration_int)
        
        if has_conflict:
            return False, f"Conflitto di orario sul palco {stage} il {day}"  # ← Aggiunto f-string
        
        return True, "OK"
        
    except ValueError:
        return False, "Formato orario non valido"

# Routes
@app.route("/")
def home():
    """Homepage with published performances - OTTIMIZZATA"""
    day_filter = request.args.get('day', '')
    stage_filter = request.args.get('stage', '')
    genre_filter = request.args.get('genre', '')
    
    # PERFORMANCE: ottieni solo performances pubblicate
    performances = performances_dao.get_published_performances(day_filter, stage_filter, genre_filter)
    
    # PERFORMANCE: ottieni stages solo se necessario
    stages = stages_dao.get_all_stages() if not stage_filter else []
    
    return render_template("home.html", 
                         performances=performances,
                         genres=GENRES,  # Costante, non query
                         stages=stages,
                         festival_name=FESTIVAL_NAME,  # Costante
                         festival_location=FESTIVAL_LOCATION)  # Costante

@app.route("/performance/<int:id>")
def performance_detail(id):
    """Single performance detail page"""
    performance = performances_dao.get_performance(id)
    if not performance or (not performance['published'] and 
                          (not current_user.is_authenticated or current_user.user_type != 'organizer')):
        abort(404)
    
    return render_template("performance_detail.html",
                           performance=performance,
                           festival_name=FESTIVAL_NAME,
                           festival_location=FESTIVAL_LOCATION)

@app.route("/register")
def register():
    """Registration page"""
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    """Handle user registration"""
    form_data = request.form.to_dict()
    
    if not all([form_data.get('email'), form_data.get('password'), 
                form_data.get('full_name'), form_data.get('user_type')]):
        flash("Tutti i campi sono obbligatori", "danger")
        return redirect(url_for("register"))
    
    if form_data.get('user_type') not in ['participant', 'organizer']:
        flash("Tipo utente non valido", "danger")
        return redirect(url_for("register"))
    
    existing_user = users_dao.get_user_by_email(form_data['email'])
    if existing_user:
        flash("Esiste già un utente con questa email", "danger")
        return redirect(url_for("register"))
    
    form_data['password'] = generate_password_hash(form_data['password'])
    
    success = users_dao.add_user(form_data)
    
    if success:
        flash("Registrazione completata con successo!", "success")
        return redirect(url_for("home"))
    else:
        flash("Errore durante la registrazione", "danger")
        return redirect(url_for("register"))

@app.route("/login", methods=["POST"])
def login():
    """Handle user login"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    user_db = users_dao.get_user_by_email(email)
    
    if not user_db or not check_password_hash(user_db['password'], password):
        flash("Credenziali non valide", "danger")
        return redirect(url_for("home"))
    
    user = User(
        id=user_db['id'],
        email=user_db['email'],
        full_name=user_db['full_name'],
        user_type=user_db['user_type'],
        profile_image=None
    )
    login_user(user)
    flash(f"Benvenuto/a {user_db['full_name']}!", "success")
    
    return redirect(url_for("profile"))

@app.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash("Logout effettuato con successo", "info")
    return redirect(url_for("home"))

@app.route("/profile")
@login_required
def profile():
    if current_user.user_type == 'participant':
        tickets = tickets_dao.get_user_tickets(current_user.id)
        return render_template("profile_participant.html", tickets=tickets)
    
    elif current_user.user_type == 'organizer':
        performances = performances_dao.get_organizer_performances(current_user.id)
        
        # ← CAMBIA: Statistiche generali del festival, non per organizzatore
        stats = tickets_dao.get_festival_stats()  # Nuova funzione
        
        return render_template("profile_organizer.html", 
                             performances=performances, 
                             stats=stats)
    else:
        flash("Tipo di utente non riconosciuto", "danger")
        return redirect(url_for("home"))

@app.route("/buy_ticket")
@login_required
def buy_ticket():
    if current_user.user_type != 'participant':
        flash("Solo i partecipanti possono acquistare biglietti", "danger")
        return redirect(url_for("home"))
    
    availability = tickets_dao.get_daily_availability()
    covered_days = tickets_dao.get_user_covered_days(current_user.id)
    existing_tickets = tickets_dao.get_user_tickets(current_user.id)
    has_multi_day = any(ticket['ticket_type'] in ['2days', 'full'] for ticket in existing_tickets)
    
    # ✅ AGGIUNGI: Dati dal controller invece che template
    ticket_types = [
        {
            'id': 'daily',          # ✅ Deve corrispondere all'input radio
            'value': 'daily', 
            'title': 'Biglietto Giornaliero',
            'description': 'Valido per un solo giorno',
            'price': 50,
            'disabled': has_multi_day,
            'disabled_reason': 'Hai già un pass multi-giorno'
        },
        {
            'id': 'twodays',        # ✅ Deve corrispondere all'input radio
            'value': '2days',
            'title': 'Pass 2 Giorni', 
            'description': 'Valido per due giorni consecutivi',
            'price': 90,
            'discount': 10,
            'disabled': existing_tickets,
            'disabled_reason': 'Hai già altri biglietti'
        },
        {
            'id': 'full',           # ✅ Deve corrispondere all'input radio
            'value': 'full',
            'title': 'Full Pass',
            'description': 'Valido per tutti e tre i giorni', 
            'price': 130,
            'discount': 20,
            'disabled': existing_tickets,
            'disabled_reason': 'Hai già altri biglietti'
        }
    ]
    
    # ✅ AGGIUNGI: Giorni del festival dal controller
    festival_days = [
        {
            'value': 'venerdi',
            'label': 'Venerdì 12 Luglio',
            'id_prefix': 'venerdi',
            'date': FESTIVAL_DATES['venerdi']
        },
        {
            'value': 'sabato', 
            'label': 'Sabato 13 Luglio',
            'id_prefix': 'sabato',
            'date': FESTIVAL_DATES['sabato']
        },
        {
            'value': 'domenica',
            'label': 'Domenica 14 Luglio', 
            'id_prefix': 'domenica',
            'date': FESTIVAL_DATES['domenica']
        }
    ]
    
    return render_template("buy_ticket.html", 
                         availability=availability,
                         covered_days=covered_days,
                         existing_tickets=existing_tickets,
                         has_multi_day=has_multi_day,
                         ticket_types=ticket_types,      # ✅ NUOVO
                         festival_days=festival_days)    # ✅ NUOVO

@app.route("/buy_ticket", methods=["POST"])
@login_required
def buy_ticket_post():
    if current_user.user_type != 'participant':
        flash("Solo i partecipanti possono acquistare biglietti", "danger")
        return redirect(url_for("home"))
    
    ticket_type = request.form.get('ticket_type')
    selected_days = request.form.getlist('days')
    
    # ← AGGIUNGI: Validazione specifica per tipo biglietto
    if ticket_type == 'daily':
        # Per biglietto giornaliero: esattamente 1 giorno da 'single_day'
        single_day = request.form.get('single_day')
        if not single_day:
            flash("Devi selezionare esattamente 1 giorno per il biglietto giornaliero", "danger")
            return redirect(url_for("buy_ticket"))
        selected_days = [single_day]  # Override con selezione singola
        
    elif ticket_type == '2days':
        if len(selected_days) != 2:
            flash(f"Devi selezionare esattamente 2 giorni per il Pass 2 Giorni, hai selezionato {len(selected_days)} giorni", "danger")
            return redirect(url_for("buy_ticket"))
            
    elif ticket_type == 'full':
        # Full pass: tutti i giorni automatici
        selected_days = ['venerdi', 'sabato', 'domenica']
    
    if not ticket_type:
        flash("Devi selezionare un tipo di biglietto", "danger")
        return redirect(url_for("buy_ticket"))
    
    availability_result = tickets_dao.check_availability(ticket_type, selected_days)
    if not availability_result:
        flash("Biglietti non disponibili per le date selezionate", "danger")
        return redirect(url_for("buy_ticket"))
    
    can_purchase, message = tickets_dao.can_purchase_ticket(current_user.id, ticket_type, selected_days)
    
    if not can_purchase:
        flash(message, "danger")
        return redirect(url_for("buy_ticket"))
    
    # Gestisci i giorni per Full Pass
    if ticket_type == 'full':
        days_string = 'venerdi,sabato,domenica'
    elif ticket_type in ['daily', '2days']:
        if not selected_days:
            flash("Devi selezionare almeno un giorno", "danger")
            return redirect(url_for("buy_ticket"))
        days_string = ','.join(selected_days)
    else:
        days_string = ''
    
    prices = {'daily': 50.0, '2days': 90.0, 'full': 130.0}  # Float invece di int
    price = float(prices[ticket_type])  # Assicurati che sia float
    
    ticket_data = {
        'user_id': current_user.id,
        'ticket_type': ticket_type,
        'days': days_string,
        'price': price,
        'purchase_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    success = tickets_dao.add_ticket(ticket_data)
    
    if success:
        flash("Biglietto acquistato con successo!", "success")
        return redirect(url_for("profile"))
    else:
        flash("Errore durante l'acquisto del biglietto", "danger")
        return redirect(url_for("buy_ticket"))

@app.route("/new_performance")
@login_required
def new_performance():
    """New performance creation page"""
    if current_user.user_type != 'organizer':
        flash("Solo gli organizzatori possono creare performance", "danger")
        return redirect(url_for("home"))
    
    return render_template("new_performance.html", 
                         genres=GENRES, 
                         stages=stages_dao.get_all_stages())

@app.route("/new_performance", methods=["POST"])
@login_required
def new_performance_post():
    """Handle new performance creation"""
    if current_user.user_type != 'organizer':
        flash("Solo gli organizzatori possono creare performance", "danger")
        return redirect(url_for("home"))
    
    form_data = request.form.to_dict()
    
    # Converti la data nel nome del giorno
    date_to_day = {
        '2025-07-12': 'venerdi',    # ← 2025 invece di 2024
        '2025-07-13': 'sabato',     # ← 2025 invece di 2024
        '2025-07-14': 'domenica'    # ← 2025 invece di 2024
    }
    
    if form_data.get('day') in date_to_day:
        form_data['day'] = date_to_day[form_data['day']]
    
    required_fields = ['artist_name', 'day', 'start_time', 'duration', 
                      'description', 'stage', 'genre']
    if not all(form_data.get(field) for field in required_fields):
        flash("Tutti i campi sono obbligatori", "danger")
        return redirect(url_for("new_performance"))
    
    stage_name = form_data.get('stage')
    stage = stages_dao.get_stage_by_name(stage_name)
    if not stage:
        flash('Palco non valido.', 'error')
        return redirect(url_for('new_performance'))
    
    stage_id = stage['id']
    
    if performances_dao.check_conflict(stage_id, form_data['day'], 
                                     form_data['start_time'], int(form_data['duration'])):
        flash("Conflitto: esiste già una performance PUBBLICATA nello stesso palco e orario", "danger")
        return redirect(url_for("new_performance"))
    
    if performances_dao.artist_exists(form_data['artist_name']):
        flash("Questo artista ha già una performance programmata", "danger")
        return redirect(url_for("new_performance"))
    
    performance_image = request.files.get('performance_image')
    if performance_image:
        # ✅ NUOVO: Aggiungi validazione altezza minima 600px
        result = save_image(performance_image, f"perf_{form_data['artist_name']}", 
                       PERFORMANCE_IMG_WIDTH, min_height=600)
    
        if isinstance(result, tuple):  # ✅ NUOVO: Gestisci errore
            image_filename, error_message = result
            if error_message:
                flash(f"Errore immagine: {error_message}", "danger")
                return redirect(url_for("new_performance"))
            form_data['performance_image'] = image_filename
        else:
            form_data['performance_image'] = result  # Backward compatibility
    else:
        form_data['performance_image'] = None
    
    form_data['organizer_id'] = current_user.id
    form_data['published'] = False
    form_data['stage_id'] = stage_id 
    
    success = performances_dao.add_performance(form_data)
    
    if success:
        flash("Performance creata con successo!", "success")
        return redirect(url_for("profile"))
    else:
        flash("Errore durante la creazione della performance", "danger")
        return redirect(url_for("new_performance"))

@app.route("/edit_performance/<int:id>")
@login_required
def edit_performance(id):
    """Edit performance page"""
    if current_user.user_type != 'organizer':
        flash("Solo gli organizzatori possono modificare le performance", "danger")
        return redirect(url_for("home"))
    
    performance = performances_dao.get_performance(id)
    if not performance or performance['organizer_id'] != current_user.id:
        abort(404)
    
    if performance['published']:
        flash("Non puoi modificare una performance già pubblicata", "warning")
        return redirect(url_for("profile"))
    
    return render_template("edit_performance.html", 
                         performance=performance,
                         genres=GENRES,
                         stages=stages_dao.get_all_stages(),
                         festival_dates=FESTIVAL_DATES)

@app.route("/edit_performance/<int:id>", methods=["POST"])
@login_required
def edit_performance_post(id):
    """Handle performance editing"""
    if current_user.user_type != 'organizer':
        flash("Solo gli organizzatori possono modificare le performance", "danger")
        return redirect(url_for("home"))
    
    performance = performances_dao.get_performance(id)
    if not performance or performance['organizer_id'] != current_user.id or performance['published']:
        abort(403)
    
    form_data = request.form.to_dict()
    form_data['id'] = id
    
    stage_name = form_data.get('stage')
    stage = stages_dao.get_stage_by_name(stage_name)
    if not stage:
        flash('Palco non valido.', 'error')
        return redirect(url_for('edit_performance', id=id))
    
    stage_id = stage['id']
    form_data['stage_id'] = stage_id

    if performances_dao.check_conflict_exclude(stage_id, form_data['day'], 
                                             form_data['start_time'], int(form_data['duration']), id):
        flash("Conflitto: esiste già una performance nello stesso palco e orario", "danger")
        return redirect(url_for("edit_performance", id=id))
    
    performance_image = request.files.get('performance_image')
    if performance_image:
        # ✅ NUOVO: Validazione completa con min/max altezza
        result = save_image(performance_image, f"perf_{form_data['artist_name']}", 
                       PERFORMANCE_IMG_WIDTH, 
                       min_height=400,     # Min 400px (come le immagini a destra)
                       max_height=800)     # Max 800px (evita immagini troppo lunghe)
    
        if isinstance(result, tuple):
            image_filename, error_message = result
            if error_message:
                flash(f"Errore immagine: {error_message}", "danger")
                return redirect(url_for("edit_performance", id=id))
            form_data['performance_image'] = image_filename
    
    success = performances_dao.update_performance(form_data)
    
    if success:
        flash("Performance aggiornata con successo!", "success")
        return redirect(url_for("profile"))
    else:
        flash("Errore durante l'aggiornamento", "danger")
        return redirect(url_for("edit_performance", id=id))

@app.route('/publish_performance/<int:performance_id>', methods=['POST'])
@login_required
def publish_performance_route(performance_id):
    if current_user.user_type != 'organizer':
        flash('Solo gli organizzatori possono pubblicare performance.', 'error')
        return redirect(url_for('home'))
    
    performance = performances_dao.get_performance(performance_id)  
    if not performance or performance['organizer_id'] != current_user.id:
        flash('Performance non trovata o non autorizzato.', 'error')
        return redirect(url_for('profile'))
    
    if performances_dao.publish_performance(performance_id):  
        flash(f'Performance "{performance["artist_name"]}" pubblicata con successo!', 'success')
    else:
        flash('Impossibile pubblicare: conflitto di orario con performance già pubblicata.', 'error')
    
    return redirect(url_for('profile'))

@app.route("/delete_performance/<int:id>", methods=["POST"])
@login_required
def delete_performance_route(id):
    """Delete unpublished performance"""
    if current_user.user_type != 'organizer':
        flash("Solo gli organizzatori possono eliminare performance", "danger")
        return redirect(url_for("home"))
    
    performance = performances_dao.get_performance(id)
    if not performance or performance['organizer_id'] != current_user.id:
        abort(404)
    
    if performance['published']:
        flash("Non puoi eliminare una performance già pubblicata", "warning")
        return redirect(url_for("profile"))
    
    success = performances_dao.delete_performance(id)
    
    if success:
        flash("Performance eliminata con successo!", "success")
    else:
        flash("Errore durante l'eliminazione", "danger")
    
    return redirect(url_for("profile"))

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    db_user = users_dao.get_user_by_id(user_id)
    if db_user:
        return User(
            id=db_user['id'],
            email=db_user['email'],
            full_name=db_user['full_name'],
            user_type=db_user['user_type'],
            profile_image=db_user['profile_image'] if 'profile_image' in db_user else None  # ← Cambiato
        )
    return None

if __name__ == "__main__":    
    app.run(host="0.0.0.0", port=3000, debug=True)