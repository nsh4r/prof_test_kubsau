from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from sqlalchemy.sql.expression import delete

from backend.src.database.models import Applicant, Faculty, ApplicantFaculty, FacultyType, Question, Answer, AnswerFaculty
from backend.src.applicants.schemas import ResponseResult, FacultyTypeSch, ApplicantAnswers


class ResultService:
    """
    This class provides methods to handle result-related operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def post_result_by_data(self, user_data):
        """
        Find or create an applicant by full name and phone number.

        Args:
            user_data: The user data containing surname, name, patronymic, and phone_number.

        Returns:
            ResponseResult: The result object.
        """
        # Проверяем, существует ли уже абитуриент по номеру телефона
        existing_applicant = await self.session.exec(select(Applicant).where(
            Applicant.phone_number == user_data.phone_number
        ))
        existing_applicant = existing_applicant.first()

        # Если найден, обновляем ФИО
        if existing_applicant:
            existing_applicant.surname = user_data.surname
            existing_applicant.name = user_data.name
            existing_applicant.patronymic = user_data.patronymic
            await self.session.commit()
            await self.session.refresh(existing_applicant)
        else:
            # Если абитуриента нет, создаем нового
            new_applicant = Applicant(
                surname=user_data.surname,
                name=user_data.name,
                patronymic=user_data.patronymic,
                phone_number=user_data.phone_number
            )
            self.session.add(new_applicant)
            await self.session.commit()
            await self.session.refresh(new_applicant)
            existing_applicant = new_applicant

        # Получаем связанные результаты
        applicant_faculties = await self.session.exec(select(ApplicantFaculty).where(
            ApplicantFaculty.applicant_id == existing_applicant.uid
        ))
        applicant_faculties = applicant_faculties.all()

        faculties_list = []

        for app_faculty in applicant_faculties:
            faculty_type = await self.session.exec(select(FacultyType).where(
                FacultyType.uid == app_faculty.faculty_type_id
            ))
            faculty_type = faculty_type.first()

            if not faculty_type:
                continue

            faculties = await self.session.exec(select(Faculty).where(
                Faculty.type_id == faculty_type.uid
            ))
            faculties = faculties.all()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type.name,
                compliance=app_faculty.compliance,
                faculties=faculties
            )
            faculties_list.append(faculty_type_obj)

        return ResponseResult(
            uid=existing_applicant.uid,
            surname=existing_applicant.surname,
            name=existing_applicant.name,
            patronymic=existing_applicant.patronymic,
            phone_number=existing_applicant.phone_number,
            faculty_type=faculties_list
        )

    from sqlmodel import select

    async def process_user_answers(self, user_data: ApplicantAnswers):
        """
        Process user answers and update test results for an existing Applicant.

        Args:
            user_data: An object containing the applicant's uid and the testing answers.

        Returns:
            ResponseResult: The result object with applicant details and faculty type results.
        """
        # Получаем абитуриента по uid
        applicant = await self.session.exec(select(Applicant).where(Applicant.uid == user_data.uid))
        applicant = applicant.first()
        if not applicant:
            raise ValueError("Абитуриент с таким uid не найден")

        # Удаляем существующие результаты тестирования для абитуриента
        existing_faculties = await self.session.exec(
            select(ApplicantFaculty).where(ApplicantFaculty.applicant_id == applicant.uid)
        )
        for faculty in existing_faculties.all():
            await self.session.delete(faculty)
        await self.session.commit()

        # Подсчёт баллов для каждого факультета
        faculty_scores = {}
        for answer_data in user_data.answers:
            for answer_id in answer_data.answer_ids:
                answer_faculties = await self.session.exec(
                    select(AnswerFaculty).where(AnswerFaculty.answer_id == answer_id)
                )
                for answer_faculty in answer_faculties.all():
                    faculty_scores[answer_faculty.faculty_type_id] = (
                            faculty_scores.get(answer_faculty.faculty_type_id, 0) + (answer_faculty.score or 0)
                    )

        faculties_list = []
        # Формирование списка результатов для каждого типа факультета
        for faculty_type_id, score in faculty_scores.items():
            faculty_type_result = await self.session.exec(
                select(FacultyType).where(FacultyType.uid == faculty_type_id)
            )
            faculty_type_obj = faculty_type_result.first()
            if not faculty_type_obj:
                continue

            faculties_result = await self.session.exec(
                select(Faculty).where(Faculty.type_id == faculty_type_id)
            )
            faculties = faculties_result.all()

            faculty_type_sch = FacultyTypeSch(
                name=faculty_type_obj.name,
                compliance=score,
                faculties=faculties
            )
            faculties_list.append(faculty_type_sch)

            # Сохранение нового результата тестирования для данного факультета
            new_applicant_faculty = ApplicantFaculty(
                applicant_id=applicant.uid,
                faculty_type_id=faculty_type_id,
                compliance=score
            )
            self.session.add(new_applicant_faculty)

        await self.session.commit()

        return ResponseResult(
            uid=applicant.uid,  # Добавляем uid абитуриента
            surname=applicant.surname,
            name=applicant.name,
            patronymic=applicant.patronymic,
            phone_number=applicant.phone_number,
            faculty_type=faculties_list
        )


class QuestionService:
    """
    This class provides methods to handle question-related operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_questions(self):
        """
        Get all questions with their answers.

        Returns:
            list: A list of questions with answers.
        """
        questions_dict = {}

        questions_query = (select(Question, Answer).join(Answer).
                           where(Question.uid == Answer.question_id))
        question_res_query = await self.session.exec(questions_query)
        question_res_query = question_res_query.all()

        if not question_res_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Questions not found!')

        for question, answer in question_res_query:
            if question.uid not in questions_dict:
                questions_dict[question.uid] = {
                    "id": question.uid,
                    "question": question.text,
                    "answers": [],
                }
            questions_dict[question.uid]["answers"].append(answer)

        return [
            {"id": q["id"], "question": q["question"], "answers": q["answers"]}
            for q in questions_dict.values()
        ]