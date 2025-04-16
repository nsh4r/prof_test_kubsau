import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_post_result_by_data(client, session):
    """Тест для /backend/api/applicant/by-data/"""
    data = {
        "surname": "Ivanov",
        "name": "Ivan",
        "patronymic": "Ivanovich",
        "phone_number": "79000000000",
        "city": "Krasnodar"
    }

    response = client.post("/backend/api/applicant/by-data/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["surname"] == data["surname"]
    assert result["name"] == data["name"]
    assert result["phone_number"] == data["phone_number"]
    assert result["city"] == data["city"]
    assert "uuid" in result  # UUID должен быть в ответе
    assert "faculty_type" in result  # Убедитесь, что результат включает факультеты


@pytest.mark.asyncio
async def test_process_user_answers(client, session):
    """Тест для /backend/api/results/"""
    data = {
        "uuid": "some-uuid",  # Используем реальный UUID абитуриента для теста
        "answers": [
            {
                "question_id": "ee1cb691-99b5-4b64-b5af-e97757c7b9ad",
                "answer_ids": ["418ec475-5604-4789-a90f-269c879ea9ed"]
            }
        ]
    }

    response = client.post("/backend/api/results/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["uuid"] == data["uuid"]
    assert "faculty_type" in result  # Убедитесь, что результат включает факультеты
