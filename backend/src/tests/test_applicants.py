# backend/src/tests/test_applicants.py
import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_register_applicant(client: AsyncClient):

    response = await client.post("/backend/api/applicant/register/", json={
        "surname": "Ivanov",
        "name": "Ivan",
        "patronymic": "Ivanovich",
        "phone_number": "79123456789",
        "city": "Moscow",
        "applicants_exams": {"Русский язык", "Математика Профиль", "Матеи"}
    })
    assert response.status_code == 200
    data = response.json()
    assert UUID(data["uuid"])

@pytest.mark.asyncio
async def test_get_applicant_results(client: AsyncClient):

    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Petrov",
        "name": "Petr",
        "patronymic": "Petrovich",
        "phone_number": "79234567890",
        "city": "St. Petersburg"
    })

    uuid = register_resp.json()["uuid"]
    
    response = await client.get(f"/backend/api/applicant/{uuid}")
    assert response.status_code == 200
    assert response.json()["uuid"] == uuid

@pytest.mark.asyncio
async def test_process_user_answers(client: AsyncClient, test_data):
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Sidorov",
        "name": "Sidr",
        "patronymic": "Sidorovich",
        "phone_number": "79111234567",
        "city": "Kazan"
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

@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient, test_data):
    response = await client.get("/backend/api/questions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0