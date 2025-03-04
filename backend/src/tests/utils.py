from typing import Final
from sqlalchemy.orm import scoped_session, sessionmaker


Session = scoped_session(sessionmaker())


class TestConstants:
    """Константные значения для тестов"""

    PHONE: Final[str] = '79000000000'
