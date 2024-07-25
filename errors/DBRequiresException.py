class DBRequiresException(Exception):
    """Выкидывать при попытке списания баланса, когда его недостаточно"""

    def __init__(self,message):
        super().__init__(message)
        self.message = message
        pass

    def __str__(self):
        return f"DBRequiresException: {self.message} - проблема с БД"

