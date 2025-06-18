import pytest
from httpx import AsyncClient
from uuid import UUID

from backend.src.database.models import Faculty, FacultyExamRequirement


@pytest.mark.asyncio
async def test_get_all_exams(client: AsyncClient, test_data):
    response = await client.get("/backend/api/exam/")
    assert response.status_code == 200
    data = response.json()
    assert "exams" in data
    assert isinstance(data["exams"], list)
    assert len(data["exams"]) == 2
    assert data["exams"][0]["code"] in ["rus", "math_basic"]


@pytest.mark.asyncio
async def test_get_all_required_exams(client: AsyncClient, test_data):
    # Сначала создадим факультет и требования
    async with client.app.state.session_factory() as session:
        faculty = Faculty(
            uuid=UUID("44444444-4444-4444-4444-444444444444"),
            name="Информационные системы",
            url="https://example.com",
            type_id=UUID("11111111-1111-1111-1111-111111111111")
        )
        session.add(faculty)

        requirement = FacultyExamRequirement(
            faculty_id=faculty.uuid,
            exam_id=UUID("236e43f1-6d9a-42d2-bf80-514e7ed3030c"),
            min_score=60
        )
        session.add(requirement)
        await session.commit()

    response = await client.get("/backend/api/exam/required")
    assert response.status_code == 200
    data = response.json()
    assert "required_exams" in data
    assert isinstance(data["required_exams"], list)
    assert len(data["required_exams"]) > 0
    assert data["required_exams"][0]["exam_code"] == "rus"
    assert data["required_exams"][0]["min_score"] == 60


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