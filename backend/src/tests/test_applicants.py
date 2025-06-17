import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.asyncio
async def test_register_applicant(client: AsyncClient, test_data):
    """Тест регистрации абитуриента с экзаменами"""
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
    assert response.status_code == 200, response.text
    data = response.json()
    assert "uuid" in data
    assert UUID(data["uuid"])


@pytest.mark.asyncio
async def test_get_applicant_results(client: AsyncClient, test_data):
    """Тест получения результатов абитуриента"""
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
            }
        ]
    })
    assert register_resp.status_code == 200, register_resp.text
    uuid = register_resp.json()["uuid"]

    response = await client.get(f"/backend/api/applicant/{uuid}")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["uuid"] == uuid
    assert data["surname"] == "Petrov"
    assert any(exam["exam_id"] == "44444444-4444-4444-4444-444444444444" for exam in data.get("exams", []))


@pytest.mark.asyncio
async def test_process_user_answers(client: AsyncClient, test_data):
    """Тест обработки ответов пользователя"""
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Sidorov",
        "name": "Sidr",
        "patronymic": "Sidorovich",
        "phone_number": "79111234567",
        "city": "Kazan",
        "exams": []
    })
    assert register_resp.status_code == 200, register_resp.text
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
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["uuid"] == uuid
    assert "faculty_type" in data
    assert len(data["faculty_type"]) > 0


@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient, test_data):
    """Тест получения списка вопросов"""
    response = await client.get("/backend/api/questions/")
    assert response.status_code == 200, response.text
    data = response.json()

    # Ожидаем словарь с ключом "questions"
    assert isinstance(data, dict)
    assert "questions" in data
    questions = data["questions"]

    assert isinstance(questions, list)
    assert len(questions) > 0
    q = questions[0]
    assert "id" in q
    assert "question" in q
    assert "answers" in q
    assert isinstance(q["answers"], list)
    assert len(q["answers"]) > 0
    assert "id" in q["answers"][0]
    assert "text" in q["answers"][0]


@pytest.mark.asyncio
async def test_get_all_exams(client: AsyncClient, test_data):
    """Тест получения списка всех экзаменов"""
    response = await client.get("/backend/api/exams/")
    assert response.status_code == 200, response.text
    data = response.json()

    assert isinstance(data, dict)
    assert "exams" in data
    exams = data["exams"]
    assert isinstance(exams, list)
    assert len(exams) > 0
    exam = exams[0]
    assert "uuid" in exam
    assert "name" in exam
    assert "code" in exam


@pytest.mark.asyncio
async def test_get_required_exams(client: AsyncClient, test_data):
    """Тест получения списка требуемых экзаменов для факультета"""
    faculty_id = "77777777-7777-7777-7777-777777777777"
    response = await client.get(f"/backend/api/faculty/{faculty_id}/required-exams/")
    assert response.status_code == 200, response.text
    data = response.json()

    assert isinstance(data, dict)
    assert "required_exams" in data
    exams = data["required_exams"]
    assert isinstance(exams, list)
    assert len(exams) > 0
    exam = exams[0]
    assert "faculty_id" in exam
    assert "exam_id" in exam
    assert "min_score" in exam


@pytest.mark.asyncio
async def test_update_applicant_exams(client: AsyncClient, test_data):
    """Тест обновления экзаменов абитуриента"""
    register_resp = await client.post("/backend/api/applicant/register/", json={
        "surname": "Fedorov",
        "name": "Fedor",
        "patronymic": "Fedorovich",
        "phone_number": "79112223344",
        "city": "Novosibirsk",
        "exams": []
    })
    assert register_resp.status_code == 200, register_resp.text
    uuid = register_resp.json()["uuid"]

    get_resp = await client.get(f"/backend/api/applicant/{uuid}")
    assert get_resp.status_code == 200, get_resp.text
    assert len(get_resp.json().get("exams", [])) == 0

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
    assert update_resp.status_code == 200, update_resp.text

    get_resp = await client.get(f"/backend/api/applicant/{uuid}")
    assert get_resp.status_code == 200, get_resp.text
    data = get_resp.json()
    assert len(data.get("exams", [])) == 1
    assert data["exams"][0]["exam_id"] == "55555555-5555-5555-5555-555555555555"
    assert data["exams"][0]["score"] == 88
