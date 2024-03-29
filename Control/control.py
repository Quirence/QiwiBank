from database.UserMethod import *
from BankAccount.BankAccount import bank_account


class Control:
    def __init__(self):
        self.user = User()
        self.user_analyzer = User.AnalyzeRequest()
        self.control_analyzer = self.AnalyzeRequest(self.user_analyzer)

    def treatment_request(self, request, session=None):
        User.thread_local.cursor = self.user.cursor  # Устанавливаем cursor в thread-local переменной
        User.thread_local.conn = self.user.conn  # Устанавливаем conn в thread-local переменной
        return self.control_analyzer(request, session)

    class AnalyzeRequest:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session=None):
            request_type = request['method']
            try:
                method = getattr(Control, request_type)
                return method(self.user_analyzer)(request, session)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")

    class Registration:
        def __init__(self, user_analyzer):  # Ensure this argument is passed correctly
            self.user_analyzer = user_analyzer

        def __call__(self, request, session=None):
            new_request = request.copy()
            new_request['request'] = 'AddUser'
            if self.user_analyzer(new_request):
                print("Registration successful.")
                return {'status': 'success', 'redirect': '/'}  # Redirect to the main page
            else:
                print("Registration failed blyat.")
                return {'status': 'failed'}

    class Login:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session=None):
            new_request = request.copy()
            new_request['request'] = 'GetPassword'
            password = request['password']
            stored_password = self.user_analyzer(new_request)
            email = request["email"]
            if stored_password == password:
                print("Authentication successful.")
                return {'status': 'success', 'redirect': '/main', "email": email}  # Redirect to the main page
            else:
                print("Incorrect password or email.")
                return {'status': 'failed'}

    # {'action': 'send_money', 'phoneNumber': '+79025780706', 'amount': '100'}
    class Openaccount:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            email = session["email"]
            kind_of_account = request["kind_of_account"]
            id_user_request = {"email": email,
                               "request": "GetID"}
            id_user = self.user_analyzer(id_user_request)
            open_request = {
                'kind_of_account': kind_of_account,
                'request': 'OpenAccount',
                'IdentificationAccount': id_user,
                'Money': 1000,
                'BIC': 'ABC123',
                'Rank': 'AAA',
                'CreditLimit': 5000,
                'PayTime': 5,
                'TimeClose': 10,
                'StatusDeposit': 'ON'
            }
            bank_account.process_request(open_request)

    class Closeaccount:

        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            email = session["email"]
            kind_of_account = request["kind_of_account"]
            id_user_request = {"email": email,
                               "request": "GetID"}
            id_user = self.user_analyzer(id_user_request)
            close_request = {
                'kind_of_account': kind_of_account,
                'request': 'CloseAccount',
                'IdentificationAccount': id_user,
            }
            bank_account.process_request(close_request)

    class Getbalance:

        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            email = session["email"]
            kind_of_account = request["kind_of_account"]
            id_user_request = {"email": email,
                               "request": "GetID"}
            id_user = self.user_analyzer(id_user_request)
            if id_user is not None:
                balance_request = {
                    'IdentificationAccount': id_user,
                    "request": "GetBalance",
                    "kind_of_account": kind_of_account
                }
                balance = bank_account.process_request(balance_request)
                return {"status": "success", "balance": balance}
            else:
                return {"status": "failed"}

    class Sendmoney:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            email = session["email"]
            number = request['phoneNumber']
            id_giver_request = {"email": email,
                                "request": "GetID"}
            id_receiver_request = {"number": number,
                                   "request": "NumberGetID"}
            id_giver = self.user_analyzer(id_giver_request)
            id_receiver = self.user_analyzer(id_receiver_request)
            if id_receiver is not None and id_giver is not None:
                kind_of_account = request["kind_of_account"]
                amount = int(request["amount"])
                id_balance_request = {
                    'kind_of_account': kind_of_account,
                    'request': 'GetBalance',
                    'IdentificationAccount': id_giver
                }
                balance_giver = bank_account.process_request(id_balance_request)
                positive_request = {
                    'kind_of_account': kind_of_account,
                    'request': 'GiveMoney',
                    'IdentificationAccount': id_giver,
                    'Money': amount
                }

                negative_request = {
                    'kind_of_account': 'Debit',
                    'request': 'GetMoney',
                    'IdentificationAccount': id_receiver,
                    'Money': amount
                }
                if balance_giver >= amount:
                    if bank_account.process_request(negative_request):
                        bank_account.process_request(positive_request)
                    else:
                        print("У получателя не открыт дебетовый счет.")
                else:
                    print("Недостаточно средств на вашем счету.")
            else:
                return {'status': 'failed'}


first_request = {
    'method': 'Openaccount',
    'kind_of_account': 'Debit',
}

second_request = {
    'method': 'Sendmoney',
    'phoneNumber': '+79025780706',
    'amount': '100',
    'kind_of_account': 'Debit',
}

third_request = {
    'method': 'Closeaccount',
    'kind_of_account': 'Debit',
}

fourth_request = {
    'method': 'Getbalance',
    'kind_of_account': 'Debit',
}

session1 = {
    "email": "bebra.hohol@gmail.com"
}

control = Control()
# control.treatment_request(fourth_request, session1)
# control.treatment_request(second_request, session1)
# control.treatment_request(third_request, session1)
# control.treatment_request(second_request, session1)
