import sqlite3


class MethodDeposit:

    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['request']
            try:
                method = getattr(MethodDeposit, request_type)()
                method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT * FROM deposit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {identification_account} уже существует.")
            else:
                money = request['money']
                BIC = request['BIC']
                deposit_status = request['deposit_status']
                cursor.execute("INSERT INTO deposit_accounts VALUES (?, ?, ?, ?)",
                               (identification_account, money, BIC, deposit_status))
                conn.commit()
                print(f"Счет {identification_account} успешно открыт.")

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT * FROM deposit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                cursor.execute("DELETE FROM deposit_accounts WHERE identification_account = ?",
                               (identification_account,))
                conn.commit()
                print(f"Счет {identification_account} успешно закрыт.")
            else:
                print(f"Счет {identification_account} не найден.")

    class GetMoney:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            money = request['money']
            cursor.execute("SELECT * FROM deposit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                cursor.execute("UPDATE deposit_accounts SET money = money + ? WHERE identification_account = ?",
                               (money, identification_account))
                conn.commit()
                print(f"Сумма {money} успешно зачислена на счет {identification_account}.")
            else:
                print(f"Счет {identification_account} не найден.")

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            money = request['money']
            cursor.execute("SELECT money, status_deposit FROM deposit_accounts WHERE identification_account = ?",
                           (identification_account,))
            account = cursor.fetchone()
            if account:
                current_money, status_deposit = account
                if status_deposit == 'OFF':
                    if current_money >= money:
                        cursor.execute("UPDATE deposit_accounts SET money = money - ? WHERE identification_account = ?",
                                       (money, identification_account))
                        conn.commit()
                        print(f"Сумма {money} успешно списана со счета {identification_account}.")
                    else:
                        print(f"Недостаточно средств на счете {identification_account}.")
                else:
                    print(
                        f"Списание средств с депозита {identification_account} невозможно, так как статус депозита: {status_deposit}.")
            else:
                print(f"Счет {identification_account} не найден.")

    class SetOn:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT status_deposit FROM deposit_accounts WHERE identification_account = ?",
                           (identification_account,))
            current_status = cursor.fetchone()
            if current_status and current_status[0] != 'ON':
                cursor.execute("UPDATE deposit_accounts SET status_deposit = 'ON' WHERE identification_account = ?",
                               (identification_account,))
                conn.commit()
                print(f"Статус депозита для счета {identification_account} успешно изменен на 'ON'.")
            elif current_status and current_status[0] == 'ON':
                print(f"Статус депозита для счета {identification_account} уже установлен как 'ON'.")
            else:
                print(f"Счет {identification_account} не найден.")

    class SetOff:
        def __call__(self, request, cursor, conn):
            identification_account = request['identification_account']
            cursor.execute("SELECT status_deposit FROM deposit_accounts WHERE identification_account = ?",
                           (identification_account,))
            current_status = cursor.fetchone()
            if current_status and current_status[0] != 'OFF':
                cursor.execute("UPDATE deposit_accounts SET status_deposit = 'OFF' WHERE identification_account = ?",
                               (identification_account,))
                conn.commit()
                print(f"Статус депозита для счета {identification_account} успешно изменен на 'OFF'.")
            elif current_status and current_status[0] == 'OFF':
                print(f"Статус депозита для счета {identification_account} уже установлен как 'OFF'.")
            else:
                print(f"Счет {identification_account} не найден.")


