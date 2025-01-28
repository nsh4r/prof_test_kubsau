from fastapi import FastAPI, HTTPException, status, Body
from sqlmodel import Session, select
from typing import List

from prof_test_kubsau.schemas import ResultInfo, ResponseResult, FacultyTypeSch, QuestionSch, UserAnswers
from prof_test_kubsau.database import (Result, create_db_and_tables, Faculty, ResultFaculty, FacultyType, Question,
                                       Answer, AnswerFaculty, engine)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/api/test/result/', response_model=ResponseResult)
def get_specific_result(request_result: ResultInfo):
    """Получает данные в теле запроса, производит поиск по номеру телефона.
    Если результат не найден, возвращает ошибку 404. Иначе выдает профиль с результатами опроса"""

    db_result = Result.model_validate(request_result)
    faculties_list = []

    with Session(engine) as session:
        profile = (select(Result, ResultFaculty)
                   .join(ResultFaculty)
                   .where(Result.phone_number == db_result.phone_number))
        result = session.exec(profile).all()

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found!')

        faculty_type_ids = [item[1].faculty_type_id for item in result]

        for i in faculty_type_ids:
            faculty_type_query = select(FacultyType).where(FacultyType.id == i)
            faculty_type_result = session.exec(faculty_type_query).first()

            if not faculty_type_result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties type not found!')

            query_faculty = select(Faculty).where(Faculty.type_id == i)
            faculties = session.exec(query_faculty).all()

            if not faculties:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties not found!')

            query_compliance = select(ResultFaculty.compliance).where(ResultFaculty.faculty_type_id == i)
            faculty_type_compliance = session.exec(query_compliance).first()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type_result.name,
                compliance=faculty_type_compliance,
                faculties=faculties
            )

            # Добавляем объект в список
            faculties_list.append(faculty_type_obj)

    # Создаем объект ResponseResult для ответа
    response_result = ResponseResult(
        surname=result[0][0].surname,
        name=result[0][0].name,
        patronymic=result[0][0].patronymic,
        phone_number=result[0][0].phone_number,
        faculty_type=faculties_list  # Используем собранный список
    )

    return response_result


@app.get('/api/test/', response_model=list[QuestionSch])
def get_questions_list():
    """В случае отсутствия вопросов или ответов на них выведет статус 404, иначе список вопросов с ответами"""

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
    print(questions_dict)

    query_result = []
    for question_data in questions_dict.values():
        print(question_data["question"])
        query_result.append(QuestionSch(id=question_data["id"],
                                        question=question_data["question"],
                                        answers=question_data["answers"],))

    return query_result


@app.post('/api/test/answers/', response_model=ResponseResult)
def calc_result(answers: List[UserAnswers] = Body(...)):
    """Принимает ответы и рассчитывает результат"""

    if not answers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answers are required")

    with Session(engine) as session:
        # Словарь для хранения баллов по каждому направлению
        faculty_scores = {}

        # Проходим по всем ответам пользователя
        for user_answer in answers:
            # Проверяем наличие вопроса
            question_query = select(Question).where(Question.id == user_answer.question_id)
            question = session.exec(question_query).first()
            if not question:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Question {user_answer.question_id} not found")

            # Проверяем ответы
            for answer_id in user_answer.answer_ids:
                answer_query = select(Answer).where(Answer.id == answer_id)
                answer = session.exec(answer_query).first()
                if not answer:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Answer {answer_id} not found")

                # Находим связь ответа с направлениями и их баллами
                answer_faculty_query = select(AnswerFaculty).where(AnswerFaculty.answer_id == answer_id)
                answer_faculties = session.exec(answer_faculty_query).all()

                for answer_faculty in answer_faculties:
                    faculty_type_id = answer_faculty.faculty_type_id
                    score = answer_faculty.score or 0

                    # Суммируем баллы для каждого направления
                    if faculty_type_id in faculty_scores:
                        faculty_scores[faculty_type_id] += score
                    else:
                        faculty_scores[faculty_type_id] = score

        # Формируем список направлений с баллами и факультетами
        faculties_list = []
        for faculty_type_id, score in faculty_scores.items():
            faculty_type_query = select(FacultyType).where(FacultyType.id == faculty_type_id)
            faculty_type = session.exec(faculty_type_query).first()
            if not faculty_type:
                continue

            faculty_query = select(Faculty).where(Faculty.type_id == faculty_type_id)
            faculties = session.exec(faculty_query).all()

            faculty_type_obj = FacultyTypeSch(
                name=faculty_type.name,
                compliance=score,
                faculties=faculties
            )
            faculties_list.append(faculty_type_obj)

        # Создаем результат
        response_result = ResponseResult(
            surname="TestSurname",  # Здесь можно указать данные пользователя
            name="TestName",  # или передать их через тело запроса
            patronymic=None,
            phone_number="00000000000",
            faculty_type=faculties_list
        )

    return response_result
