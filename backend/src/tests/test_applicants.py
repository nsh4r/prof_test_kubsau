import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import select

from backend.src.__init__ import app
from backend.src.applicants.schemas import ResponseResult, ApplicantInfo, ApplicantAnswers
from backend.src.database.models import Applicant, FacultyType, Faculty, Question, Answer
from backend.src.tests.factories import (
    ApplicantFactory, FacultyTypeFactory, FacultyFactory,
    QuestionFactory, AnswerFactory, AnswerFacultyFactory
)
from backend.src.tests.utils import TestConstants


@pytest.fixture(scope="function")
def db_session_factory():
    """Fixture to provide session for factories"""
    from backend.src.database.main import async_engine
    from sqlalchemy.orm import sessionmaker

    sync_engine = async_engine.sync_engine
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True)
def setup_factories(db_session_factory):
    """Configure factories to use the test session"""
    from backend.src.tests import factories
    for factory in [
        factories.ApplicantFactory,
        factories.FacultyTypeFactory,
        factories.FacultyFactory,
        factories.QuestionFactory,
        factories.AnswerFactory,
        factories.ApplicantFacultyFactory,
        factories.AnswerFacultyFactory,
    ]:
        factory._meta.sqlalchemy_session = db_session_factory


@pytest.mark.asyncio
async def test_post_result_by_data_new_applicant(db_session_factory):
    # Create test data
    faculty_type = FacultyTypeFactory()
    faculty = FacultyFactory(type_id=faculty_type.uuid)

    async with AsyncClient(app=app, base_url="http://test") as client:
        applicant_data = ApplicantInfo(
            surname=TestConstants.SURNAME,
            name=TestConstants.NAME,
            patronymic=TestConstants.PATRONYMIC,
            phone_number=TestConstants.PHONE,
            city=TestConstants.CITY
        )

        response = await client.post(
            "/backend/api/applicant/by-data/",
            json=applicant_data.model_dump()
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["surname"] == TestConstants.SURNAME
        assert response_data["phone_number"] == TestConstants.PHONE


@pytest.mark.asyncio
async def test_post_result_by_data_existing_applicant(db_session_factory):
    # Create existing applicant
    existing_applicant = ApplicantFactory()

    async with AsyncClient(app=app, base_url="http://test") as client:
        updated_name = "UpdatedName"
        applicant_data = ApplicantInfo(
            surname=existing_applicant.surname,
            name=updated_name,
            patronymic=existing_applicant.patronymic,
            phone_number=existing_applicant.phone_number,
            city=existing_applicant.city
        )

        response = await client.post(
            "/backend/api/applicant/by-data/",
            json=applicant_data.model_dump()
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == updated_name


@pytest.mark.asyncio
async def test_process_user_answers(db_session_factory):
    # Create test data
    applicant = ApplicantFactory()
    question = QuestionFactory()
    answer1 = AnswerFactory(question_id=question.uuid)
    answer2 = AnswerFactory(question_id=question.uuid)
    faculty_type1 = FacultyTypeFactory()
    faculty_type2 = FacultyTypeFactory()
    AnswerFacultyFactory(
        answer_id=answer1.uuid,
        faculty_type_id=faculty_type1.uuid,
        score=3
    )
    AnswerFacultyFactory(
        answer_id=answer2.uuid,
        faculty_type_id=faculty_type2.uuid,
        score=5
    )
    FacultyFactory(type_id=faculty_type1.uuid)
    FacultyFactory(type_id=faculty_type2.uuid)

    async with AsyncClient(app=app, base_url="http://test") as client:
        answers_data = ApplicantAnswers(
            uuid=applicant.uuid,
            answers=[{
                "question_id": str(question.uuid),
                "answer_ids": [str(answer1.uuid), str(answer2.uuid)]
            }]
        )

        response = await client.post(
            "/backend/api/results/",
            json=answers_data.model_dump()
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert len(response_data["faculty_type"]) == 2


@pytest.mark.asyncio
async def test_get_all_questions(db_session_factory):
    # Create test data
    question1 = QuestionFactory()
    question2 = QuestionFactory()
    AnswerFactory(question_id=question1.uuid)
    AnswerFactory(question_id=question1.uuid)
    AnswerFactory(question_id=question2.uuid)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/backend/api/questions/")

        assert response.status_code == status.HTTP_200_OK
        questions = response.json()
        assert len(questions) == 2