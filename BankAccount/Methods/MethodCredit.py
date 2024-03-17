import sqlite3


class MethodCredit:

    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['request']
            try:
                method = getattr(MethodCredit, request_type)()
                method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT * FROM credit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {identification_account} уже существует.")
            else:
                money = request['money']
                BIC = request['BIC']
                credit_limit = request['credit_limit']
                rank = request['rank']
                cursor.execute("INSERT INTO credit_accounts VALUES (?, ?, ?, ?, ?)",
                               (identification_account, money, BIC, credit_limit, rank))
                conn.commit()
                print(f"Счет {identification_account} успешно открыт.")

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT * FROM credit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                cursor.execute("DELETE FROM credit_accounts WHERE identification_account = ?",
                               (identification_account,))
                conn.commit()
                print(f"Счет {identification_account} успешно закрыт.")
            else:
                print(f"Счет {identification_account} не найден.")

    class GetMoney:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            money = request['money']
            cursor.execute("SELECT * FROM credit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                cursor.execute("UPDATE credit_accounts SET money = money + ? WHERE identification_account = ?",
                               (money, identification_account))
                conn.commit()
                print(f"Сумма {money} успешно зачислена на счет {identification_account}.")
            else:
                print(f"Счет {identification_account} не найден.")

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            money = request['money']
            credit_limit = request['credit_limit']
            cursor.execute("SELECT money FROM credit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                current_money = account[0]
                if current_money + credit_limit >= money:
                    cursor.execute("UPDATE credit_accounts SET money = money - ? WHERE identification_account = ?",
                                   (money, identification_account))
                    conn.commit()
                    print(f"Сумма {money} успешно списана со счета {identification_account}.")
                else:
                    print(f"Недостаточно средств на счете {identification_account}.")
            else:
                print(f"Счет {identification_account} не найден.")
