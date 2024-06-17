from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session, select

from prof_test_kubsau.schemas import ResultInfo, ResponseResult
from prof_test_kubsau.database import Result, create_db_and_tables, Faculty, ResultFaculty, FacultyType, engine

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/api/test/result/', response_model=ResponseResult)  # response_model=ResponseResult
def get_specific_result(request_result: ResultInfo):
    """Получает данные в теле запроса, производит поиск по номеру телефона.
    Если результат не найден, возвращает ошибку 404."""

    db_result = Result.model_validate(request_result)
    faculties = []
    with Session(engine) as session:
        profile = (select(Result, ResultFaculty)
                   .join(ResultFaculty).
                   where(Result.phone_number == db_result.phone_number))    # ваыбираем данные исходя из номера
        result = session.exec(profile).all()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found!')
        faculty_type_ids = [item[1].faculty_type_id for item in result]     # получаем номер ледирующего типа факультета
        for i in faculty_type_ids:
            query_faculty = (select(Faculty).where(Faculty.type_id == i))   # ищем факультеты принадлежащие к типу
            faculty = session.exec(query_faculty).first()
            faculties.append(faculty)
        if not faculties:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties not found!')
        for i in faculty_type_ids:
            faculty_type = select(FacultyType).where(FacultyType.id == i)   # поиск типа
        faculty_type_result = session.exec(faculty_type).first()
        if not faculty_type_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Faculties type not found!')

    response_result = ResponseResult(                                       # заполнение формы вывода
        surname=result[0][0].surname,
        name=result[0][0].name,
        patronymic=result[0][0].patronymic,
        phone_number=result[0][0].phone_number,
        faculty_type=faculty_type_result.name,
        faculties=faculties,
        compliance=result[0][1].compliance
    )
    return response_result
