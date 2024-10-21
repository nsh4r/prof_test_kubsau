from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session, select

from prof_test_kubsau.schemas import ResultInfo, ResponseResult, FacultyTypeSch, QuestionsResponse
from prof_test_kubsau.database import Result, create_db_and_tables, Faculty, ResultFaculty, FacultyType, engine

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


@app.get('/api/test/', response_model=QuestionsResponse)
def get_questions_list():
    """В случае отсутствия вопросов или ответов на них выведет статус 404, иначе список вопросов с ответами"""
    pass
