from BankAccount.BankAccount import BankAccount
class Bank:
    def __init__(self, frontend_info):
        # Инициализация банка - получение информации о пользователе по информации из фронтенда (логин и сессия)
        pass

    def create_account(self, account_type, user_info):
        # Создание нового счета определенного типа для пользователя
        # Вернуть информацию о созданном счете, например, его идентификатор
        return BankAccount.create_account(account_type, user_info)

    def connect_to_account(self, account_id):
        # Подключение к существующему счету по его идентификатору
        # Здесь может быть ваша логика для поиска и подключения к счету
        # Вернуть объект счета для дальнейшего управления
        return BankAccount.get_account(account_id)

    def withdraw_money(self, account_id, frontend_request):
        # Преобразование frontend_request в формат request для снятия денег
        request = {
            'IdentificationAccount': account_id,
            'Money': frontend_request['Money']
        }
        account = self.connect_to_account(account_id)
        return account.withdraw_money(request)

    def deposit_money(self, account_id, frontend_request):
        # Преобразование frontend_request в формат request для внесения денег
        request = {
            'IdentificationAccount': account_id,
            'Money': frontend_request['Money']
        }
        account = self.connect_to_account(account_id)
        return account.deposit_money(request)

    def transfer_money(self, from_account_id, to_account_id, frontend_request):
        # Преобразование frontend_request в формат request для перевода денег
        request = {
            'FromAccount': from_account_id,
            'ToAccount': to_account_id,
            'Money': frontend_request['Money']
        }
        from_account = self.connect_to_account(from_account_id)
        to_account = self.connect_to_account(to_account_id)
        return from_account.transfer_money(to_account, request)

    def credit_penalties(self, account_id, frontend_request):
        # Преобразование frontend_request в формат request для начисления пеней
        request = {
            'IdentificationAccount': account_id,
            'PenaltyAmount': frontend_request['PenaltyAmount']
        }
        account = self.connect_to_account(account_id)
        return account.credit_penalties(request)

    def automatic_deposit(self, account_id, frontend_request):
        # Преобразование frontend_request в формат request для автоматического внесения денег
        request = {
            'IdentificationAccount': account_id,
            'DepositAmount': frontend_request['DepositAmount']
        }
        account = self.connect_to_account(account_id)
        return account.automatic_deposit(request)