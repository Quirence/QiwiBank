# routes.py
from urllib.parse import parse_qs
from database.users import add_user, get_users
import hashlib

def handle_registration_form(request_handler):
    request_handler.send_response(200)
    request_handler.send_header('Content-type', 'text/html')
    request_handler.end_headers()
    with open('templates/registration_form.html', 'r') as file:
        request_handler.wfile.write(file.read().encode('utf-8'))

def handle_login_form(request_handler):
    request_handler.send_response(200)
    request_handler.send_header('Content-type', 'text/html')
    request_handler.end_headers()
    with open('templates/login_form.html', 'r') as file:
        request_handler.wfile.write(file.read().encode('utf-8'))

def handle_main_page(request_handler):
    request_handler.send_response(200)
    request_handler.send_header('Content-type', 'text/html')
    request_handler.end_headers()
    with open('templates/main_page.html', 'r') as file:
        request_handler.wfile.write(file.read().encode('utf-8'))

    # Добавьте здесь обработку вашей страницы, если она предполагается

def handle_register(request_handler, data_dict):
    username = data_dict.get('username', [''])[0]
    email = data_dict.get('email', [''])[0]
    password = data_dict.get('password', [''])[0]
    confirmPassword = data_dict.get('confirmPassword', [''])[0]

    if not (username and email and password and confirmPassword):
        request_handler.send_response(400)
        request_handler.send_header('Content-type', 'text/html')
        request_handler.end_headers()
        request_handler.wfile.write(b'Please fill out all fields!')
        return

    if password != confirmPassword:
        request_handler.send_response(400)
        request_handler.send_header('Content-type', 'text/html')
        request_handler.end_headers()
        request_handler.wfile.write(b'Passwords do not match!')
        return

    add_user(username, email, password)
    request_handler.send_response(302)
    request_handler.send_header('Location', '/login')
    request_handler.end_headers()
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
                request_handler.send_response(302)
                request_handler.send_header('Location', '/main_page')
                request_handler.end_headers()
                return

    # Если не найден пользователь или пароли не совпадают
    request_handler.send_response(401)
    request_handler.send_header('Content-type', 'text/html')
    request_handler.end_headers()
    request_handler.wfile.write(b'Unauthorized Access!')