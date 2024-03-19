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
                                   (IdentificationAccount TEXT,
                                   Money REAL,
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
                                   (IdentificationAccount TEXT,
                                   Money REAL DEFAULT 0,
                                   BIC TEXT,
                                   CreditLimit REAL,
                                   Rank TEXT DEFAULT 'AAA',
                                   TimeActive INTEGER DEFAULT (strftime('%s', 'now')),
                                   LastPayTime INTEGER DEFAULT (strftime('%s', 'now')),
                                   PayTime INTEGER,
                                   TimeClose INTEGER)''')
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
                                   (IdentificationAccount TEXT,
                                   Money REAL DEFAULT 0,
                                   BIC TEXT,
                                   StatusDeposit TEXT DEFAULT 'ON',
                                   TimeActive INTEGER DEFAULT (strftime('%s', 'now')),
                                   LastPayTime INTEGER DEFAULT (strftime('%s', 'now')),
                                   PayTime INTEGER DEFAULT 0,
                                   TimeClose INTEGER DEFAULT 0)''')
            self.conn.commit()

        def treatment_request(self, request):
            self.analyzer(request, self.cursor, self.conn)


# Создание экземпляра класса BankAccount
bank_account = BankAccount()

# Запрос на открытие депозитного счета
request = {
    'kind_of_account': 'Deposit',
    'request': 'PayDeposit',
    'IdentificationAccount': '12345',
    'Money': 50000.0,
    'BIC': 'ABC123',
    'PayTime': 5,
    'TimeClose': 10,
    'StatusDeposit': 'ON'
}

# Вызов метода process_request с различными запросами
bank_account.process_request(request)