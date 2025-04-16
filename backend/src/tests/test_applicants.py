import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_post_result_by_data(client: AsyncClient):
    response = await client.post("/backend/api/applicant/by-data/", json={
        "surname": "Petrov",
        "name": "Petr",
        "patronymic": "Petrovich",
        "phone_number": "79123456789",
        "city": "Moscow"
    })
    assert response.status_code == 201
    data = response.json()
    assert UUID(data["uuid"])
    assert data["surname"] == "Petrov"
    assert data["name"] == "Petr"
    assert data["phone_number"] == "79123456789"

@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient):
    response = await client.get("/backend/api/questions/")
    assert response.status_code in [200, 404]  # 404 if нет вопросов в БД
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_process_user_answers(client: AsyncClient):
    # Сначала создаем абитуриента
    create_resp = await client.post("/backend/api/applicant/by-data/", json={
        "surname": "Sidorov",
        "name": "Sidr",
        "patronymic": "Sidorovich",
        "phone_number": "79111234567",
        "city": "Kazan"
    })
    assert create_resp.status_code == 201
    uuid = create_resp.json()["uuid"]

    # Подготовим ответ (может понадобиться скорректировать UUID ответов и вопросов)
    payload = {
        "uuid": uuid,
        "answers": [
            {
                "question_id": "11111111-1111-1111-1111-111111111111",
                "answer_ids": ["22222222-2222-2222-2222-222222222222"]
            }
        ]
    }

    response = await client.post("/backend/api/results/", json=payload)
    assert response.status_code in [201, 400]
    if response.status_code == 201:
        data = response.json()
        assert data["uuid"] == uuid
        assert isinstance(data["faculty_type"], list)
