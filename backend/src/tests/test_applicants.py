import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_register_applicant(client: AsyncClient, test_data):
    response = await client.post("/backend/api/applicant/register/", json={
        "surname": "Иванов",
        "name": "Иван",
        "patronymic": "Иванович",
        "phone_number": "79001234567",
        "city": "Краснодар",
        "exams": [
            {
                "exam_id": "236e43f1-6d9a-42d2-bf80-514e7ed3030c",
                "exam_name": "Русский язык",
                "exam_code": "rus",
                "score": 80
            },
            {
                "exam_id": "bde589f5-c13e-4606-ad55-c394038091b8",
                "exam_name": "Математика (базовая)",
                "exam_code": "math_basic",
                "score": 75
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert UUID(data["uuid"])
    # Проверяем, что экзамены сохранились
    get_response = await client.get(f"/backend/api/applicant/{data['uuid']}")
    assert len(get_response.json()["exams"]) == 2

@pytest.mark.asyncio
async def test_get_applicant_results(client: AsyncClient, test_data):
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Петров",
        "name": "Петр",
        "patronymic": "Петрович",
        "phone_number": "79234567890",
        "city": "Санкт-Петербург",
        "exams": [
            {
                "exam_id": "236e43f1-6d9a-42d2-bf80-514e7ed3030c",
                "exam_name": "Русский язык",
                "exam_code": "rus",
                "score": 85
            }
        ]
    })
    uuid = register_resp.json()["uuid"]
    response = await client.get(f"/backend/api/applicant/{uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == uuid
    # Проверяем, что экзамены возвращаются в ответе
    assert len(data["exams"]) == 1
    assert data["exams"][0]["exam_code"] == "rus"

@pytest.mark.asyncio
async def test_process_user_answers(client: AsyncClient, test_data):
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Сидоров",
        "name": "Сидор",
        "patronymic": "Сидорович",
        "phone_number": "79111234567",
        "city": "Казань",
        "exams": [
            {
                "exam_id": "236e43f1-6d9a-42d2-bf80-514e7ed3030c",
                "exam_name": "Русский язык",
                "exam_code": "rus",
                "score": 70
            }
        ]
    })
    uuid = register_resp.json()["uuid"]

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
    assert response.status_code == 201
    data = response.json()
    assert data["uuid"] == uuid
    assert len(data["faculty_type"]) > 0
    # Проверяем, что экзамены остались в ответе
    assert len(data["exams"]) == 1

@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient, test_data):
    response = await client.get("/backend/api/questions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "answers" in data[0]
    assert len(data[0]["answers"]) > 0