import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.asyncio
async def test_get_all_exams(client: AsyncClient, test_data):
    response = await client.get("/backend/api/exam/")
    assert response.status_code == 200
    data = response.json()
    assert "exams" in data
    assert isinstance(data["exams"], list)
    assert len(data["exams"]) == 2  # Мы создаем 2 экзамена в фикстуре

    # Проверяем структуру каждого экзамена
    for exam in data["exams"]:
        assert "uuid" in exam
        assert "name" in exam
        assert "code" in exam
        assert isinstance(exam["name"], str)
        assert isinstance(exam["code"], str)


@pytest.mark.asyncio
async def test_get_all_required_exams(client: AsyncClient, test_data):
    response = await client.get("/backend/api/exam/required")
    assert response.status_code == 200
    data = response.json()
    assert "required_exams" in data
    assert isinstance(data["required_exams"], list)

    # Проверяем, что есть хотя бы одно требование (мы создаем 1 в фикстуре)
    assert len(data["required_exams"]) == 1

    # Проверяем структуру данных
    requirement = data["required_exams"][0]
    assert "faculty_id" in requirement
    assert "faculty_name" in requirement
    assert "exam_id" in requirement
    assert "exam_code" in requirement
    assert "min_score" in requirement

    # Проверяем конкретные значения из фикстуры
    assert requirement["exam_code"] == "rus"
    assert requirement["min_score"] == 60


@pytest.mark.asyncio
async def test_register_with_invalid_exam(client: AsyncClient, test_data):
    response = await client.post("/backend/api/applicant/register/", json={
        "surname": "Иванов",
        "name": "Иван",
        "phone_number": "79001234567",
        "exams": [
            {
                "exam_id": "00000000-0000-0000-0000-000000000000",  # Несуществующий экзамен
                "exam_name": "Несуществующий экзамен",
                "exam_code": "invalid",
                "score": 80
            }
        ]
    })
    assert response.status_code == 400
    assert "Exam with id" in response.json()["detail"]