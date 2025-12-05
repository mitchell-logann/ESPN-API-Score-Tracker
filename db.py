import sqlite3

def initDB():
    conn = sqlite3.connect("tracker.db")
    c = conn.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS favorites (
        user_id TEXT,
        team_id TEXT
    ) """)
    conn.commit()
    conn.close()
    
def saveFavorite(user_id, team_id):
    conn = sqlite3.connect("tracker.db")
    c = conn.cursor()
    c.execute("INSERT INTO favorites (user_id, team_id) VALUES (?, ?)", (user_id, team_id))
    conn.commit()
    conn.close()
    
def getFavorite(user_id):
    conn = sqlite3.connect("tracker.db")
    c = conn.cursor()
    c.execute("SELECT team_id FROM favorites WHERE user_id = ?", (user_id,))
    result = [r[0] for r in c.fetchall()]
    conn.close()
    return result

def removeFavorite(user_id, team_id):
    conn = sqlite3.connect("tracker.db")
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE user_id = ? AND team_id = ?", (user_id, team_id))
    conn.commit()
    conn.close()