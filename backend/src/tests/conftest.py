import asyncio
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from uuid import UUID

from backend.src.database.main import get_session
from backend.src.__init__ import app
from backend.src.config import settings
from backend.src.database.models import (
    Applicant, Faculty, ApplicantFaculty,
    FacultyType, Question, Answer, AnswerFaculty, Exam, FacultyExamRequirement
)

DATABASE_URL = settings.postgres_url

test_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture()
async def client(prepare_database):
    async def override_get_session():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture()
async def test_data():
    async with TestSessionLocal() as session:
        # Типы факультетов
        faculty_type1 = FacultyType(uuid=UUID("11111111-1111-1111-1111-111111111111"), name="Технический")
        faculty_type2 = FacultyType(uuid=UUID("22222222-2222-2222-2222-222222222222"), name="Гуманитарный")
        session.add_all([faculty_type1, faculty_type2])
        await session.commit()

        # Факультеты
        faculty1 = Faculty(
            uuid=UUID("33333333-3333-3333-3333-333333333333"),
            name="Факультет информатики",
            url="https://example.com/info",
            type_id=faculty_type1.uuid
        )
        session.add(faculty1)
        await session.commit()

        # Требования факультета к экзаменам
        exam_requirement = FacultyExamRequirement(
            faculty_id=faculty1.uuid,
            exam_id=UUID("236e43f1-6d9a-42d2-bf80-514e7ed3030c"),
            min_score=60
        )
        session.add(exam_requirement)
        await session.commit()

        # Остальные данные (вопросы, ответы и т.д.) остаются как были
        question = Question(uuid=UUID("11111111-1111-1111-1111-111111111111"), text="Тестовый вопрос")
        session.add(question)
        await session.commit()

        answer1 = Answer(uuid=UUID("22222222-2222-2222-2222-222222222222"), text="Тестовый ответ 1", question_id=question.uuid)
        answer2 = Answer(uuid=UUID("33333333-3333-3333-3333-333333333333"), text="Тестовый ответ 2", question_id=question.uuid)
        session.add_all([answer1, answer2])
        await session.commit()

        answer_faculty1 = AnswerFaculty(answer_id=answer1.uuid, faculty_type_id=faculty_type1.uuid, score=10)
        answer_faculty2 = AnswerFaculty(answer_id=answer2.uuid, faculty_type_id=faculty_type2.uuid, score=5)
        session.add_all([answer_faculty1, answer_faculty2])
        await session.commit()

        # Экзамены
        exam1 = Exam(uuid=UUID("236e43f1-6d9a-42d2-bf80-514e7ed3030c"), name="Русский язык", code="rus")
        exam2 = Exam(uuid=UUID("bde589f5-c13e-4606-ad55-c394038091b8"), name="Математика (базовая)", code="math_basic")
        session.add_all([exam1, exam2])
        await session.commit()
