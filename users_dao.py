import sqlite3


def get_user_by_email(email):
    """Get user by email"""
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
    """Get user by ID"""
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
    """Add new user"""
    sql = "INSERT INTO users (email, password, full_name, user_type) VALUES (?, ?, ?, ?)"
    
    conn = sqlite3.connect('db/festival.db')
    cursor = conn.cursor()
    cursor.execute(sql, (user_data['email'], user_data['password'], user_data['full_name'], user_data['user_type']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return True

