import templates
def login():
    with open("templates/login_form.html") as template:
        return template.read()
def main():
    with open("templates/main_page.html") as template:
        return template.read()

def register():
    with open("templates/registration_form.html") as template:
        return template.read()

def home():
    with open("templates/home_page.html") as template:
        return template.read()