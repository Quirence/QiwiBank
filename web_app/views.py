import templates


def login():
    with open('../templates/login_form.html', encoding="utf-8") as template:
        return template.read()


def main():
    with open("../templates/main_page.html", encoding="utf-8") as template:
        return template.read()


def register():
    with open("../templates/registration_form.html", encoding="utf-8") as template:
        return template.read()


def home():
    with open("../templates/home_page.html", encoding="utf-8") as template:
        return template.read()


def command():
    with open("../templates/command_form.html", encoding="utf-8") as template:
        return template.read()


def verification():
    with open("../templates/verification_form.html", encoding="utf-8") as template:
        return template.read()
