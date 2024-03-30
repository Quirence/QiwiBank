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


def verif_main():
    with open("../templates/verif_main.html", encoding="utf-8") as template:
        return template.read()


def credit():
    with open("../templates/credit.html", encoding="utf-8") as template:
        return template.read()


def debit():
    with open("../templates/debit.html", encoding="utf-8") as template:
        return template.read()


def deposit():
    with open("../templates/deposit.html", encoding="utf-8") as template:
        return template.read()


def open_acc_debit():
    with open("../templates/open_acc_debit.html", encoding="utf-8") as template:
        return template.read()


def close_acc_debit():
    with open("../templates/close_acc_debit.html", encoding="utf-8") as template:
        return template.read()


def send_money_debit():
    with open("../templates/send_money_debit.html", encoding="utf-8") as template:
        return template.read()


def open_acc_credit():
    with open("../templates/open_acc_credit.html", encoding="utf-8") as template:
        return template.read()


def close_acc_credit():
    with open("../templates/close_acc_credit.html", encoding="utf-8") as template:
        return template.read()


def open_acc_deposit():
    with open("../templates/open_acc_deposit.html", encoding="utf-8") as template:
        return template.read()


def close_acc_deposit():
    with open("../templates/close_acc_deposit.html", encoding="utf-8") as template:
        return template.read()


def send_money_credit():
    with open("../templates/send_money_credit.html", encoding="utf-8") as template:
        return template.read()

def send_money_deposit():
    with open("../templates/send_money_deposit.html", encoding="utf-8") as template:
        return template.read()

def local_send_money():
    with open("../templates/local_send_money.html", encoding="utf-8") as template:
        return template.read()