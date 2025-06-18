import pytest
from uuid import uuid4
from ..database.models import Exam, Faculty, FacultyExamRequirement
from ..applicants.service import ExamsService

@pytest.mark.asyncio
async def test_get_all_exams(async_session):
    # Добавляем экзамены
    exam1 = Exam(uuid=uuid4(), name="Русский язык", code="rus")
    exam2 = Exam(uuid=uuid4(), name="Математика", code="math")
    async_session.add_all([exam1, exam2])
    await async_session.commit()

    # Создаем сервис и вызываем метод
    service = ExamsService(session=async_session)
    result = await service.get_all_exams()

    # Проверки
    assert len(result.exams) == 2
    codes = {exam.code for exam in result.exams}
    assert "rus" in codes
    assert "math" in codes


@pytest.mark.asyncio
async def test_get_all_required_exams(async_session):
    # Добавляем факультет и экзамен
    faculty = Faculty(uuid=uuid4(), name="Инженерный")
    exam = Exam(uuid=uuid4(), name="Физика", code="phys")
    async_session.add_all([faculty, exam])
    await async_session.commit()

    # Добавляем требование
    requirement = FacultyExamRequirement(
        faculty_id=faculty.uuid,
        exam_id=exam.uuid,
        min_score=60
    )
    async_session.add(requirement)
    await async_session.commit()

    # Создаем сервис и вызываем метод
    service = ExamsService(session=async_session)
    result = await service.get_all_required_exams()

    # Проверки
    assert len(result.required_exams) == 1
    req_exam = result.required_exams[0]
    assert req_exam.faculty_id == faculty.uuid
    assert req_exam.faculty_name == "Инженерный"
    assert req_exam.exam_id == exam.uuid
    assert req_exam.exam_code == "phys"
    assert req_exam.min_score == 60
