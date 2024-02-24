# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from routes import handle_registration_form, handle_login_form, handle_main_page, handle_register, handle_login
from database.users import add_user, get_users
import hashlib

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    sessions = {}

    def do_GET(self):
        if self.path == '/login':
            self.handle_login_form()
        elif self.path == '/main_page':
            session_id = self.headers.get('Cookie')
            if session_id and session_id in self.sessions and self.sessions[session_id]:
                self.handle_main_page()
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
        else:
            self.handle_registration_form()

    def do_POST(self):
        if self.path == '/register':
            self.handle_register()
        elif self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = parse_qs(post_data)
            self.handle_login(data_dict)

    def handle_registration_form(self):
        handle_registration_form(self)

    def handle_login_form(self):
        handle_login_form(self)

    def handle_main_page(self):
        session_id = self.headers.get('Cookie')
        if session_id and session_id in self.sessions and self.sessions[session_id]:
            handle_main_page(self)
        else:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()

    def handle_register(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data_dict = parse_qs(post_data)
        handle_register(self, data_dict)

    def handle_login(request_handler, data_dict):
        username = data_dict.get('username', [''])[0]
        password = data_dict.get('password', [''])[0]

        user_list = get_users()

        # Хешируем введенный пароль
        hashed_password_input = hashlib.sha256(password.encode()).hexdigest()

        # Проверяем, есть ли пользователь с таким логином
        for user in user_list:
            if user[1] == username:
                hashed_password_db = user[3]
                # Сравниваем хеши паролей
                if hashed_password_db == hashed_password_input:
                    # Устанавливаем сессию для пользователя
                    session_id = str(hash(username + password))
                    request_handler.sessions[session_id] = True
                    request_handler.send_response(302)
                    request_handler.send_header('Set-Cookie', session_id)
                    request_handler.send_header('Location', '/main_page')
                    request_handler.end_headers()
                    return

        # Если не найден пользователь или пароли не совпадают
        request_handler.send_response(401)
        request_handler.send_header('Content-type', 'text/html')
        request_handler.end_headers()
        request_handler.wfile.write(b'Unauthorized Access!')


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
