from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from backend.src.database.models import Result, Faculty, ResultFaculty, FacultyType, Question, Answer, AnswerFaculty
from backend.src.applicants.schemas import ResponseResult, FacultyTypeSch


class ResultService:
    """
    This class provides methods to handle result-related operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_result_by_phone(self, phone_number: str):
        """
        Get a result by phone number.

        Args:
            phone_number (str): The phone number of the result.

        Returns:
            ResponseResult: The result object.
        """
        profile = (select(Result, ResultFaculty).join(ResultFaculty).
                   where(Result.phone_number == phone_number))
        result = await self.session.exec(profile)
        result = result.all()

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found!')

        faculties_list = []
        faculty_type_ids = [item[1].faculty_type_id for item in result]

        for i in faculty_type_ids:
            faculty_type_result = await self.session.exec(select(FacultyType).where(FacultyType.uid == i))
            faculty_type_result = faculty_type_result.first()

            if not faculty_type_result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties type not found!')

            faculties = await self.session.exec(select(Faculty).where(Faculty.type_id == i))
            faculties = faculties.all()

            if not faculties:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties not found!')

            faculty_type_compliance = await self.session.exec(select(ResultFaculty.compliance).
                                                              where(ResultFaculty.faculty_type_id == i))
            faculty_type_compliance = faculty_type_compliance.first()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type_result.name,
                compliance=faculty_type_compliance,
                faculties=faculties
            )

            faculties_list.append(faculty_type_obj)

        return ResponseResult(
            surname=result[0][0].surname,
            name=result[0][0].name,
            patronymic=result[0][0].patronymic,
            phone_number=result[0][0].phone_number,
            faculty_type=faculties_list
        )

    async def process_user_answers(self, user_data):
        """
        Process user answers and create a new result.

        Args:
            user_data: The user data containing answers.

        Returns:
            ResponseResult: The result object.
        """
        existing_result = await self.session.exec(select(Result).
                                                  where(Result.phone_number == user_data.phone_number))
        existing_result = existing_result.first()

        if existing_result:
            existing_faculties = await self.session.exec(select(ResultFaculty).
                                                         where(ResultFaculty.result_id == existing_result.uid))
            existing_faculties = existing_faculties.all()

            for faculty in existing_faculties:
                await self.session.delete(faculty)
            await self.session.delete(existing_result)
            await self.session.commit()

        new_result = Result(
            surname=user_data.surname,
            name=user_data.name,
            patronymic=user_data.patronymic,
            phone_number=user_data.phone_number
        )
        self.session.add(new_result)
        await self.session.commit()
        await self.session.refresh(new_result)

        faculty_scores = {}

        for answer_data in user_data.answers:
            for answer_id in answer_data.answer_ids:
                answer_faculties = await self.session.exec(select(AnswerFaculty).
                                                           where(AnswerFaculty.answer_id == answer_id))
                answer_faculties = answer_faculties.all()

                for answer_faculty in answer_faculties:
                    faculty_scores[answer_faculty.faculty_type_id] =\
                        (faculty_scores.get(answer_faculty.faculty_type_id, 0) + (answer_faculty.score or 0))

        faculties_list = []
        for faculty_type_id, score in faculty_scores.items():
            faculty_type = await self.session.exec(select(FacultyType).
                                                   where(FacultyType.uid == faculty_type_id))
            faculty_type = faculty_type.first()

            if not faculty_type:
                continue

            faculties = await self.session.exec(select(Faculty).
                                                where(Faculty.type_id == faculty_type_id))
            faculties = faculties.all()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type.name,
                compliance=score,
                faculties=faculties
            )
            faculties_list.append(faculty_type_obj)

            result_faculty = ResultFaculty(
                result_id=new_result.uid,
                faculty_type_id=faculty_type_id,
                compliance=score
            )
            self.session.add(result_faculty)

        await self.session.commit()

        return ResponseResult(
            surname=new_result.surname,
            name=new_result.name,
            patronymic=new_result.patronymic,
            phone_number=new_result.phone_number,
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