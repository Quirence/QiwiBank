# Импорт необходимых модулей
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from routes import handle_registration_form, handle_login_form, handle_main_page
from database.users import add_user, get_users

# Класс для обработки запросов
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # Структура для хранения сессий
    sessions = {}

    def do_GET(self):
        if self.path == '/login':
            session_id = self.headers.get('Cookie')
            if session_id and session_id in self.sessions and self.sessions[session_id]:
                self.send_response(302)
                self.send_header('Location', '/main_page')  # Перенаправляем на главную страницу
                self.end_headers()
            else:
                handle_login_form(self)
        elif self.path == '/main_page':
            session_id = self.headers.get('Cookie')
            if session_id and session_id in self.sessions and self.sessions[session_id]:
                handle_main_page(self)
            else:
                self.send_response(302)
                self.send_header('Location', '/login')  # Перенаправляем на страницу входа
                self.end_headers()
        else:
            handle_registration_form(self)

    def do_POST(self):
        if self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = parse_qs(post_data)
            username = data_dict.get('username', [''])[0]
            email = data_dict.get('email', [''])[0]
            password = data_dict.get('password', [''])[0]
            confirmPassword = data_dict.get('confirmPassword', [''])[0]

            # Проверка на пустые поля
            if not (username and email and password and confirmPassword):
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Please fill out all fields!')
                return

            if password != confirmPassword:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Passwords do not match!')
                return

            add_user(username, email, password)  # Добавление пользователя в базу данных

            # Перенаправляем пользователя на страницу авторизации после успешной регистрации
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
        elif self.path == '/login':
            print("Received login POST request")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = parse_qs(post_data)
            username = data_dict.get('username', [''])[0]
            password = data_dict.get('password', [''])[0]

            # Получаем список пользователей из базы данных
            user_list = get_users()

            # Проверяем, существует ли пользователь с таким логином и паролем
            if (username, password) in [(user[1], user[3]) for user in user_list]:
                print("User authenticated successfully")
                session_id = self.headers.get('Cookie')
                if not session_id:
                    session_id = str(hash(username + password))
                    self.sessions[session_id] = True  # Устанавливаем сессию
                    print("Session created:", session_id)
                    self.send_response(302)
                    self.send_header('Set-Cookie', session_id)
                    self.send_header('Location', '/main_page')
                    self.end_headers()
            else:
                print("Authentication failed")
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Unauthorized Access!')

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
