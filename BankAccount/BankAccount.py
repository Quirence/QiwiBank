import sqlite3
from Methods.MethodDebit import MethodDebit
from Methods.MethodCredit import MethodCredit
from Methods.MethodDeposit import MethodDeposit


class BankAccount:
    def __init__(self):
        self.accounts = {
            'Debit': self.Debit(),
            'Credit': self.Credit(),
            'Deposit': self.Deposit()
        }

    def process_request(self, request):
        kind_of_account = request['kind_of_account']
        try:
            treatment_request = self.accounts[kind_of_account]
            treatment_request.treatment_request(request)
        except KeyError:
            print(f"Unsupported kind of account: {kind_of_account}. Supported types are: {list(self.accounts.keys())}")

        except AttributeError:
            print(f"Unsupported request type: {request['request']}")

    class Debit:
        def __init__(self):
            self.conn = sqlite3.connect('debit_accounts.db')
            self.cursor = self.conn.cursor()
            self.create_table()
            self.analyzer = MethodDebit.AnalyzeRequest()

        def create_table(self):
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS debit_accounts
                                   (identification_account TEXT,
                                   money REAL,
                                   BIC TEXT)''')
            self.conn.commit()

        def treatment_request(self, request):
            self.analyzer(request, self.cursor, self.conn)

    class Credit:
        def __init__(self):
            self.conn = sqlite3.connect('credit_accounts.db')
            self.cursor = self.conn.cursor()
            self.create_table()
            self.analyzer = MethodCredit.AnalyzeRequest()

        def create_table(self):
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS credit_accounts
                                   (identification_account TEXT,
                                   money REAL DEFAULT 0,
                                   BIC TEXT,
                                   credit_limit REAL,
                                   rank TEXT DEFAULT 'AAA')''')
            self.conn.commit()

        def treatment_request(self, request):
            self.analyzer(request, self.cursor, self.conn)

    class Deposit:
        def __init__(self):
            self.conn = sqlite3.connect('deposit_accounts.db')
            self.cursor = self.conn.cursor()
            self.create_table()
            self.analyzer = MethodDeposit.AnalyzeRequest()

        def create_table(self):
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS deposit_accounts
                                   (identification_account TEXT,
                                   money REAL DEFAULT 0,
                                   BIC TEXT,
                                   status_deposit TEXT DEFAULT 'OFF')''')
            self.conn.commit()

        def treatment_request(self, request):
            self.analyzer(request, self.cursor, self.conn)


bank_account = BankAccount()

request1 = {
    'kind_of_account': 'Deposit',
    'request': 'GiveMoney',
    'identification_account': '12345',
    'money': 50000.0,
    'BIC': 'ABC123',
    'deposit_status': 'ON'
}

# Вызов метода process_request с различными запросами
bank_account.process_request(request1)
