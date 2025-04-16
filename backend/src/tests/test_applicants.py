# backend/src/tests/test_applicants.py
import pytest
from fastapi import status
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_post_result_by_data(session, client):
    """
    Тест для проверки POST запроса с результатами анкеты
    """
    response = await client.post("/backend/api/applicant/by-data/", json={
        "surname": "Иванов",
        "name": "Иван",
        "patronymic": "Иванович",
        "phone_number": "+79123456789",
        "city": "Москва"
    })
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["surname"] == "Иванов"
    assert result["name"] == "Иван"
    assert result["patronymic"] == "Иванович"
    assert result["phone_number"] == "+79123456789"

@pytest.mark.asyncio
async def test_process_user_answers(client, session):
    """
    Тест для POST запроса обработки ответов пользователя
    """
    data = {
        "uuid": "some-uuid",  # Используем реальный UUID абитуриента для теста
        "answers": [
            {
                "question_id": "ee1cb691-99b5-4b64-b5af-e97757c7b9ad",
                "answer_ids": ["418ec475-5604-4789-a90f-269c879ea9ed"]
            }
        ]
    }
    response = await client.post("/backend/api/results/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["uuid"] == data["uuid"]
    assert "faculty_type" in result
