from fastapi.testclient import TestClient
from fastapi import status

from prof_test_kubsau.server import app

client = TestClient(app)

API_URL = "/api/test/result/"


def test_result_true():
    """
    Arrange: Валидные данные,объект есть в базе
    Act: Запрос получения результатов
    Assert: API вернула статус 200 и корректный JSON
    """
    response = client.post(
        API_URL,
        json={
            "surname": "Ivanov",
            "name": "Ivan",
            "patronymic": "Ivanovich",
            "phone_number": "79000000000",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "surname": "Ivanov",
      "name": "Ivan",
      "patronymic": "Ivanovich",
      "phone_number": "79000000000",
    }


def test_result_false():
    response = client.post(API_URL)

    assert response.status_code == status.HTTP_404_NOT_FOUND
