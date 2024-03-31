import os
import sqlite3
import json
from datetime import datetime, timedelta

class Logs:
    def __init__(self):
        db_file = os.path.join(os.path.dirname(__file__), 'requests.db')
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                request TEXT,
                                response TEXT,
                                session TEXT,
                                cleanup_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def add_log(self, request, response, session=None):
        self.cursor.execute("INSERT INTO logs (request, response, session) VALUES (?, ?, ?)", (json.dumps(request), json.dumps(response), json.dumps(session)))
        self.conn.commit()

    def get_log_by_id(self, log_id):
        self.cursor.execute("SELECT request, response, session FROM logs WHERE id = ?", (log_id,))
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0]), json.loads(row[1]), json.loads(row[2])
        else:
            return None, None, None

    def get_last_cleanup_timestamp(self):
        self.cursor.execute("SELECT cleanup_timestamp FROM logs ORDER BY id DESC LIMIT 1")
        row = self.cursor.fetchone()
        if row:
            return datetime.fromisoformat(row[0])
        else:
            return datetime.now()

    def set_last_cleanup_timestamp(self, timestamp):
        self.cursor.execute("UPDATE logs SET cleanup_timestamp = ?", (timestamp,))
        self.conn.commit()

    def cleanup_database(self):
        current_time = datetime.now()
        last_cleanup_time = self.get_last_cleanup_timestamp()
        if current_time - last_cleanup_time >= timedelta(weeks=1):
            self.cursor.execute("DELETE FROM logs WHERE timestamp <= ?", (current_time - timedelta(weeks=1),))
            self.conn.commit()
            self.set_last_cleanup_timestamp(current_time)

    def close(self):
        self.conn.close()

# Пример использования
# if __name__ == "__main__":
#     logs = Logs()
#
#     # Предположим, что это пример использования класса и добавление логов происходит регулярно
#     logs.add_log({'example_request': 'data'}, {'example_response': 'data'})
#     logs.add_log({'example_request': 'data'}, {'example_response': 'data'})
#     logs.add_log({'example_request': 'data'}, {'example_response': 'data'})
#
#     # Выполняем очистку базы данных (если прошла неделя с момента последней очистки)
#     logs.cleanup_database()
#
#     logs.close()
