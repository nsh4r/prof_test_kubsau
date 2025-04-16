import pytest
from httpx import AsyncClient
from backend.src.__init__ import app
from fastapi import HTTPException, status

@pytest.mark.asyncio
async def test_post_result_by_data(session):
    """
    Тест для проверки POST запроса с результатами анкеты
    """
    # создаем клиента
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # отправляем запрос
        response = await ac.post("/api/test/answers/", json={
            "surname": "Иванов",
            "name": "Иван",
            "patronymic": "Иванович",
            "phone_number": "+79123456789",
            "answers": [1, 2, 3, 4, 5, 1, 2]
        })
        # проверяем статус
        assert response.status_code == 200
        # можно добавить проверку тела ответа, если нужно:
        # assert response.json() == {"expected": "value"}

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
    assert "faculty_type" in result
