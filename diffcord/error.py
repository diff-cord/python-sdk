from aiohttp import ClientResponse


class DiffcordException(Exception):
    pass


class HTTPException(DiffcordException):
    def __init__(self, status_code: int, message: str, error_code: str):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        super().__init__(message)

    def __repr__(self):
        return f"<HTTPException status={self.status_code} message={self.message} error_code={self.error_code}>"

    def __str__(self):
        return self.__repr__()


class RateLimitException(HTTPException):
    def __init__(self, error: dict, response: ClientResponse):
        super().__init__(response.status, error["message"], error["code"])

    def __repr__(self):
        return f"<RateLimitException status={self.status_code} message={self.message} error_code={self.error_code}>"

    def __str__(self):
        return self.__repr__()


class ServerException(HTTPException):
    def __init__(self, error: dict, response: ClientResponse):
        super().__init__(response.status, error["message"], error["code"])

    def __repr__(self):
        return f"<ServerException status={self.status_code} message={self.message} error_code={self.error_code}>"

    def __str__(self):
        return self.__repr__()


class MissingTokenException(HTTPException):
    def __init__(self, error: dict, response: ClientResponse):
        super().__init__(response.status, error["message"], error["code"])

    def __repr__(self):
        return f"<MissingTokenException status={self.status_code} message={self.message} error_code={self.error_code}>"

    def __str__(self):
        return self.__repr__()


class InvalidTokenException(HTTPException):

    def __init__(self, error: dict, response: ClientResponse):
        super().__init__(response.status, error["message"], error["code"])

    def __repr__(self):
        return f"<InvalidTokenException status={self.status_code} message={self.message} error_code={self.error_code}>"

    def __str__(self):
        return self.__repr__()

