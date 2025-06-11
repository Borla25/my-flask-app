import sqlite3

def get_all_stages():
    """Get all stages"""
    query = '''SELECT id, name, capacity, description, created_at
               FROM stages
               ORDER BY name'''
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    
    stages = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stages


def get_stage_by_name(name):
    """Get stage by name"""
    query = '''SELECT id, name, capacity, description, created_at
               FROM stages
               WHERE name = ?'''
    
    conn = sqlite3.connect('db/festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (name,))
    
    stage = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return stage