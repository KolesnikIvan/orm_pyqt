'''Error exceptions'''

class IncorrectDataReceived(Exception):
    def __str__(self):
        return 'got incorrect message'

class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class NonDictInputError(Exception):
    def __str__(self):
        return 'func argument must be a dict'

class MissingReqField(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'no field {self.missing_field} in a dict'
