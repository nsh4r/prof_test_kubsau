from fastapi import HTTPException, status
from sqlmodel import Session, select
from backend.src.database.models import engine, Result, Faculty, ResultFaculty, FacultyType, Question, Answer, AnswerFaculty
from backend.src.users.schemas import ResponseResult, FacultyTypeSch

def get_result_by_phone(request_result):
    with Session(engine) as session:
        profile = (select(Result, ResultFaculty)
                   .join(ResultFaculty)
                   .where(Result.phone_number == request_result.phone_number))
        result = session.exec(profile).all()

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found!')

        faculties_list = []
        faculty_type_ids = [item[1].faculty_type_id for item in result]

        for i in faculty_type_ids:
            faculty_type_result = session.exec(select(FacultyType).where(FacultyType.id == i)).first()

            if not faculty_type_result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties type not found!')

            faculties = session.exec(select(Faculty).where(Faculty.type_id == i)).all()

            if not faculties:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties not found!')

            faculty_type_compliance = session.exec(select(ResultFaculty.compliance).where(ResultFaculty.faculty_type_id == i)).first()

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

def get_all_questions():
    questions_dict = {}

    with Session(engine) as session:
        questions_query = select(Question, Answer).join(Answer).where(Question.id == Answer.question_id)
        question_res_query = session.exec(questions_query).all()

    if not question_res_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Questions not found!')

    for question, answer in question_res_query:
        if question.id not in questions_dict:
            questions_dict[question.id] = {
                "id": question.id,
                "question": question.text,
                "answers": [],
            }
        questions_dict[question.id]["answers"].append(answer)

    return [
        {"id": q["id"], "question": q["question"], "answers": q["answers"]}
        for q in questions_dict.values()
    ]

def process_user_answers(user_data):
    with Session(engine) as session:
        existing_result = session.exec(select(Result).where(Result.phone_number == user_data.phone_number)).first()

        if existing_result:
            existing_faculties = session.exec(select(ResultFaculty).where(ResultFaculty.result_id == existing_result.id)).all()
            for faculty in existing_faculties:
                session.delete(faculty)
            session.delete(existing_result)
            session.commit()

        new_result = Result(
            surname=user_data.surname,
            name=user_data.name,
            patronymic=user_data.patronymic,
            phone_number=user_data.phone_number
        )
        session.add(new_result)
        session.commit()
        session.refresh(new_result)

        faculty_scores = {}

        for answer_data in user_data.answers:
            for answer_id in answer_data.answer_ids:
                answer_faculties = session.exec(select(AnswerFaculty).where(AnswerFaculty.answer_id == answer_id)).all()
                for answer_faculty in answer_faculties:
                    faculty_scores[answer_faculty.faculty_type_id] = faculty_scores.get(answer_faculty.faculty_type_id, 0) + (answer_faculty.score or 0)

        faculties_list = []
        for faculty_type_id, score in faculty_scores.items():
            faculty_type = session.exec(select(FacultyType).where(FacultyType.id == faculty_type_id)).first()
            if not faculty_type:
                continue

            faculties = session.exec(select(Faculty).where(Faculty.type_id == faculty_type_id)).all()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type.name,
                compliance=score,
                faculties=faculties
            )
            faculties_list.append(faculty_type_obj)

            result_faculty = ResultFaculty(
                result_id=new_result.id,
                faculty_type_id=faculty_type_id,
                compliance=score
            )
            session.add(result_faculty)

        session.commit()

        return ResponseResult(
            surname=new_result.surname,
            name=new_result.name,
            patronymic=new_result.patronymic,
            phone_number=new_result.phone_number,
            faculty_type=faculties_list
        )
