from database.UserMethod import *
from BankAccount.BankAccount import bank_account

class Control:
    def __init__(self):
        self.user = User()
        self.user_analyzer = User.AnalyzeRequest()
        self.control_analyzer = self.AnalyzeRequest(self.user_analyzer)

    def treatment_request(self, request, session):
        User.thread_local.cursor = self.user.cursor  # Устанавливаем cursor в thread-local переменной
        User.thread_local.conn = self.user.conn  # Устанавливаем conn в thread-local переменной
        print(session["email"])
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
            if stored_password == password:
                print("Authentication successful.")
                return {'status': 'success', 'redirect': '/main'}  # Redirect to the main page
            else:
                print("Incorrect password or email.")
                return {'status': 'failed'}

    # {'action': 'send_money', 'phoneNumber': '+79025780706', 'amount': '100'}
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
            if id_receiver is not None:
                kind_of_account = request["kind_of_account"]
                amount = request["amount"]
                positive_request = {
                    'kind_of_account': kind_of_account,
                    'request': 'GiveMoney',
                    'IdentificationAccount': id_giver,
                    'Money': amount
                }

                negative_request = {
                    'kind_of_account': kind_of_account,
                    'request': 'GetMoney',
                    'IdentificationAccount': id_receiver,
                    'Money': amount
                }
                print(positive_request["kind_of_account"])
                bank_account.process_request(positive_request)
                bank_account.process_request(negative_request)
            else:
                return {'status': 'failed'}


request = {
    'method': 'Sendmoney',
    'phoneNumber': '+79025780706',
    'amount': '100',
    'kind_of_account': 'Debit',
}
request1 = {
    'kind_of_account': 'Credit',
    'request': 'GetMoney',
    'IdentificationAccount': '12345',
    'Money': 50,
    'BIC': 'ABC123',
    'Rank': 'AAA',
    'CreditLimit': 5000,
    'PayTime': 5,
    'TimeClose': 10,
    'StatusDeposit': 'ON'
}

session = {
    "email": "bebra.hohol@gmail.com"
}
control = Control()
control_response = control.treatment_request(request, session)
