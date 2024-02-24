import sqlite3
import os
import hashlib
current_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_dir, 'users.db')

def add_user(username, email, password):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Создаем таблицу users, если ее нет
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')

    # Хешируем пароль
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Добавляем пользователя в базу данных
    cursor.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?)''', (username, email, hashed_password))

    conn.commit()
    conn.close()
def get_users():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM users''')
    users = cursor.fetchall()

    conn.close()

    return users

def get_user_by_username(username):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM users WHERE username = ?''', (username,))
    user = cursor.fetchone()

    conn.close()

    return user
