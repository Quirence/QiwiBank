from database.UserMethod import *
from BankAccount.BankAccount import bank_account
from Control.Requests import *

get_request = Requests()


class Control:
    def __init__(self):
        self.user = User()
        self.user_analyzer = User.AnalyzeRequest()
        self.control_analyzer = self.AnalyzeRequest(self.user_analyzer)

    def treatment_request(self, request, session=None):
        User.thread_local.cursor = self.user.cursor
        User.thread_local.conn = self.user.conn
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
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session=None):
            new_request = request.copy()
            new_request['request'] = 'AddUser'
            if self.user_analyzer(new_request):
                print("Registration successful.")
                return {'status': 'success', 'redirect': '/'}
            else:
                print("Registration failed")
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
                return {'status': 'success', 'redirect': '/main', "email": email}
            else:
                print("Incorrect password or email.")
                return {'status': 'failed'}

    class Openaccount:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_user_request = get_request.id_user_request(session)
            id_user = self.user_analyzer(id_user_request)
            open_request = get_request.open_request(request, id_user)
            bank_account.process_request(open_request)

    class Closeaccount:

        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_user_request = get_request.id_user_request(session)
            id_user = self.user_analyzer(id_user_request)
            close_request = get_request.close_request(request, id_user)
            bank_account.process_request(close_request)

    class Getbalance:

        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_user_request = get_request.id_user_request(session)
            id_user = self.user_analyzer(id_user_request)
            if id_user is not None:
                balance_request = get_request.balance_request(request, id_user)
                balance = bank_account.process_request(balance_request)
                return {"status": "success", "balance": balance}
            else:
                return {"status": "failed"}

    class Sendmoney:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_giver_request = get_request.id_user_request(session)
            id_receiver_request = get_request.id_number_user_request(request)
            print(id_giver_request, id_receiver_request)
            id_giver = self.user_analyzer(id_giver_request)
            id_receiver = self.user_analyzer(id_receiver_request)
            if all((id_receiver, id_giver)):
                amount = int(request["amount"])
                id_balance_request = get_request.id_balance_request(request, id_giver)
                balance_giver = bank_account.process_request(id_balance_request)
                if balance_giver:
                    if balance_giver >= amount:
                        giver_request = get_request.giver_request(request, id_giver)
                        receiver_request = get_request.receiver_request(request, id_receiver)
                        bank_account.process_request(receiver_request)
                        bank_account.process_request(giver_request)
                else:
                    print(f"Недостаточно средств на вашем счету")
            else:
                print(f"Счет получателя не найден")


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
# Для readme - здесь можно проверить, как control реагирует на запросы из интерфейса (вручную)
control = Control()
# control.treatment_request(fourth_request, session1)
# control.treatment_request(second_request, session1)
# control.treatment_request(third_request, session1)
# control.treatment_request(second_request, session1)
