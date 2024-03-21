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
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {IdentificationAccount} уже существует.")
            else:
                BIC = request['BIC']
                CreditLimit = request['CreditLimit']
                rank = request['rank']
                cursor.execute("INSERT INTO credit_accounts VALUES (?, ?, ?, ?)",
                               (IdentificationAccount, BIC, CreditLimit, rank))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно открыт.")

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                cursor.execute("DELETE FROM credit_accounts WHERE IdentificationAccount = ?",
                               (IdentificationAccount,))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно закрыт.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class GetMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT * FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                cursor.execute("UPDATE credit_accounts SET Money = Money + ? WHERE IdentificationAccount = ?",
                               (Money, IdentificationAccount))
                conn.commit()
                print(f"Сумма {Money} успешно зачислена на счет {IdentificationAccount}.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            CreditLimit = request['CreditLimit']
            cursor.execute("SELECT Money FROM credit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                CurrentMoney = account[0]
                if CurrentMoney + CreditLimit >= Money:
                    cursor.execute("UPDATE credit_accounts SET Money = Money - ? WHERE IdentificationAccount = ?",
                                   (Money, IdentificationAccount))
                    conn.commit()
                    print(f"Сумма {Money} успешно списана со счета {IdentificationAccount}.")
                else:
                    print(f"Недостаточно средств на счете {IdentificationAccount}.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")