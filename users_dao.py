import sqlite3
from werkzeug.security import check_password_hash


def get_user_by_email(email):
    """Recupera utente per email. Usato per login e controllo duplicati."""
    sql = 'SELECT * FROM users WHERE email = ?'
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (email,))
    
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Recupera utente per ID. Callback Flask-Login per sessioni."""
    sql = 'SELECT * FROM users WHERE id = ?'
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (user_id,))
    
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return user if user else None

def add_user(user_data):
    """Registra nuovo utente. Password già hashata in input."""
    sql = "INSERT INTO users (email, password, full_name, user_type) VALUES (?, ?, ?, ?)"
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (
            user_data['email'], 
            user_data['password'],  # Già hashata con werkzeug
            user_data['full_name'], 
            user_data['user_type']
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email duplicata (constraint UNIQUE)
        return False
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def update_user(user_id, user_data):
    """Aggiorna profilo utente. Non modifica password per sicurezza."""
    sql = '''UPDATE users 
             SET full_name = ?, profile_image = ?
             WHERE id = ?'''
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (
            user_data['full_name'],
            user_data.get('profile_image', None),
            user_id
        ))
        conn.commit()
        # rowcount > 0 = aggiornamento effettuato
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def change_password(user_id, new_password_hash):
    """Cambia password utente. Hash già calcolato per sicurezza."""
    sql = 'UPDATE users SET password = ? WHERE id = ?'
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (new_password_hash, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def get_users_by_type(user_type):
    """Recupera utenti per tipo. Admin dashboard per gestione utenti."""
    sql = '''SELECT id, email, full_name, user_type, profile_image, created_at
             FROM users 
             WHERE user_type = ?
             ORDER BY full_name'''
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (user_type,))
    
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return users

def delete_user(user_id):
    """Elimina utente se non ha dati associati (performance/biglietti)."""
    sql = 'DELETE FROM users WHERE id = ?'
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        # Constraint FK violata - utente ha dati associati
        return False
    except sqlite3.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def verify_user_credentials(email, password_hash):
    """Verifica credenziali complete per autenticazione sicura."""
    user = get_user_by_email(email)
    
    if not user:
        return None
    
    # Controllo hash password (werkzeug.security.check_password_hash)
    if check_password_hash(user['password'], password_hash):
        # Rimuove password dall'oggetto restituito per sicurezza
        user_safe = dict(user)
        del user_safe['password']
        return user_safe
    
    return None

