import pytest
from uuid import uuid4
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.applicants.service import ResultService, QuestionService
from backend.src.applicants.schemas import ApplicantInfo, ApplicantAnswers, AnswerInput
from backend.src.tests.factories import (
    ApplicantFactory,
    FacultyTypeFactory,
    FacultyFactory,
    QuestionFactory,
    AnswerFactory,
    AnswerFacultyFactory
)
from backend.src.tests.utils import TestConstants


@pytest.mark.asyncio
class TestResultService:
    async def test_post_result_by_data_new_applicant(self, session: AsyncSession):
        service = ResultService(session)
        user_data = ApplicantInfo(
            surname=TestConstants.SURNAME,
            name=TestConstants.NAME,
            patronymic=TestConstants.PATRONYMIC,
            phone_number=TestConstants.PHONE,
            city=TestConstants.CITY
        )

        result = await service.post_result_by_data(user_data)

        assert result.surname == TestConstants.SURNAME
        assert result.name == TestConstants.NAME
        assert result.patronymic == TestConstants.PATRONYMIC
        assert result.phone_number == TestConstants.PHONE
        assert result.city == TestConstants.CITY
        assert isinstance(result.faculty_type, list)

    async def test_post_result_by_data_existing_applicant(self, session: AsyncSession):
        # Create existing applicant
        applicant = await ApplicantFactory.create(
            phone_number=TestConstants.PHONE,
            surname="OldSurname",
            name="OldName"
        )

        service = ResultService(session)
        user_data = ApplicantInfo(
            surname="NewSurname",
            name="NewName",
            patronymic=TestConstants.PATRONYMIC,
            phone_number=TestConstants.PHONE,
            city=TestConstants.CITY
        )

        result = await service.post_result_by_data(user_data)

        assert result.surname == "NewSurname"
        assert result.name == "NewName"
        assert result.phone_number == TestConstants.PHONE

    async def test_process_user_answers(self, session: AsyncSession):
        # Setup test data
        applicant = await ApplicantFactory.create()
        faculty_type = await FacultyTypeFactory.create()
        question = await QuestionFactory.create()
        answer1 = await AnswerFactory.create(question_id=question.uuid)
        answer2 = await AnswerFactory.create(question_id=question.uuid)
        await AnswerFacultyFactory.create(
            answer_id=answer1.uuid,
            faculty_type_id=faculty_type.uuid,
            score=3
        )
        await AnswerFacultyFactory.create(
            answer_id=answer2.uuid,
            faculty_type_id=faculty_type.uuid,
            score=2
        )

        service = ResultService(session)
        user_data = ApplicantAnswers(
            uuid=applicant.uuid,
            answers=[
                AnswerInput(
                    question_id=question.uuid,
                    answer_ids=[answer1.uuid, answer2.uuid]
                )
            ]
        )

        result = await service.process_user_answers(user_data)

        assert result.uuid == applicant.uuid
        assert len(result.faculty_type) == 1
        assert result.faculty_type[0].compliance == 5  # 3 + 2

    async def test_process_user_answers_invalid_uuid(self, session: AsyncSession):
        service = ResultService(session)
        user_data = ApplicantAnswers(
            uuid=uuid4(),
            answers=[]
        )

        with pytest.raises(ValueError, match="Абитуриент с таким uuid не найден"):
            await service.process_user_answers(user_data)


@pytest.mark.asyncio
class TestQuestionService:
    async def test_get_all_questions(self, session: AsyncSession):
        # Create test data
        question = await QuestionFactory.create()
        answer1 = await AnswerFactory.create(question_id=question.uuid)
        answer2 = await AnswerFactory.create(question_id=question.uuid)

        service = QuestionService(session)
        result = await service.get_all_questions()

        assert len(result) == 1
        assert result[0]['id'] == str(question.uuid)
        assert result[0]['question'] == question.text
        assert len(result[0]['answers']) == 2

    async def test_get_all_questions_empty(self, session: AsyncSession):
        service = QuestionService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_all_questions()

        assert exc_info.value.status_code == 404