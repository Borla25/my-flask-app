import sqlite3
from datetime import datetime

MAX_DAILY_CAPACITY = 200  # Capacità massima giornaliera

def get_user_tickets(user_id):
    """Get all tickets for a user"""
    sql = 'SELECT * FROM tickets WHERE user_id = ?'
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (user_id,))
    
    tickets = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return tickets

def add_ticket(ticket_data):
    """Add new ticket"""
    sql = '''INSERT INTO tickets (user_id, ticket_type, days, price, purchase_date)
             VALUES (?, ?, ?, ?, ?)'''
    
    try:
        with sqlite3.connect('db/festival.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute(sql, (
                ticket_data['user_id'], 
                ticket_data['ticket_type'],
                ticket_data['days'], 
                ticket_data['price'], 
                ticket_data['purchase_date']
            ))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"SQLite Error in add_ticket: {e}")  # ← AGGIUNGI QUESTO
        return False
    except Exception as e:
        print(f"General Error in add_ticket: {e}")  # ← AGGIUNGI QUESTO
        return False

def get_daily_availability():
    """Get available tickets for each day"""
    # Inizializza con tutti i giorni
    availability = {
        'venerdi': MAX_DAILY_CAPACITY,
        'sabato': MAX_DAILY_CAPACITY, 
        'domenica': MAX_DAILY_CAPACITY
    }
    
    try:
        conn = sqlite3.connect('db/festival.db')
        cursor = conn.cursor()
        
        # ← NUOVA LOGICA: Conta ogni biglietto una sola volta per giorno
        cursor.execute('SELECT ticket_type, days FROM tickets WHERE days IS NOT NULL AND days != ""')
        tickets = cursor.fetchall()
        
        # Conta i biglietti per ogni giorno
        day_counts = {'venerdi': 0, 'sabato': 0, 'domenica': 0}
        
        for ticket_type, days in tickets:
            if not days:
                continue
                
            # Dividi i giorni e aggiungi il conteggio
            ticket_days = [day.strip() for day in days.split(',')]
            for day in ticket_days:
                if day in day_counts:
                    day_counts[day] += 1
        
        # Calcola la disponibilità
        for day in availability:
            sold = day_counts[day]
            availability[day] = max(0, MAX_DAILY_CAPACITY - sold)
            
        # ← DEBUG temporaneo per verificare
        print(f"DEBUG availability - Day counts: {day_counts}")
        print(f"DEBUG availability - Final availability: {availability}")
                    
    except sqlite3.Error as e:
        print(f"Error in get_daily_availability: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return availability

def check_availability(ticket_type, selected_days):
    """Check ticket availability"""
    availability = get_daily_availability()
    
    if ticket_type == 'daily':
        if len(selected_days) != 1:
            return False
        day = selected_days[0]
        result = day in availability and availability[day] > 0
        return result
    
    elif ticket_type == '2days':
        if len(selected_days) != 2:
            return False
        result = all(day in availability and availability[day] > 0 for day in selected_days)
        return result
    
    elif ticket_type == 'full':
        required_days = ['venerdi', 'sabato', 'domenica']
        result = all(availability.get(day, 0) > 0 for day in required_days)
        return result
    
    return False


def can_purchase_ticket(user_id, ticket_type, selected_days):
    """Check if user can purchase a specific ticket type"""
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Validazioni specifiche per tipo di biglietto
        if ticket_type == 'daily':
            if len(selected_days) == 0:
                return False, "Seleziona almeno un giorno per il biglietto giornaliero."
            elif len(selected_days) > 1:
                return False, "Per il biglietto giornaliero puoi selezionare un solo giorno."
        elif ticket_type == '2days':
            if len(selected_days) != 2:
                return False, "Per il pass 2 giorni devi selezionare esattamente 2 giorni."
        
        # Get all user's existing tickets
        cursor.execute('SELECT ticket_type, days FROM tickets WHERE user_id = ?', (user_id,))
        existing_tickets = cursor.fetchall()
        
        if not existing_tickets:
            return True, "OK"
        
        # Check existing ticket types
        has_multi_day = any(ticket[0] in ['2days', 'full'] for ticket in existing_tickets)
        
        if has_multi_day:
            return False, "Hai già un pass multi-giorno. Non puoi acquistare altri biglietti."
        
        # If requesting multi-day ticket but has daily tickets
        if ticket_type in ['2days', 'full'] and existing_tickets:
            return False, "Hai già biglietti giornalieri. Non puoi acquistare un pass multi-giorno."
        
        # If requesting daily ticket, check for day conflicts
        if ticket_type == 'daily':
            existing_days = set()
            for ticket in existing_tickets:
                if ticket[1]:  # days field not empty
                    existing_days.update(ticket[1].split(','))
            
            # Check if any selected day is already covered
            for day in selected_days:
                if day in existing_days:
                    day_names = {'venerdi': 'Venerdì', 'sabato': 'Sabato', 'domenica': 'Domenica'}  # ← Cambiato
                    return False, f"Hai già un biglietto per {day_names.get(day, day)}."
            
            return True, "OK"
        
        return True, "OK"
        
    except Exception as e:
        print(f"Error checking ticket purchase eligibility: {e}")
        return False, "Errore durante la verifica"
    finally:
        cursor.close()
        conn.close()

def get_user_covered_days(user_id):
    """Get all days already covered by user's tickets"""
    sql = 'SELECT ticket_type, days FROM tickets WHERE user_id = ?'
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, (user_id,))
        tickets = cursor.fetchall()
        covered_days = set()
        
        for ticket in tickets:
            ticket_type, days = ticket[0], ticket[1]
            
            if ticket_type == 'full':
                covered_days.update(['venerdi', 'sabato', 'domenica'])  # ← Cambiato
            elif ticket_type == '2days' and days:
                covered_days.update(days.split(','))
            elif ticket_type == 'daily' and days:
                covered_days.update(days.split(','))
        
        return covered_days
        
    except Exception as e:
        print(f"Error getting covered days: {e}")
        return set()
    finally:
        cursor.close()
        conn.close()

def get_festival_stats():
    """Get general festival ticket sales statistics"""
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        # ← Statistiche generali del festival
        cursor.execute('SELECT COUNT(*), SUM(price) FROM tickets')
        total_tickets, total_revenue = cursor.fetchone()
        
        # ← Vendite per tipo di biglietto
        cursor.execute('''SELECT ticket_type, COUNT(*) 
                          FROM tickets 
                          GROUP BY ticket_type''')
        by_type_data = cursor.fetchall()
        
        # ← Vendite per giorno del festival
        cursor.execute('''SELECT 
                            SUM(CASE WHEN days LIKE '%venerdi%' THEN 1 ELSE 0 END) as venerdi,
                            SUM(CASE WHEN days LIKE '%sabato%' THEN 1 ELSE 0 END) as sabato,
                            SUM(CASE WHEN days LIKE '%domenica%' THEN 1 ELSE 0 END) as domenica
                          FROM tickets 
                          WHERE days IS NOT NULL AND days != ''
                       ''')
        day_stats = cursor.fetchone()
        
        # ← Formatta i dati
        by_type = {
            'daily': 0,
            '2days': 0,
            'full': 0
        }
        
        for ticket_type, count in by_type_data:
            if ticket_type in by_type:
                by_type[ticket_type] = count
        
        by_day = {
            'venerdi': day_stats[0] if day_stats[0] else 0,
            'sabato': day_stats[1] if day_stats[1] else 0,
            'domenica': day_stats[2] if day_stats[2] else 0
        }
        
        return {
            'total_tickets': total_tickets or 0,
            'total_revenue': f"{total_revenue:.2f}" if total_revenue else "0.00",
            'by_type': by_type,
            'by_day': by_day,
            'available_tickets': get_daily_availability()
        }
        
    except sqlite3.Error:
        return {
            'total_tickets': 0,
            'total_revenue': "0.00",
            'by_type': {'daily': 0, '2days': 0, 'full': 0},
            'by_day': {'venerdi': 0, 'sabato': 0, 'domenica': 0},
            'available_tickets': {'venerdi': 200, 'sabato': 200, 'domenica': 200}
        }
    finally:
        cursor.close()
        conn.close()