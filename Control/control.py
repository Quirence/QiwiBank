
from database.UserMethod import User

class Bank:
    def __init__(self, frontend_info):
        # Инициализация банка - получение информации о пользователе по информации из фронтенда (логин и сессия)
        pass

    def create_account(self, account_type, user_info):
        # Проверяем, если метод регистрации, вызываем соответствующий метод класса User
        if user_info.get('method') == 'registration':
            # Создаем экземпляр класса User
            user_manager = User()
            # Вызываем метод добавления нового пользователя
            user_manager.treatment_request(user_info)
            return "User registered successfully."  # Возвращаем сообщение об успешной регистрации
        else:
            return "Invalid registration method."  # Возвращаем сообщение об ошибке, если метод регистрации неверен
