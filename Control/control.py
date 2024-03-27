from QiwiBank.database.UserMethod import *


class Control:
    def __init__(self):
        self.user = User()
        self.user_analyzer = User.AnalyzeRequest()
        self.control_analyzer = self.AnalyzeRequest(self.user_analyzer)

    def treatment_request(self, request):
        return self.control_analyzer(request)

    class AnalyzeRequest:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request):
            request_type = request['method']
            try:
                method = getattr(Control, request_type)
                return method(self.user_analyzer)(request)
            except AttributeError:
                print(f"Unsupported request type: {request_type}")

    class Registration:
        def __init__(self, user_analyzer):  # Ensure this argument is passed correctly
            self.user_analyzer = user_analyzer

        def __call__(self, request):
            new_request = request.copy()
            new_request['request'] = 'AddUser'
            if self.user_analyzer(new_request):
                print("Registration successful.")
                return {'status': 'success', 'redirect': '/'}  # Redirect to the main page
            else:
                print("Registration failed.")
                return {'status': 'failed'}

    class Login:
        def __init__(self, user_analyzer):
            self.user_analyzer = user_analyzer

        def __call__(self, request):
            new_request = request.copy()
            new_request['request'] = 'GetPassword'
            password = request['password']
            stored_password = self.user_analyzer()(request)
            if stored_password == password:
                print("Authentication successful.")
                return {'status': 'success', 'redirect': '/main'}  # Redirect to the main page
            else:
                print("Incorrect password or email.")
                return {'status': 'failed'}
