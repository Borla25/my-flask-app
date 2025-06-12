import sqlite3
from datetime import datetime, timedelta

def get_published_performances(day_filter='', stage_filter='', genre_filter=''):
    """Recupera performance pubblicate con filtri opzionali."""
    
    # Query con JOIN ottimizzato per performance
    query = '''SELECT p.id, p.artist_name, p.description, p.day, p.start_time, 
                      p.duration, p.genre, p.performance_image, s.name as stage_name
               FROM performances p 
               JOIN stages s ON p.stage_id = s.id
               WHERE p.published = 1'''
    params = []
    
    # Costruzione dinamica con prepared statements
    if day_filter:
        query += ' AND p.day = ?'
        params.append(day_filter)
    
    if stage_filter:
        query += ' AND s.name = ?'
        params.append(stage_filter)
    
    if genre_filter:
        query += ' AND p.genre = ?'
        params.append(genre_filter)
    
    # Ordinamento cronologico con limite per performance
    query += ''' ORDER BY p.day ASC, p.start_time ASC LIMIT 50'''
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    performances = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return performances

def get_performance(performance_id):
    """Recupera singola performance con dati organizzatore."""
    sql = '''SELECT p.*, u.full_name as organizer_name 
             FROM performances p 
             JOIN users u ON p.organizer_id = u.id 
             WHERE p.id = ?'''
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (performance_id,))
    
    performance = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return performance

def get_organizer_performances(organizer_id):
    """Recupera performance di un organizzatore. Bozze prima, poi cronologico."""
    sql = '''SELECT p.*, s.name as stage_name 
             FROM performances p 
             JOIN stages s ON p.stage_id = s.id 
             WHERE p.organizer_id = ?
             ORDER BY 
                p.published ASC,    -- Bozze prima (0 < 1)
                p.day ASC,
                p.start_time ASC'''
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (organizer_id,))
    
    performances = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return performances

def add_performance(performance_data):
    """Inserisce nuova performance. Normalizza i giorni in formato ISO."""
    sql = '''INSERT INTO performances 
             (artist_name, day, start_time, duration, description, stage_id, genre, 
              performance_image, organizer_id, published)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    
    day = performance_data['day']
    
    # Normalizzazione formato data
    day_mapping = {
        'venerdi': '2025-07-12',    
        'sabato': '2025-07-13',    
        'domenica': '2025-07-14'    
    }
    
    if day in day_mapping:
        day = day_mapping[day]
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (performance_data['artist_name'], day,  
                           performance_data['start_time'], performance_data['duration'],
                           performance_data['description'], performance_data['stage_id'],
                           performance_data['genre'], performance_data.get('performance_image', ''),
                           performance_data['organizer_id'], performance_data['published']))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def update_performance(performance_data):
    """Aggiorna performance. Due query: con/senza immagine per ottimizzare."""
    day = performance_data['day']
    
    # Stessa normalizzazione di add_performance
    day_mapping = {
        'venerdi': '2025-07-12',   
        'sabato': '2025-07-13',    
        'domenica': '2025-07-14'   
    }
    
    if day in day_mapping:
        day = day_mapping[day]
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        # Query condizionale per gestione immagine
        if 'performance_image' in performance_data and performance_data['performance_image']:
            sql = '''UPDATE performances SET 
                     artist_name=?, day=?, start_time=?, duration=?, description=?, 
                     stage_id=?, genre=?, performance_image=?
                     WHERE id=?'''
            cursor.execute(sql, (performance_data['artist_name'], day,
                               performance_data['start_time'], performance_data['duration'],
                               performance_data['description'], performance_data['stage_id'],
                               performance_data['genre'], performance_data['performance_image'],
                               performance_data['id']))
        else:
            # Preserva immagine esistente
            sql = '''UPDATE performances SET 
                     artist_name=?, day=?, start_time=?, duration=?, description=?, 
                     stage_id=?, genre=?
                     WHERE id=?'''
            cursor.execute(sql, (performance_data['artist_name'], day,
                               performance_data['start_time'], performance_data['duration'],
                               performance_data['description'], performance_data['stage_id'],
                               performance_data['genre'], performance_data['id']))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def publish_performance(performance_id):
    """Pubblica performance dopo controllo conflitti orari."""
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Recupera dati per controllo conflitti
        sql = '''SELECT day, start_time, duration, stage_id, artist_name
                 FROM performances 
                 WHERE id = ? AND published = 0'''
        cursor.execute(sql, (performance_id,))
        performance = cursor.fetchone()
        
        if not performance:
            return False
        
        day, start_time, duration, stage_id, artist_name = performance
        
        # Verifica conflitti con performance pubblicate
        if check_conflict(stage_id, day, start_time, duration):
            print(f"Impossibile pubblicare {artist_name}: conflitto orario")
            return False
        
        # Procede con pubblicazione
        sql_update = '''UPDATE performances 
                        SET published = 1
                        WHERE id = ?'''
        cursor.execute(sql_update, (performance_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Errore pubblicazione: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def check_conflict(stage_id, day, start_time, duration):
    """Verifica sovrapposizioni orarie sullo stesso palco."""
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Calcolo orario fine per logica sovrapposizione
    start_datetime = datetime.strptime(start_time, "%H:%M")
    end_datetime = start_datetime + timedelta(minutes=int(duration))
    end_time = end_datetime.strftime("%H:%M")
    
    # Logica sovrapposizione: due performance NON si sovrappongono se una finisce prima che inizi l'altra
    sql = '''SELECT * FROM performances 
             WHERE stage_id = ? AND day = ? AND published = 1 AND
             NOT (? >= time(start_time, '+' || duration || ' minutes') OR 
                  ? <= start_time)'''
    
    cursor.execute(sql, (stage_id, day, start_time, end_time))
    conflicts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return len(conflicts) > 0

def check_conflict_exclude(stage_id, day, start_time, duration, exclude_id):
    """Come check_conflict ma esclude performance specifica (per modifiche)."""
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    start_datetime = datetime.strptime(start_time, "%H:%M")
    end_datetime = start_datetime + timedelta(minutes=int(duration))
    end_time = end_datetime.strftime("%H:%M")
    
    # Stessa logica con esclusione per ID
    sql = '''SELECT * FROM performances 
             WHERE stage_id = ? AND day = ? AND published = 1 AND id != ? AND
             NOT (? >= time(start_time, '+' || duration || ' minutes') OR 
                  ? <= start_time)'''
    
    cursor.execute(sql, (stage_id, day, exclude_id, start_time, end_time))
    conflicts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return len(conflicts) > 0

def artist_exists(artist_name):
    """Verifica unicità artista (regola business: un artista = una performance)."""
    sql = 'SELECT * FROM performances WHERE artist_name = ?'
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (artist_name,))
    
    artist = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return artist is not None

def delete_performance(performance_id):
    """Elimina solo bozze (published=0) per proteggere programma pubblicato."""
    sql = 'DELETE FROM performances WHERE id = ? AND published = 0'
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (performance_id,))
        conn.commit()
        # rowcount > 0 = eliminazione avvenuta
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()