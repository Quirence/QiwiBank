import socket
from http import cookies
from views import *
from urllib.parse import unquote_plus
from Control.control import *
import time

# Глобальные переменные
HOST = ("localhost", 7777)
control = Control()
active_sessions = {}
COOKIE_NAME = "session_id"

URLS = {
    "/": home,
    "/login": login,
    "/main": main,
    "/register": register,
    "/command": command,
    "/verification": verification,
    "/verif_main": verif_main,
    "/credit": credit,
    "/debit": debit,
    "/deposit": deposit,
    "/open_acc_debit": open_acc_debit,
    "/close_acc_debit": close_acc_debit,
    "/send_money_debit": send_money_debit
}

POST_urls = {
    "/login": login,
    "/register": register,
    "/command": command
}


def check_session_validity(session_id):
    if session_id in active_sessions:
        session_start_time = active_sessions[session_id]["start_time"]
        if time.time() - session_start_time <= 3 * 3600:
            return True
    return False


def generate_session_id():
    return str(time.time())


def set_cookie_header(session_id):
    cookie = cookies.SimpleCookie()
    cookie[COOKIE_NAME] = session_id
    cookie[COOKIE_NAME]["path"] = "/"
    cookie[COOKIE_NAME]["max-age"] = 3 * 3600  # expire after 3 hours
    return cookie.output(header="").strip()


def redirect_to(location, session_id, email=None):
    if email:
        return f"HTTP/1.1 302 Found\nLocation: {location}\nSet-Cookie: {set_cookie_header(session_id)}\nSet-Cookie: email={email}\nContent-Type: text/html; charset=utf-8\n\n"
    else:
        return f"HTTP/1.1 302 Found\nLocation: {location}\nSet-Cookie: {set_cookie_header(session_id)}\nContent-Type: text/html; charset=utf-8\n\n"


def redirect_main(session_id, email=None):
    if check_session_validity(session_id):
        # Пользователь авторизован, перенаправляем на /verif_main
        new_location = "/verif_main"
        return redirect_to(new_location, session_id, email)
    else:
        # Пользователь не авторизован, перенаправляем на главную страницу
        new_location = "/main"
        return redirect_to(new_location, session_id)


def generate_headers(method, url, session_id):
    if url not in URLS:
        return "HTTP/1.1 404 Not found\nContent-Type: text/html; charset=utf-8\n\n", 404

    if url == "/login" and check_session_validity(session_id):
        # Пользователь уже авторизован, перенаправляем на /verif_main
        new_location = "/verif_main"
        return redirect_to(new_location, session_id), 302

    if url == "/login" and method == "POST":
        new_location = "http://localhost:7777/command"  # Перенаправляем на /command после успешной аутентификации
        return redirect_to(new_location, session_id), 302

    if url == "/register" and method == "POST":
        # Пользователь только что зарегистрировался, перенаправляем на /verif_main
        new_location = "/verif_main"
        return redirect_to(new_location, session_id), 302

    if url == "/register" and check_session_validity(session_id):
        # Пользователь авторизован, перенаправляем на /verif_main
        new_location = "/verif_main"
        return redirect_to(new_location, session_id), 302

    if url == "/main" and check_session_validity(session_id):
        # Пользователь авторизован, перенаправляем на /verif_main
        new_location = "/verif_main"
        return redirect_to(new_location, session_id), 302

    if url != "/login" and url != "/register" and url != "/main" and not check_session_validity(session_id):
        return redirect_main(session_id), 302

    if method == "POST" and url not in POST_urls:
        return "HTTP/1.1 405 Method not allowed\nContent-Type: text/html; charset=utf-8\n\n", 405

    return "HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\n", 200


def parse_request(request):
    lines = request.split("\r\n")
    first_line_parts = lines[0].split(" ")
    method = first_line_parts[0]
    url = first_line_parts[1]
    version = first_line_parts[2] if len(first_line_parts) > 2 else None
    index = None
    for i, line in enumerate(lines):
        if line == "":
            index = i
            break
    if index is None:
        headers = {}
        data = {}
    else:
        headers = {}
        for line in lines[1:index]:
            key, value = line.split(": ", 1)
            headers[key] = value
        body = "\r\n".join(lines[index + 1:])
        data = {}
        if method == "POST":
            params = body.split("&")
            for param in params:
                key, value = param.split("=")
                data[unquote_plus(key)] = unquote_plus(value)
        # Извлечение email из куки, если он есть
        if "Cookie" in headers:
            cookie = cookies.SimpleCookie(headers["Cookie"])
            if "email" in cookie:
                data["email"] = cookie["email"].value
    return method, url, headers, data


def generate_content(code, url):
    if code == 404:
        return "<h1>404</h1><p>Not found</p>"
    if code == 405:
        return "<h1>405</h1><p>Method not allowed</p>"
    return URLS[url]()


def generate_result(request):
    method, url, headers, data = parse_request(request)
    print(data)
    session_id = None
    user_email = None
    if "Cookie" in headers:
        cookie = cookies.SimpleCookie(headers["Cookie"])
        if COOKIE_NAME in cookie:
            session_id = cookie[COOKIE_NAME].value
            if session_id in active_sessions:
                user_email = active_sessions[session_id].get('email')

    headers, code = generate_headers(method, url, session_id)
    if (url == '/register' or url == '/login') and method == "POST":
        session = {
            "email": "bebra.hohol@gmail.com",
            "session_id": "something"
        }
        control_response = control.treatment_request(data, session)
        if control_response is not None and control_response.get('status') == 'success':
            user_email = control_response.get('email')
            session_id = generate_session_id()
            new_location = "/verif_main"
            headers = redirect_to(new_location, session_id, user_email)
            active_sessions[session_id] = {"start_time": time.time(), "email": user_email}

    body = generate_content(code, url)
    response = (headers + body).encode()
    return response


def run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(HOST)
    server_socket.listen()
    print("Сервер запущен и ожидает подключений!")

    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(2048)
        response = generate_result(request.decode("UTF-8"))
        client_socket.sendall(response)
        client_socket.close()


run()

