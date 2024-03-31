import sqlite3
from datetime import datetime


class MethodDeposit:
    class AnalyzeRequest:
        def __call__(self, request, cursor, conn):
            request_type = request['request']
            try:
                method = getattr(MethodDeposit, request_type)()
                return method(request, cursor, conn)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")
                return {"status": "failed"}

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM deposit_accounts WHERE IdentificationAccount = ?", (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {IdentificationAccount} уже существует.")
                return {"status": "failed"}
            else:
                BIC = request['BIC']
                StatusDeposit = request.get('StatusDeposit', 'DEFAULT')
                PayTime = request.get('PayTime', 0)
                Money = request.get('Money', 0)
                TimeActive = int(request.get('TimeActive', datetime.now().timestamp()))
                LastPayTime = request.get('LastPayTime', datetime.now().strftime('%S'))
                TimeClose = TimeActive + request.get('TimeClose', 0)
                Percent = request.get('Percent', 0)
                cursor.execute("INSERT INTO deposit_accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (IdentificationAccount, Money, BIC, StatusDeposit, TimeActive, LastPayTime, PayTime,
                                TimeClose, Percent))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно открыт.")
                return {"status": "success"}

    class CloseAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account[3] != 'ON':
                if account:
                    cursor.execute("DELETE FROM deposit_accounts WHERE IdentificationAccount = ?",
                                   (IdentificationAccount,))
                    conn.commit()
                    print(f"Счет {IdentificationAccount} успешно закрыт.")
                    return {"status": "success"}
                else:
                    print(f"Счет {IdentificationAccount} не найден.")
                    return {"status": "failed"}
            else:
                print('Депозит должен быть деактивирован, чтобы его возможно было закрыть.')
                return {"status": "failed"}

    class GetMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT * FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                cursor.execute("UPDATE deposit_accounts SET Money = Money + ? WHERE IdentificationAccount = ?",
                               (Money, IdentificationAccount))
                conn.commit()
                print(f"Сумма {Money} успешно зачислена на счет {IdentificationAccount}.")
                return {"status": "success"}
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return {"status": "failed"}

    class GiveMoney:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            Money = request['Money']
            cursor.execute("SELECT Money, StatusDeposit FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                CurrentMoney, StatusDeposit = account
                if StatusDeposit == 'OFF':
                    if CurrentMoney >= Money:
                        cursor.execute("UPDATE deposit_accounts SET Money = Money - ? WHERE IdentificationAccount = ?",
                                       (Money, IdentificationAccount))
                        conn.commit()
                        print(f"Сумма {Money} успешно списана со счета {IdentificationAccount}.")
                        return {"status": "success"}
                    else:
                        print(f"Недостаточно средств на счете {IdentificationAccount}.")
                        return {"status": "failed"}
                else:
                    print(
                        f"Списание средств с депозита {IdentificationAccount} невозможно, так как статус депозита: {StatusDeposit}.")
                    return {"status": "failed"}
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return {"status": "failed"}

    class SetOn:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT StatusDeposit FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            current_status = cursor.fetchone()
            if current_status and current_status[0] != 'ON':
                cursor.execute("UPDATE deposit_accounts SET StatusDeposit = 'ON' WHERE IdentificationAccount = ?",
                               (IdentificationAccount,))
                conn.commit()
                print(f"Статус депозита для счета {IdentificationAccount} успешно изменен на 'ON'.")
            elif current_status and current_status[0] == 'ON':
                print(f"Статус депозита для счета {IdentificationAccount} уже установлен как 'ON'.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class SetOff:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT StatusDeposit FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            current_status = cursor.fetchone()
            if current_status and current_status[0] != 'OFF':
                cursor.execute("UPDATE deposit_accounts SET StatusDeposit = 'OFF' WHERE IdentificationAccount = ?",
                               (IdentificationAccount,))
                conn.commit()
                print(f"Статус депозита для счета {IdentificationAccount} успешно изменен на 'OFF'.")
            elif current_status and current_status[0] == 'OFF':
                print(f"Статус депозита для счета {IdentificationAccount} уже установлен как 'OFF'.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class PayDeposit:
        def __call__(self, request, cursor, conn):
            cursor.execute(
                "SELECT IdentificationAccount,"
                "TimeActive,"
                "LastPayTime,"
                "PayTime,"
                "TimeClose,"
                "StatusDeposit,"
                "Money,"
                "Percent FROM deposit_accounts")
            accounts = cursor.fetchall()
            current_time = int(datetime.now().strftime('%S'))
            for account in accounts:
                IdentificationAccount, TimeActive, LastPayTime, PayTime, TimeClose, StatusDeposit, Money, Percent = account
                if StatusDeposit == 'ON':
                    if int(current_time) - int(LastPayTime) >= int(PayTime):
                        new_balance = Money * Percent / 100 + Money
                        cursor.execute(
                            "UPDATE deposit_accounts SET Money = ?, LastPayTime = ? WHERE IdentificationAccount = ?",
                            (new_balance, current_time, IdentificationAccount))
                        conn.commit()
                        print(f"Счет {IdentificationAccount} успешно оплачен. Новый баланс: {new_balance}")
                    if current_time > TimeClose:
                        set_off_request = {'request': 'SetOff', 'IdentificationAccount': IdentificationAccount}
                        MethodDeposit.AnalyzeRequest()(set_off_request, cursor, conn)
                        print(f"Ваш депозитный счет {IdentificationAccount} успешно закрыт")
                else:
                    print(f"Депозит {IdentificationAccount} не активен.")

    class GetBalance:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT Money FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            money = cursor.fetchone()
            if money:
                return int(money[0])
            else:
                return None
