import os
import sqlite3
import json
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
                                session TEXT)''')
        self.conn.commit()

    def add_log(self, request, response, session):
        self.cursor.execute("INSERT INTO logs (request, response, session) VALUES (?, ?, ?)", (json.dumps(request), json.dumps(response), json.dumps(session)))
        self.conn.commit()

    def get_log_by_id(self, log_id):
        self.cursor.execute("SELECT request, response, session FROM logs WHERE id = ?", (log_id,))
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0]), json.loads(row[1]), json.loads(row[2])
        else:
            return None, None, None

    def close(self):
        self.conn.close()

# Пример использования
# if __name__ == "__main__":
#     logs = Logs()
#
#     requests = [
#         {'email': 'artiom.burkalov@mail.ru', 'password': 'logobun3', 'method': 'Login'},
#         {'method': 'Getbalance', 'kind_of_account': 'Debit'},
#         {'method': 'Openaccount', 'kind_of_account': 'Debit'},
#         {'method': 'Getbalance', 'kind_of_account': 'Debit'},
#         {'phoneNumber': '123', 'amount': '1000', 'method': 'Sendmoney', 'kind_of_account': 'Debit'},
#         {'email': 'artiom.burkalov@mail.ru', 'request': 'GetID'},
#         {'number': '123', 'request': 'NumberGetID'}
#     ]
#
#     responses = [
#         {'status': 'success'},
#         {'status': 'success', 'balance': 1000},
#         {'status': 'success', 'id_giver': 2, 'id_receiver': 1, 'amount': 1000}
#     ]
#
#     sessions = [
#         None,
#         {'start_time': 1711875769.4994056, 'email': 'test@test.com'},
#         {'start_time': 1711875769.4994056, 'email': 'test@test.com'},
#         None,
#         {'start_time': 1711875769.4994056, 'email': 'test@test.com'},
#         None,
#         {'start_time': 1711875769.4994056, 'email': 'test@test.com'}
#     ]
#
#     # Добавляем запросы, ответы и сессии в логи
#     for req, resp, sess in zip(requests, responses, sessions):
#         logs.add_log(req, resp, sess)
#
#     # Получаем лог по его ID
#     log_id = 3  # Пример ID лога
#     request, response, session = logs.get_log_by_id(log_id)
#     if request and response:
#         print("Retrieved log:")
#         print("Request:", request)
#         print("Response:", response)
#         print("Session:", session)
#     else:
#         print("Log not found for ID:", log_id)
#
#     logs.close()
