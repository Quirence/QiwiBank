import sqlite3


class MethodDebit:
    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['request']
            try:
                method = getattr(MethodDebit, request_type)()
                return method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")
                return False

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM debit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {IdentificationAccount} уже существует.")
            else:
                BIC = request['BIC']
                Money = request.get('Money', 'DEFAULT')
                cursor.execute("INSERT INTO debit_accounts VALUES (?, ?, ?)",
                               (IdentificationAccount, Money, BIC))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно открыт.")

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM debit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                cursor.execute("DELETE FROM debit_accounts WHERE IdentificationAccount = ?",
                               (IdentificationAccount,))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно закрыт.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class GetMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT * FROM debit_accounts WHERE IdentificationAccount = ?", (IdentificationAccount,))
            account_exists = cursor.fetchone()
            if account_exists:
                cursor.execute("UPDATE debit_accounts SET Money = Money + ? WHERE IdentificationAccount = ?",
                               (Money, IdentificationAccount))
                conn.commit()
                print(f"Сумма {Money} успешно зачислена на счет {IdentificationAccount}.")
                return True
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return False

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT Money FROM debit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                CurrentMoney = account[0]
                if CurrentMoney >= Money:
                    cursor.execute("UPDATE debit_accounts SET Money = Money - ? WHERE IdentificationAccount = ?",
                                   (Money, IdentificationAccount))
                    conn.commit()
                    print(f"Сумма {Money} успешно списана со счета {IdentificationAccount}.")
                    return True
                else:
                    print(f"Недостаточно средств на счете {IdentificationAccount}.")
                    return False
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return False

    class GetBalance:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT Money FROM debit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            money = cursor.fetchone()
            if money:
                # Возвращаем баланс в виде строки
                return int(money[0])
            else:
                print("Счёта с указанными данными не существует.")
                return None
