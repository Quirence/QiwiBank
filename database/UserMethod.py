import os
import sqlite3
class User:
    def __init__(self):
        # Получаем путь к текущему файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Формируем путь к базе данных
        db_path = os.path.join(current_dir, 'users.db')

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.analyzer = User.AnalyzeRequest()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               email TEXT NOT NULL,
                               password TEXT NOT NULL,
                               number TEXT,
                               name TEXT,
                               surname TEXT,
                               patronymic TEXT,
                               passport_data INTEGER,
                               verification INTEGER DEFAULT 0,
                               rank TEXT DEFAULT 'AAA')''')
        self.conn.commit()

    def treatment_request(self, request):
        self.analyzer(request, self.cursor, self.conn)

    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['method']

            request_methods = {
                'registration': User.AddUser(),
                'delete': User.DelUser(),
                'verification': User.VerifyUser(),
                'is_verified': User.IsVerified(),
                'get_id': User.GetID()
            }

            # Получаем метод из словаря, если он есть, и вызываем его
            method = request_methods.get(request_type)
            if method:
                method(request, cursor, conn)
            else:
                print(f"Unsupported request type: {request_type}")

    class AddUser:
        def __call__(self, request, cursor, conn):
            email = request['email']
            number = request['number']
            cursor.execute("SELECT * FROM users WHERE email = ? OR number = ?",
                           (email, number))
            account = cursor.fetchone()
            if account:
                print("Аккаунт с указанными данными уже существует.")
            else:
                password = request['password']
                name = request['name']
                surname = request['surname']
                patronymic = request['patronymic']
                cursor.execute("INSERT INTO users(email,password,number,name,surname,patronymic) VALUES "
                               "(?,?,?,?,?,?)",
                               (email, password, number, name, surname, patronymic))
                conn.commit()

    class DelUser:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()

    class VerifyUser:
        def __call__(self, request, cursor, conn):
            passport = request['passport_data']
            user_id = request['id']
            cursor.execute("UPDATE users SET passport_data=?, verification = 1 WHERE id = ?", (passport, user_id))
            conn.commit()

    class IsVerified:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            verif = cursor.execute("SELECT verification FROM users WHERE id = ?", (user_id,))
            isverif = verif.fetchone()
            if isverif:
                return isverif[0]
            else:
                print("Аккаунта с указанными данными не существует.")

    class GetID:
        def __call__(self, request, cursor, conn):
            email = request['email']
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            account = cursor.fetchone()
            if account:
                return account[0]
            else:
                print("Аккаунта с указанными данными не существует.")
                return 0


user = User()
request1 = {
    'id': '4',
    'request': 'IsVerified',
    'surname': 'Семён',
    'name': 'Ебучий',
    'passport_data': '1112',
    'patronymic': 'Нигга',
    'email': 'artiom.burkal123@mail.ru',
    'number': '+79029450736',
    'password': 'logobun3'
}
