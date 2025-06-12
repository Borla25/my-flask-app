import sqlite3
from datetime import datetime

MAX_DAILY_CAPACITY = 200  # Capacità massima giornaliera del festival

def get_user_tickets(user_id):
    """Recupera tutti i biglietti di un utente. Usato nel profilo partecipante."""
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
    """Inserisce nuovo biglietto. Gestisce transazioni per integrità vendita."""
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
        print(f"Errore DB add_ticket: {e}")
        return False
    except Exception as e:
        print(f"Errore generale add_ticket: {e}")
        return False

def get_daily_availability():
    """Calcola posti disponibili per giorno. Ogni biglietto conta una volta per giorno."""
    # Inizializza capacità massima
    availability = {
        'venerdi': MAX_DAILY_CAPACITY,
        'sabato': MAX_DAILY_CAPACITY, 
        'domenica': MAX_DAILY_CAPACITY
    }
    
    try:
        conn = sqlite3.connect('db/festival.db')
        cursor = conn.cursor()
        
        # Recupera tutti i biglietti con giorni validi
        cursor.execute('SELECT ticket_type, days FROM tickets WHERE days IS NOT NULL AND days != ""')
        tickets = cursor.fetchall()
        
        # Conteggio per giorno (ogni biglietto conta una volta per giorno coperto)
        day_counts = {'venerdi': 0, 'sabato': 0, 'domenica': 0}
        
        for ticket_type, days in tickets:
            if not days:
                continue
                
            # Dividi giorni CSV e incrementa contatori
            ticket_days = [day.strip() for day in days.split(',')]
            for day in ticket_days:
                if day in day_counts:
                    day_counts[day] += 1
        
        # Calcola disponibilità residua
        for day in availability:
            sold = day_counts[day]
            availability[day] = max(0, MAX_DAILY_CAPACITY - sold)
            
        # Debug per monitoraggio vendite
        print(f"DEBUG availability - Venduti: {day_counts}")
        print(f"DEBUG availability - Disponibili: {availability}")
                    
    except sqlite3.Error as e:
        print(f"Errore calcolo disponibilità: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return availability

def check_availability(ticket_type, selected_days):
    """Verifica disponibilità biglietti per tipo specifico."""
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
    """Valida regole business acquisto biglietti. Previene conflitti e duplicati."""
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Validazioni specifiche per tipo biglietto
        if ticket_type == 'daily':
            if len(selected_days) == 0:
                return False, "Seleziona almeno un giorno per il biglietto giornaliero."
            elif len(selected_days) > 1:
                return False, "Per il biglietto giornaliero puoi selezionare un solo giorno."
        elif ticket_type == '2days':
            if len(selected_days) != 2:
                return False, "Per il pass 2 giorni devi selezionare esattamente 2 giorni."
        
        # Recupera biglietti esistenti dell'utente
        cursor.execute('SELECT ticket_type, days FROM tickets WHERE user_id = ?', (user_id,))
        existing_tickets = cursor.fetchall()
        
        if not existing_tickets:
            return True, "OK"
        
        # Verifica pass multi-giorno esistenti
        has_multi_day = any(ticket[0] in ['2days', 'full'] for ticket in existing_tickets)
        
        if has_multi_day:
            return False, "Hai già un pass multi-giorno. Non puoi acquistare altri biglietti."
        
        # Impedisce acquisto pass se ha biglietti giornalieri
        if ticket_type in ['2days', 'full'] and existing_tickets:
            return False, "Hai già biglietti giornalieri. Non puoi acquistare un pass multi-giorno."
        
        # Per biglietti giornalieri: verifica conflitti giorni
        if ticket_type == 'daily':
            existing_days = set()
            for ticket in existing_tickets:
                if ticket[1]:  # Campo days non vuoto
                    existing_days.update(ticket[1].split(','))
            
            # Controlla sovrapposizioni per giorno selezionato
            for day in selected_days:
                if day in existing_days:
                    day_names = {'venerdi': 'Venerdì', 'sabato': 'Sabato', 'domenica': 'Domenica'}
                    return False, f"Hai già un biglietto per {day_names.get(day, day)}."
            
            return True, "OK"
        
        return True, "OK"
        
    except Exception as e:
        print(f"Errore validazione acquisto: {e}")
        return False, "Errore durante la verifica"
    finally:
        cursor.close()
        conn.close()

def get_user_covered_days(user_id):
    """Restituisce giorni già coperti dai biglietti utente. Per UI form acquisto."""
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
            
            # Full pass copre automaticamente tutti i giorni
            if ticket_type == 'full':
                covered_days.update(['venerdi', 'sabato', 'domenica'])
            elif ticket_type == '2days' and days:
                covered_days.update(days.split(','))
            elif ticket_type == 'daily' and days:
                covered_days.update(days.split(','))
        
        return covered_days
        
    except Exception as e:
        print(f"Errore recupero giorni coperti: {e}")
        return set()
    finally:
        cursor.close()
        conn.close()

def get_festival_stats():
    """Genera statistiche vendite per dashboard organizzatori."""
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    
    try:
        # Metriche totali festival
        cursor.execute('SELECT COUNT(*), SUM(price) FROM tickets')
        total_tickets, total_revenue = cursor.fetchone()
        
        # Breakdown per tipo biglietto
        cursor.execute('''SELECT ticket_type, COUNT(*) 
                          FROM tickets 
                          GROUP BY ticket_type''')
        by_type_data = cursor.fetchall()
        
        # Analisi partecipazione per giorno (query aggregata)
        cursor.execute('''SELECT 
                            SUM(CASE WHEN days LIKE '%venerdi%' THEN 1 ELSE 0 END) as venerdi,
                            SUM(CASE WHEN days LIKE '%sabato%' THEN 1 ELSE 0 END) as sabato,
                            SUM(CASE WHEN days LIKE '%domenica%' THEN 1 ELSE 0 END) as domenica
                          FROM tickets 
                          WHERE days IS NOT NULL AND days != ''
                       ''')
        day_stats = cursor.fetchone()
        
        # Formattazione dati per dashboard
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
        # Fallback con valori di default per robustezza
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