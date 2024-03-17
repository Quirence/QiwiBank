import sqlite3


class MethodDebit:

    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['request']
            try:
                method = getattr(MethodDebit, request_type)()
                method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT * FROM debit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {identification_account} уже существует.")
            else:
                money = request['money']
                BIC = request['BIC']
                cursor.execute("INSERT INTO debit_accounts VALUES (?, ?, ?)",
                               (identification_account, money, BIC))
                conn.commit()
                print(f"Счет {identification_account} успешно открыт.")

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT * FROM debit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                cursor.execute("DELETE FROM debit_accounts WHERE identification_account = ?",
                               (identification_account,))
                conn.commit()
                print(f"Счет {identification_account} успешно закрыт.")
            else:
                print(f"Счет {identification_account} не найден.")

    class GetMoney:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            money = request['money']
            cursor.execute("SELECT * FROM debit_accounts WHERE identification_account = ?", (identification_account,))
            account_exists = cursor.fetchone()
            if account_exists:
                cursor.execute("UPDATE debit_accounts SET money = money + ? WHERE identification_account = ?",
                               (money, identification_account))
                conn.commit()
                print(f"Сумма {money} успешно зачислена на счет {identification_account}.")
            else:
                print(f"Счет {identification_account} не найден.")

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            money = request['money']
            cursor.execute("SELECT money FROM debit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                current_money = account[0]
                if current_money >= money:
                    cursor.execute("UPDATE debit_accounts SET money = money - ? WHERE identification_account = ?",
                                   (money, identification_account))
                    conn.commit()
                    print(f"Сумма {money} успешно списана со счета {identification_account}.")
                else:
                    print(f"Недостаточно средств на счете {identification_account}.")
            else:
                print(f"Счет {identification_account} не найден.")
