import socket
from views import *
from urllib.parse import unquote_plus
from QiwiBank.Control.control import *

HOST = ("localhost", 7777)
control = Control()
URLS = {
    "/": home,
    "/login": login,
    "/main": main,
    "/register": register,
    "/command": command,
    "/verification": verification
}

POST_urls = {
    "/login": login,
    "/register": register,
    "/command": command
}


def generate_headers(method, url):
    if method == "POST" and url not in POST_urls:
        return "HTTP/1.1 405 Method not allowed\nContent-Type: text/html; charset=utf-8\n\n", 405
    if url not in URLS:
        return "HTTP/1.1 404 Not found\nContent-Type: text/html; charset=utf-8\n\n", 404

    if url == "/login" and method == "POST":
        new_location = "http://localhost:7777/main"
        return f"HTTP/1.1 302 Found\nLocation: {new_location}\nContent-Type: text/html; charset=utf-8\n\n", 302

    return "HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\n", 200


def parse_request(request):
    # Разбиваем запрос на строки
    lines = request.split("\r\n")

    # Первая строка содержит метод, URL и версию HTTP (если указана)
    first_line_parts = lines[0].split(" ")
    method = first_line_parts[0]
    url = first_line_parts[1]
    version = first_line_parts[2] if len(first_line_parts) > 2 else None

    # Ищем индекс пустой строки, разделяющей заголовки и тело запроса
    index = None
    for i, line in enumerate(lines):
        if line == "":
            index = i
            break

    # Если пустая строка не найдена, то это GET запрос без тела
    if index is None:
        headers = {}
        data = {}
    else:
        # Заголовки запроса
        headers = {}
        for line in lines[1:index]:
            key, value = line.split(": ", 1)  # Разделяем строку только по первому символу ":"
            headers[key] = value

        # Тело POST-запроса
        body = "\r\n".join(lines[index + 1:])

        # Инициализируем словарь для хранения данных
        data = {}

        # Если это POST-запрос, парсим тело запроса
        if method == "POST":
            # Разбиваем тело запроса на параметры
            params = body.split("&")

            # Добавляем параметры в словарь
            for param in params:
                key, value = param.split("=")
                data[unquote_plus(key)] = unquote_plus(value)  # декодируем ключи и значения

    return method, url, headers, data


def generate_content(code, url):
    if code == 404:
        return "<h1>404</h1><p>Not found</p>"
    if code == 405:
        return "<h1>405</h1><p>Method not allowed</p>"
    return URLS[url]()

def GenerateRes(request):
    method, url, headers, data = parse_request(request)
    if method != "GET":
        print(data)
    headers, code = generate_headers(method, url)

    # Если регистрация или аутентификация прошли успешно, выполняем редирект
    if (url == '/register' or url == '/login') and method == "POST":
        control_response = control.treatment_request(data)
        if control_response.get('status') == 'success':
            if url == '/login':
                new_location = "/main"  # Перенаправление на main_page при аутентификации
            else:
                new_location = "/"  # Перенаправление на home_page при регистрации
            headers = f"HTTP/1.1 302 Found\nLocation: {new_location}\nContent-Type: text/html; charset=utf-8\n\n"
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
        response = GenerateRes(request.decode("UTF-8"))

        client_socket.sendall(response)
        client_socket.close()


run()
