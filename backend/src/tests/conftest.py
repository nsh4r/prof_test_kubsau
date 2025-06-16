import asyncio
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from uuid import UUID, uuid4

from backend.src.database.main import get_session
from backend.src.__init__ import app
from backend.src.config import settings
from backend.src.database.models import (
    Applicant, Faculty, ApplicantFaculty,
    FacultyType, Question, Answer, AnswerFaculty,
    Exam, FacultyExamRequirement, ApplicantExam
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
        # Создаем тестовые экзамены
        exam1 = Exam(uuid=UUID("44444444-4444-4444-4444-444444444444"),
                     name="Математика (профиль)",
                     code="math_profile")
        exam2 = Exam(uuid=UUID("55555555-5555-5555-5555-555555555555"),
                     name="Информатика",
                     code="informatics")
        exam3 = Exam(uuid=UUID("66666666-6666-6666-6666-666666666666"),
                     name="Русский язык",
                     code="russian")

        session.add(exam1)
        session.add(exam2)
        session.add(exam3)
        await session.commit()

        # Создаем тестовые данные факультетов
        faculty_type1 = FacultyType(uuid=UUID("11111111-1111-1111-1111-111111111111"),
                                    name="Технический")
        faculty_type2 = FacultyType(uuid=UUID("22222222-2222-2222-2222-222222222222"),
                                    name="Гуманитарный")

        session.add(faculty_type1)
        session.add(faculty_type2)
        await session.commit()

        # Создаем факультеты
        faculty1 = Faculty(uuid=UUID("77777777-7777-7777-7777-777777777777"),
                           name="Информационные системы",
                           url="https://example.com/is",
                           type_id=faculty_type1.uuid)
        faculty2 = Faculty(uuid=UUID("88888888-8888-8888-8888-888888888888"),
                           name="Филология",
                           url="https://example.com/philology",
                           type_id=faculty_type2.uuid)

        session.add(faculty1)
        session.add(faculty2)
        await session.commit()

        # Добавляем требования по экзаменам для факультетов
        requirement1 = FacultyExamRequirement(
            faculty_id=faculty1.uuid,
            exam_id=exam1.uuid,
            min_score=60
        )
        requirement2 = FacultyExamRequirement(
            faculty_id=faculty1.uuid,
            exam_id=exam2.uuid,
            min_score=70
        )
        requirement3 = FacultyExamRequirement(
            faculty_id=faculty2.uuid,
            exam_id=exam3.uuid,
            min_score=65
        )

        session.add(requirement1)
        session.add(requirement2)
        session.add(requirement3)
        await session.commit()

        # Создаем вопрос
        question = Question(uuid=UUID("11111111-1111-1111-1111-111111111111"),
                            text="Тестовый вопрос")
        session.add(question)
        await session.commit()

        # Создаем ответы
        answer1 = Answer(uuid=UUID("22222222-2222-2222-2222-222222222222"),
                         text="Тестовый ответ 1",
                         question_id=question.uuid)
        answer2 = Answer(uuid=UUID("33333333-3333-3333-3333-333333333333"),
                         text="Тестовый ответ 2",
                         question_id=question.uuid)

        session.add(answer1)
        session.add(answer2)
        await session.commit()

        # Создаем связи ответов с факультетами
        answer_faculty1 = AnswerFaculty(answer_id=answer1.uuid,
                                        faculty_type_id=faculty_type1.uuid,
                                        score=10)
        answer_faculty2 = AnswerFaculty(answer_id=answer2.uuid,
                                        faculty_type_id=faculty_type2.uuid,
                                        score=5)

        session.add(answer_faculty1)
        session.add(answer_faculty2)
        await session.commit()