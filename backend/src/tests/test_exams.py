import pytest
from uuid import uuid4
from backend.src.database.models import Exam, Faculty, FacultyExamRequirement
from backend.src.applicants.service import ExamsService

@pytest.mark.asyncio
async def test_get_all_exams(async_session):
    exam1 = Exam(uuid=uuid4(), name="Русский язык", code="rus")
    exam2 = Exam(uuid=uuid4(), name="Математика", code="math")
    async_session.add_all([exam1, exam2])
    await async_session.commit()

    service = ExamsService(session=async_session)
    result = await service.get_all_exams()

    assert len(result.exams) == 2
    codes = {exam.code for exam in result.exams}
    assert "rus" in codes
    assert "math" in codes

@pytest.mark.asyncio
async def test_get_all_required_exams(async_session):
    faculty = Faculty(uuid=uuid4(), name="Инженерный")
    exam = Exam(uuid=uuid4(), name="Физика", code="phys")
    async_session.add_all([faculty, exam])
    await async_session.commit()

    requirement = FacultyExamRequirement(
        faculty_id=faculty.uuid,
        exam_id=exam.uuid,
        min_score=60
    )
    async_session.add(requirement)
    await async_session.commit()

    service = ExamsService(session=async_session)
    result = await service.get_all_required_exams()

    assert len(result.required_exams) == 1
    req_exam = result.required_exams[0]
    assert req_exam.faculty_id == faculty.uuid
    assert req_exam.faculty_name == "Инженерный"
    assert req_exam.exam_id == exam.uuid
    assert req_exam.exam_code == "phys"
    assert req_exam.min_score == 60
