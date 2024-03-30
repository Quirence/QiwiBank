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
                return False

    class OpenAccount:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT * FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                print(f"Аккаунт с идентификационным номером {IdentificationAccount} уже существует.")
            else:
                BIC = request['BIC']
                StatusDeposit = request.get('StatusDeposit', 'DEFAULT')
                PayTime = request.get('PayTime', 0)
                Money = request.get('Money', 0)
                TimeActive = int(request.get('TimeActive', datetime.now().timestamp()))
                LastPayTime = request.get('LastPayTime', datetime.now().strftime('%s'))
                TimeClose = TimeActive + request.get('TimeClose', 0)
                cursor.execute("INSERT INTO deposit_accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               (IdentificationAccount, Money, BIC, StatusDeposit, TimeActive, LastPayTime, PayTime,
                                TimeClose))
                conn.commit()
                print(f"Счет {IdentificationAccount} успешно открыт.")

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
                else:
                    print(f"Счет {IdentificationAccount} не найден.")
            else:
                print('Депозит должен быть деактивирован, чтобы его возможно было закрыть.')

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
                return True
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return False

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
                        return True
                    else:
                        print(f"Недостаточно средств на счете {IdentificationAccount}.")
                        return False
                else:
                    print(
                        f"Списание средств с депозита {IdentificationAccount} невозможно, так как статус депозита: {StatusDeposit}.")
                    return False
            else:
                print(f"Счет {IdentificationAccount} не найден.")
                return False

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
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute(
                "SELECT TimeActive,"
                "LastPayTime,"
                "PayTime,"
                "TimeClose,"
                "StatusDeposit FROM deposit_accounts WHERE IdentificationAccount = ?",
                (IdentificationAccount,))
            account = cursor.fetchone()
            if account:
                TimeActive, LastPayTime, PayTime, TimeClose, StatusDeposit = account
                if StatusDeposit == 'ON':
                    current_time = int(datetime.now().strftime('%s'))
                    if int(current_time) - int(LastPayTime) >= int(PayTime):
                        Money = request['Money']
                        BIC = request['BIC']
                        get_money_request = {
                            'request': 'GetMoney',
                            'IdentificationAccount': IdentificationAccount,
                            'Money': Money
                        }
                        MethodDeposit.AnalyzeRequest()(get_money_request, cursor, conn)
                        cursor.execute("UPDATE deposit_accounts SET LastPayTime = ? WHERE IdentificationAccount = ?",
                                       (current_time, IdentificationAccount,))
                        conn.commit()
                        print(f"Время последнего зачисления для счета {IdentificationAccount} успешно обновлено.")
                    if current_time > TimeClose:
                        set_off_request = {'request': 'SetOff', 'IdentificationAccount': IdentificationAccount}
                        MethodDeposit.AnalyzeRequest()(set_off_request, cursor, conn)
                        print(f"Ваш депозитный счет успешно закрыт")
                else:
                    print(f"Депозит {IdentificationAccount} не активен.")
            else:
                print(f"Счет {IdentificationAccount} не найден.")

    class GetBalance:
        def __call__(self, request, cursor, conn):
            IdentificationAccount = request['IdentificationAccount']
            cursor.execute("SELECT Money, StatusDeposit FROM deposit_accounts WHERE IdentificationAccount = ?",
                           (IdentificationAccount,))
            money = cursor.fetchone()
            if money:
                return int(money[0]), str(money[1])
            else:
                print('Счёта с указанными данными не существует.')
