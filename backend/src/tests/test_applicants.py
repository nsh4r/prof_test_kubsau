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
        "exams": [
            {
                "exam_id": "44444444-4444-4444-4444-444444444444",
                "exam_name": "Математика (профиль)",
                "exam_code": "math_profile",
                "score": 75
            }
        ]
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
        "city": "St. Petersburg",
        "exams": [
            {
                "exam_id": "44444444-4444-4444-4444-444444444444",
                "exam_name": "Математика (профиль)",
                "exam_code": "math_profile",
                "score": 80
            },
            {
                "exam_id": "55555555-5555-5555-5555-555555555555",
                "exam_name": "Информатика",
                "exam_code": "informatics",
                "score": 85
            }
        ]
    })

    uuid = register_resp.json()["uuid"]

    response = await client.get(f"/backend/api/applicant/{uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == uuid
    assert len(data["exams"]) == 2
    assert data["exams"][0]["exam_name"] == "Математика (профиль)"
    assert data["exams"][0]["score"] == 80


@pytest.mark.asyncio
async def test_process_user_answers(client: AsyncClient, test_data):
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Sidorov",
        "name": "Sidr",
        "patronymic": "Sidorovich",
        "phone_number": "79111234567",
        "city": "Kazan",
        "exams": [
            {
                "exam_id": "66666666-6666-6666-6666-666666666666",
                "exam_name": "Русский язык",
                "exam_code": "russian",
                "score": 90
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


@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient, test_data):
    response = await client.get("/backend/api/questions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_all_exams(client: AsyncClient, test_data):
    response = await client.get("/backend/api/exams/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["exams"], list)
    assert len(data["exams"]) == 3
    assert data["exams"][0]["name"] == "Математика (профиль)"


@pytest.mark.asyncio
async def test_get_required_exams(client: AsyncClient, test_data):
    faculty_id = "77777777-7777-7777-7777-777777777777"
    response = await client.get(f"/backend/api/faculty/{faculty_id}/required-exams")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["required_exams"], list)
    assert len(data["required_exams"]) == 2
    assert data["required_exams"][0]["min_score"] == 60
    assert data["required_exams"][0]["faculty_name"] == "Информационные системы"


@pytest.mark.asyncio
async def test_update_applicant_exams(client: AsyncClient):
    # Сначала регистрируем абитуриента без экзаменов
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Fedorov",
        "name": "Fedor",
        "patronymic": "Fedorovich",
        "phone_number": "79112223344",
        "city": "Novosibirsk"
    })
    uuid = register_resp.json()["uuid"]

    # Обновляем данные с экзаменами
    update_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Fedorov",
        "name": "Fedor",
        "patronymic": "Fedorovich",
        "phone_number": "79112223344",
        "city": "Novosibirsk",
        "exams": [
            {
                "exam_id": "55555555-5555-5555-5555-555555555555",
                "exam_name": "Информатика",
                "exam_code": "informatics",
                "score": 88
            }
        ]
    })
    assert update_resp.status_code == 200

    # Проверяем, что экзамены обновились
    get_resp = await client.get(f"/backend/api/applicant/{uuid}")
    data = get_resp.json()
    assert len(data["exams"]) == 1
    assert data["exams"][0]["score"] == 88