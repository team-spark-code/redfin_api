"""커스텀 예외 클래스"""


class RedFinException(Exception):
    """기본 RedFin 예외"""
    pass


class NotFoundException(RedFinException):
    """리소스를 찾을 수 없음"""
    pass


class AlreadyExistsException(RedFinException):
    """리소스가 이미 존재함"""
    pass


class ValidationException(RedFinException):
    """데이터 검증 오류"""
    pass


class DatabaseException(RedFinException):
    """데이터베이스 오류"""
    pass

