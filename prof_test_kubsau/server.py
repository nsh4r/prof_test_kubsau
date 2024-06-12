from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session, select

from prof_test_kubsau.schemas import ResultInfo, ResponseResult
from prof_test_kubsau.database import Result, ResultFaculty, Faculty, FacultyType, create_db_and_tables, engine

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/api/test/result/', response_model=ResponseResult)
def get_specific_result(request_result: ResultInfo):
    """Получает данные в теле запроса, производит поиск по номеру телефона.
    Если результат не найден, возвращает ошибку 404."""

    with (Session(engine) as session):
        db_result = Result.model_validate(request_result)
        print(db_result)
        statement = select(Result).where(db_result.phone_number == Result.phone_number)
        result = session.exec(statement).first()
        print(result)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found!')

        return result
