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
    "/deposit": deposit
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


def redirect_to(location, session_id):
    return f"HTTP/1.1 302 Found\nLocation: {location}\nSet-Cookie: {set_cookie_header(session_id)}\nContent-Type: text/html; charset=utf-8\n\n"


def redirect_main(session_id):
    if check_session_validity(session_id):
        # Пользователь авторизован, перенаправляем на /verif_main
        new_location = "/verif_main"
        return redirect_to(new_location, session_id)
    else:
        # Пользователь не авторизован, перенаправляем на главную страницу
        new_location = "/main"
        return redirect_to(new_location, session_id)


def generate_headers(method, url, session_id):
    redirect_urls = {
        "/login": "/verif_main",
        "/register": "/verif_main",
        "/main": "/verif_main"
    }

    if url not in URLS:
        return "HTTP/1.1 404 Not found\nContent-Type: text/html; charset=utf-8\n\n", 404

    if url in redirect_urls and check_session_validity(session_id):
        # Пользователь уже авторизован, перенаправляем на соответствующий URL
        new_location = redirect_urls[url]
        return redirect_to(new_location, session_id), 302

    if method == "POST":
        if url == "/login":
            new_location = "http://localhost:7777/command"  # Перенаправляем на /command после успешной аутентификации
            return redirect_to(new_location, session_id), 302
        elif url == "/register":
            # Пользователь только что зарегистрировался, перенаправляем на /verif_main
            new_location = "/verif_main"
            return redirect_to(new_location, session_id), 302
        elif url not in POST_urls:
            return "HTTP/1.1 405 Method not allowed\nContent-Type: text/html; charset=utf-8\n\n", 405

    if url not in ["/login", "/register", "/main"] and not check_session_validity(session_id):
        return redirect_main(session_id), 302

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
    return method, url, headers, data


def generate_content(code, url):
    if code == 404:
        return "<h1>404</h1><p>Not found</p>"
    if code == 405:
        return "<h1>405</h1><p>Method not allowed</p>"
    return URLS[url]()


def generate_result(request):
    method, url, headers, data = parse_request(request)
    session_id = None
    if "Cookie" in headers:
        cookie = cookies.SimpleCookie(headers["Cookie"])
        if COOKIE_NAME in cookie:
            session_id = cookie[COOKIE_NAME].value

    headers, code = generate_headers(method, url, session_id)
    if (url == '/register' or url == '/login') and method == "POST":
        control_response = control.treatment_request(data)
        if control_response is not None and control_response.get('status') == 'success':
            session_id = generate_session_id()  # Генерируем новый session_id
            new_location = "/verif_main"  # Перенаправляем на /command после успешной аутентификации
            headers = redirect_to(new_location, session_id)
            active_sessions[session_id] = {"start_time": time.time()}  # Сохраняем новый session_id в active_sessions
            return headers.encode()
    body = generate_content(code, url)
    response = (headers + body).encode()
    return response


def run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(HOST)
    server_socket.listen()
    print("I am listening!")

    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(2048)
        with open('out.txt', 'w') as f:
            f.write(request.decode("UTF-8"))
        response = generate_result(request.decode("UTF-8"))
        client_socket.sendall(response)
        client_socket.close()


run()


