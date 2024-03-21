import socket
from views import *
import templates
HOST = ("localhost", 7777)

URLS = {
    "/": home,
    "/login": login,
    "/main": main,
    "/register": register
}

def generate_headers(method, url):
    if method == "POST" and url != "/register" and url != "/login":
        return "HTTP/1.1 405 Method not allowed\n\n", 405
    if url not in URLS:
        return "HTTP/1.1 404 Not found\n\n", 404

    if url == "/login" and method == "POST":
        # Обработка паролей
        new_location = "http://localhost:7777/main"
        return f"HTTP/1.1 302 Found\nLocation: {new_location}\n\n", 302

    return "HTTP/1.1 200 OK\n\n", 200

def parse_request(request):
    parsed = request.split(" ")
    print(parsed)
    method = parsed[0]
    url = parsed[1]
    if method == "GET":
        return (method, url, "")
    if method == "POST":
        POST_body = parsed[-1]
    return (method, url, POST_body)

def generate_content(code, url):
    if code == 404:
        return "<h1>404</h1><p>Not found</p>"
    if code == 405:
        return "<h1>405</h1><p>Method not allowed</p>"
    return URLS[url]()

def GenerateRes(request):
    method, url, POST_body = parse_request(request)

    headers, code = generate_headers(method, url)

    body = generate_content(code, url)

    return (headers + body).encode()
def run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(HOST)
    server_socket.listen()
    print("I am listening!")

    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024)
        with open('out.txt', 'w') as f:
            f.write(request.decode("UTF-8"))
        response = GenerateRes(request.decode("UTF-8"))


        client_socket.sendall(response)
        client_socket.close()

run()