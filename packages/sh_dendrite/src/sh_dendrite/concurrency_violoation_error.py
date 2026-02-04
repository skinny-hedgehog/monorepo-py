class ConcurrencyViolationError(Exception):
    def __init__(self, message: str, code: str, reason: str) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
