import sqlite3
from datetime import date

DB_NAME = 'habits.db'


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            description TEXT,
            reminder_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            completion_date DATE,
            FOREIGN KEY (habit_id) REFERENCES habits (id),
            UNIQUE(habit_id, completion_date)
        )
    ''')
    conn.commit()
    conn.close()


def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
    ''', (user_id, username, full_name))
    conn.commit()
    conn.close()


def add_habit(user_id, name, description, reminder_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO habits (user_id, name, description, reminder_time)
        VALUES (?, ?, ?, ?)
    ''', (user_id, name, description, reminder_time))
    conn.commit()
    habit_id = cursor.lastrowid
    conn.close()
    return habit_id


def get_habits(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, description, reminder_time FROM habits
        WHERE user_id = ?
    ''', (user_id,))
    habits = cursor.fetchall()
    conn.close()
    return habits


def check_habit(habit_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = date.today()
    try:
        cursor.execute('''
            INSERT INTO completions (habit_id, completion_date)
            VALUES (?, ?)
        ''', (habit_id, today))
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success


def get_streak(habit_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT completion_date FROM completions
        WHERE habit_id = ?
        ORDER BY completion_date DESC
    ''', (habit_id,))
    completions = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not completions:
        return 0

    streak = 0
    current_date = date.today()
    for completion in completions:
        if completion == current_date:
            streak += 1
            current_date = current_date.replace(day=current_date.day - 1)
        else:
            break
    return streak


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]


def get_habits_with_reminder(reminder_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, id, name FROM habits
        WHERE reminder_time = ?
    ''', (reminder_time,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def get_habit_by_id(habit_id):
    """Получает информацию о привычке по её ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, description, reminder_time FROM habits
        WHERE id = ?
    ''', (habit_id,))
    habit = cursor.fetchone()
    conn.close()
    return habit
