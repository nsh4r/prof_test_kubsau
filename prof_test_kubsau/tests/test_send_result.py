import pytest
from fastapi.testclient import TestClient
from fastapi import status

from prof_test_kubsau.database import Base, engine, Result
from prof_test_kubsau.server import app
from prof_test_kubsau.tests.factories import ResultFactory
from prof_test_kubsau.tests.utils import TestConstants, Session

client = TestClient(app)

API_URL = "/api/test/result/"


@pytest.fixture(scope='module')
def db_session():
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def result() -> Result:
    """Результат прохождения теста"""
    return ResultFactory(name='Райан', surname='Гослинг', patronymic='', phone_number=TestConstants.PHONE)


def test_success(result: Result):
    """
    Arrange: Валидные данные,объект есть в базе
    Act: Запрос получения результатов
    Assert: API вернула статус 200 и корректный JSON
    """
    response = client.post(
        API_URL,
        json={
            'surname': result.surname,
            'name': result.name,
            'patronymic': result.patronymic,
            'phone_number': result.phone_number,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      'surname': result.surname,
      'name': result.name,
      'patronymic': result.patronymic,
      'phone_number': result.phone_number,
    }


@pytest.mark.parametrize('phone_number', [79000000000, '', '+79000000000'])
def test_validation_error(phone_number: str):
    """
    Arrange: Невалидный номер телефона.
    Act: Запрос к API на получение результатов.
    Assert: API вернуло 422.
    """
    response = client.post(
        API_URL,
        json={
            'surname': 'Ivanov',
            'name': 'Ivan',
            'patronymic': 'Ivanovich',
            'phone_number': phone_number,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
