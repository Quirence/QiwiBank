import sqlite3


class User:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
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
            request_type = request['request']
            try:
                method = getattr(User, request_type)()
                method(request, cursor, conn)
            except AttributeError:
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

    class GetFSP:
        def __call__(self, request, cursor, conn):
            user_id = request['id']
            fsp = cursor.execute("SELECT name, surname, patronymic FROM users WHERE id = ?", (user_id,))
            fsp_fetch = fsp.fetchone()
            if fsp_fetch:
                out = {
                    'name': fsp_fetch[0],
                    'surname': fsp_fetch[1],
                    'patronymic': fsp_fetch[2]
                }
                return out
            else:
                print("Аккаунта с указанными данными не существует.")


user = User()
request1 = {
    'id': '4',
    'request': 'GetFSP',
    'surname': 'Семён',
    'name': 'Ебучий',
    'passport_data': '1112',
    'patronymic': 'Нигга',
    'email': 'artiom.burkal123@mail.ru',
    'number': '+79029450736',
    'password': 'logobun3'
}
user.treatment_request(request1)
