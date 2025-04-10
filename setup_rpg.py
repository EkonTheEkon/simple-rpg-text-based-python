import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('rpg_game.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    player_class TEXT NOT NULL,
    xp INTEGER DEFAULT 0,
    gold INTEGER DEFAULT 1000,
    level INTEGER DEFAULT 1,
    health INTEGER DEFAULT 100,
    max_health INTEGER DEFAULT 100,
    attack INTEGER DEFAULT 10,
    defense INTEGER DEFAULT 10,
    speed INTEGER DEFAULT 10
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    name TEXT NOT NULL,
    amount INTEGER,
    tipe TEXT,
    stats TEXT,
    FOREIGN KEY (player_id) REFERENCES players (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory_potions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    name TEXT NOT NULL,
    amount INTEGER,
    tipe TEXT,
    FOREIGN KEY (player_id) REFERENCES players (id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")