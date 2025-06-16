from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from sqlalchemy.sql.expression import delete
from uuid import UUID

from backend.src.database.models import (Applicant, Faculty, ApplicantFaculty, FacultyType, Question, Answer,
                                         AnswerFaculty, Exam, FacultyExamRequirement)
from backend.src.applicants.schemas import (ResponseResult, FacultyTypeSch, ApplicantAnswers, ApplicantInfo, Exams,
                                            QuestionSch, AnswerSch, RequiredExams, RequiredExam)


class ResultService:
    """
    This class provides methods to handle result-related operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the ResultService with a database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def register_or_get_applicant(self, user_data: ApplicantInfo) -> UUID:
        """
        Register new applicant or get existing one by phone number.
        
        Args:
            user_data: Applicant information containing:
                - surname: str
                - name: str
                - patronymic: str | None
                - phone_number: str
                - city: str | None
                
        Returns:
            UUID: The UUID of the applicant (new or existing)
            
        Notes:
            - If applicant exists, updates their personal information
            - If applicant doesn't exist, creates new record
        """

        existing_applicant = await self.session.exec(select(Applicant).where(
            Applicant.phone_number == user_data.phone_number
        ))
        existing_applicant = existing_applicant.first()


        if existing_applicant:
            existing_applicant.surname = user_data.surname
            existing_applicant.name = user_data.name
            existing_applicant.patronymic = user_data.patronymic
            existing_applicant.city = user_data.city
            await self.session.commit()
            await self.session.refresh(existing_applicant)
            return existing_applicant.uuid
        else:

            new_applicant = Applicant(
                surname=user_data.surname,
                name=user_data.name,
                patronymic=user_data.patronymic,
                phone_number=user_data.phone_number,
                city=user_data.city
            )
            self.session.add(new_applicant)
            await self.session.commit()
            await self.session.refresh(new_applicant)
            return new_applicant.uuid

    async def get_applicant_results(self, applicant_uuid: UUID) -> ResponseResult:
        """
        Get applicant results by UUID.
        
        Args:
            applicant_uuid: UUID of the applicant
            
        Returns:
            ResponseResult: Object containing applicant data and test results
            
        Raises:
            HTTPException: 404 if applicant not found
        """
        applicant = await self.session.exec(select(Applicant).where(Applicant.uuid == applicant_uuid))
        applicant = applicant.first()
        if not applicant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")

        applicant_faculties = await self.session.exec(select(ApplicantFaculty).where(
            ApplicantFaculty.applicant_id == applicant.uuid
        ))
        applicant_faculties = applicant_faculties.all()

        faculties_list = []

        for app_faculty in applicant_faculties:
            faculty_type = await self.session.exec(select(FacultyType).where(
                FacultyType.uuid == app_faculty.faculty_type_id
            ))
            faculty_type = faculty_type.first()

            if not faculty_type:
                continue

            faculties = await self.session.exec(select(Faculty).where(
                Faculty.type_id == faculty_type.uuid
            ))
            faculties = faculties.all()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type.name,
                compliance=app_faculty.compliance,
                faculties=faculties
            )
            faculties_list.append(faculty_type_obj)

        return ResponseResult(
            uuid=applicant.uuid,
            surname=applicant.surname,
            name=applicant.name,
            patronymic=applicant.patronymic,
            city=applicant.city,
            phone_number=applicant.phone_number,
            faculty_type=faculties_list
        )

    async def process_user_answers(self, user_data: ApplicantAnswers) -> ResponseResult:
        """
        Process user answers and update test results for an existing Applicant.
        
        Args:
            user_data: Contains:
                - uuid: Applicant UUID
                - answers: List of answers with question_id and answer_ids
                
        Returns:
            ResponseResult: Updated test results
            
        Raises:
            ValueError: If applicant not found
        """

        applicant = await self.session.exec(select(Applicant).where(Applicant.uuid == user_data.uuid))
        applicant = applicant.first()
        if not applicant:
            raise ValueError("Абитуриент с таким uuid не найден")

        
        existing_faculties = await self.session.exec(
            select(ApplicantFaculty).where(ApplicantFaculty.applicant_id == applicant.uuid)
        )
        for faculty in existing_faculties.all():
            await self.session.delete(faculty)
        await self.session.commit()

        
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
        
        for faculty_type_id, score in faculty_scores.items():
            faculty_type_result = await self.session.exec(
                select(FacultyType).where(FacultyType.uuid == faculty_type_id)
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

           
            new_applicant_faculty = ApplicantFaculty(
                applicant_id=applicant.uuid,
                faculty_type_id=faculty_type_id,
                compliance=score
            )
            self.session.add(new_applicant_faculty)

        await self.session.commit()

        return ResponseResult(
            uuid=applicant.uuid,
            surname=applicant.surname,
            name=applicant.name,
            patronymic=applicant.patronymic,
            city=applicant.city,
            phone_number=applicant.phone_number,
            faculty_type=faculties_list
        )


class QuestionService:
    """
    This class provides methods to handle question-related operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the QuestionService with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session


    async def get_all_questions(self) -> list[QuestionSch]:
        """
        Get all questions with their answers.

        Returns:
            list: A list of dictionaries containing:
                - id: Question UUID
                - question: Question text
                - answers: List of answer objects

        Raises:
            HTTPException: 404 if no questions found
        """
        questions_dict = {}

        query = select(Question, Answer).join(Answer).where(Question.uuid == Answer.question_id)
        result = await self.session.exec(query)
        rows = result.all()

        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questions not found!")

        for question, answer in rows:
            if question.uuid not in questions_dict:
                questions_dict[question.uuid] = QuestionSch(
                    id=str(question.uuid),
                    question=question.text,
                    answers=[]
                )
            questions_dict[question.uuid].answers.append(
                AnswerSch(
                    id=str(answer.uuid),
                    text=answer.text
                )
            )

        return list(questions_dict.values())


class ExamsService:
    """
        This class provides methods to handle question-related operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the ExamsService with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session


    async def get_all_exams(self) -> Exams:
        """
        Get all exams.

        Returns:
            list: A list of dictionaries containing:
                - id: Exam UUID
                - name: Exam name
                - code: Code of exam
        Raises:
            HTTPException: 404 if no exams found
        """
        exams_query = select(Exam)
        exams_res_query = await self.session.exec(exams_query)
        exams_res_query = exams_res_query.all()

        if not exams_res_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Exams not found!')

        exams_list = [
            Exam(uuid=exam.uuid, name=exam.name, code=exam.code)
            for exam in exams_res_query
        ]

        return Exams(exams=exams_list)



    async def get_all_required_exams(self) -> RequiredExams:
        """
        Get all questions with their answers.

        Returns:
            List of questions with answer options

        Raises:
            HTTPException: 404 if no questions found
        """
        query = (
            select(
                Faculty.uuid,
                Faculty.name,
                Exam.uuid,
                Exam.code,
                FacultyExamRequirement.min_score
            )
            .join(FacultyExamRequirement, Faculty.uuid == FacultyExamRequirement.faculty_id)
            .join(Exam, Exam.uuid == FacultyExamRequirement.exam_id)
        )
        result = await self.session.exec(query)
        rows = result.all()

        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Required exams not found!")

        exams_list = [
            RequiredExam(
                faculty_id=faculty_id,
                faculty_name=faculty_name,
                exam_id=exam_id,
                exam_code=exam_code,
                min_score=min_score
            )
            for faculty_id, faculty_name, exam_id, exam_code, min_score in rows
        ]

        return RequiredExams(required_exams=exams_list)