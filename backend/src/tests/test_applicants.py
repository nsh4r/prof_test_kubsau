import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_get_questions(client: AsyncClient, test_data):
    response = await client.get("/backend/api/questions/")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    question = data[0]
    assert "id" in question
    assert "question" in question
    assert "answers" in question
    assert isinstance(question["answers"], list)
    assert len(question["answers"]) > 0

    answer = question["answers"][0]
    assert "id" in answer
    assert "text" in answer


@pytest.mark.asyncio
async def test_get_all_exams(client: AsyncClient, test_data):
    response = await client.get("/backend/api/exams/")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # мы создали 3 экзамена

    exam = data[0]
    assert "uuid" in exam
    assert "name" in exam
    assert "code" in exam


@pytest.mark.asyncio
async def test_get_required_exams(client: AsyncClient, test_data):
    faculty_id = "77777777-7777-7777-7777-777777777777"  # Информационные системы
    response = await client.get(f"/backend/api/faculty/{faculty_id}/required-exams/")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    exam_req = data[0]
    assert "exam_id" in exam_req
    assert "min_score" in exam_req
