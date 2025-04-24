import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_register_applicant(client: AsyncClient):
    # Тест регистрации нового абитуриента
    response = await client.post("/backend/api/applicant/register/", json={
        "surname": "Ivanov",
        "name": "Ivan",
        "patronymic": "Ivanovich",
        "phone_number": "79123456789",
        "city": "Moscow"
    })
    assert response.status_code == 200
    data = response.json()
    assert UUID(data["uuid"])
    
    # Тест получения существующего абитуриента
    response_existing = await client.post("/backend/api/applicant/register/", json={
        "surname": "Ivanov",
        "name": "Ivan",
        "patronymic": "Ivanovich",
        "phone_number": "79123456789",
        "city": "Moscow"
    })
    assert response_existing.status_code == 200
    assert response_existing.json()["uuid"] == data["uuid"]

@pytest.mark.asyncio
async def test_get_applicant_results(client: AsyncClient):
    # Сначала регистрируем абитуриента
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Petrov",
        "name": "Petr",
        "patronymic": "Petrovich",
        "phone_number": "79234567890",
        "city": "St. Petersburg"
    })
    assert register_resp.status_code == 200
    uuid = register_resp.json()["uuid"]

    # Тест получения результатов (должен вернуть 200 даже без результатов)
    response = await client.get(f"/backend/api/applicant/{uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == uuid
    assert isinstance(data["faculty_type"], list)

    # Тест для несуществующего абитуриента
    invalid_uuid = "00000000-0000-0000-0000-000000000000"
    response_not_found = await client.get(f"/backend/api/applicant/{invalid_uuid}")
    assert response_not_found.status_code == 404

@pytest.mark.asyncio
async def test_process_user_answers(client: AsyncClient):
    # Сначала регистрируем абитуриента
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Sidorov",
        "name": "Sidr",
        "patronymic": "Sidorovich",
        "phone_number": "79111234567",
        "city": "Kazan"
    })
    assert register_resp.status_code == 200
    uuid = register_resp.json()["uuid"]

    # Подготовим тестовые данные
    payload = {
        "uuid": uuid,
        "answers": [
            {
                "question_id": "11111111-1111-1111-1111-111111111111",
                "answer_ids": ["22222222-2222-2222-2222-222222222222"]
            }
        ]
    }

    # Тест обработки ответов
    response = await client.post("/backend/api/results/", json=payload)
    assert response.status_code in [201, 400]
    if response.status_code == 201:
        data = response.json()
        assert data["uuid"] == uuid
        assert isinstance(data["faculty_type"], list)
        
        # Проверяем, что результаты появились
        results_resp = await client.get(f"/backend/api/applicant/{uuid}")
        assert results_resp.status_code == 200
        assert len(results_resp.json()["faculty_type"]) > 0

@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient):
    response = await client.get("/backend/api/questions/")
    assert response.status_code in [200, 404]  # 404 если нет вопросов в БД
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            question = data[0]
            assert "id" in question
            assert "question" in question
            assert "answers" in question
            assert isinstance(question["answers"], list)
            