# routes.py

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