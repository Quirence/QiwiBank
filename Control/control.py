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

    def start_payment_scheduler(self):
        self.pay_credit()
        self.pay_deposit()

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
                return {'status': 'success'}
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
                return {'status': 'success', "email": email}
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
            response = bank_account.process_request(open_request)
            return response

    class Closeaccount:

        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_user_request = get_request.id_user_request(session)
            id_user = self.user_analyzer(id_user_request)
            close_request = get_request.close_request(request, id_user)
            response = bank_account.process_request(close_request)
            return response

    class Getbalance:

        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_user_request = get_request.id_user_request(session)
            id_user = self.user_analyzer(id_user_request)
            if id_user is not None:
                balance_request = get_request.balance_request(request, id_user)
                balance = bank_account.process_request(balance_request)
                if balance is not None:
                    return {"status": "success", "balance": balance}
            return {"status": "failed"}

    class Sendmoney:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_giver_request = get_request.id_user_request(session)
            id_receiver_request = get_request.id_number_user_request(request)
            id_giver = self.user_analyzer(id_giver_request)
            id_receiver = self.user_analyzer(id_receiver_request)
            if all((id_receiver, id_giver)):
                amount = int(request["amount"])
                id_balance_request = get_request.id_balance_request(request, id_giver)
                balance_giver = bank_account.process_request(id_balance_request)
                limit = balance_giver
                if type(balance_giver) is tuple:
                    limit = balance_giver[1]
                    balance_giver = balance_giver[0]
                if balance_giver and amount <= limit:
                    giver_request = get_request.giver_request(request, id_giver)
                    receiver_request = get_request.receiver_request(request, id_receiver)
                    if bank_account.process_request(receiver_request).get("status") == "success":
                        if bank_account.process_request(giver_request).get("status") == "failed":
                            giver_request["kind_of_account"] = receiver_request["kind_of_account"]
                            bank_account.process_request(giver_request)
                    else:
                        print("Счет получателя не найден")
                        return {"status": "failed"}
                    return {"status": "success", "id_giver": id_giver, "id_receiver": id_receiver, "amount": amount}
                else:
                    print(f"Недостаточно средств на вашем счету")
                    return {"status": "failed"}
            else:
                print(f"Пользователя с таким номером не существует")
                return {"status": "failed"}

    class Selfsend:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request, session):
            id_user_request = get_request.id_user_request(session)
            id_user = self.user_analyzer(id_user_request)
            id_balance_request = get_request.id_balance_from_request(request, id_user)
            balance = bank_account.process_request(id_balance_request)
            limit = balance
            if type(balance) is tuple:
                limit = balance[1]
                balance = balance[0]
            amount = request["amount"]
            if amount == "":
                amount = 0
            else:
                amount = int(amount)
            if balance and (amount <= limit):
                giver_request = get_request.from_giver_request(request, id_user)
                receiver_request = get_request.to_receiver_request(request, id_user)
                if bank_account.process_request(receiver_request).get("status") == "success":
                    if bank_account.process_request(giver_request).get("status") == "failed":
                        giver_request["kind_of_account"] = request["to_kind_of_account"]
                        bank_account.process_request(giver_request)
                        return {"status": "failed"}
                else:
                    print("У вас не открыт счет, на который вы переводите")
                    return {"status": "failed"}
                return {"status": "success", "amount": amount}
            else:
                print(f"Недостаточно средств на счету, с которого вы переводите")
                return {"status": "failed"}
            pass

    @staticmethod
    def pay_credit():
        pay_credit_request = get_request.pay_credit_request()
        bank_account.process_request(pay_credit_request)

    @staticmethod
    def pay_deposit():
        pay_deposit_request = get_request.pay_deposit_request()
        bank_account.process_request(pay_deposit_request)


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
# control = Control()
# control.treatment_request(first_request, session1)
# control.treatment_request(second_request, session1)
# control.treatment_request(third_request, session1)
# control.treatment_request(second_request, session1)
