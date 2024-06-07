from fastapi import FastAPI, Depends, HTTPException, status

from prof_test_kubsau.schemas import ResultInfo, ResponseResult
from prof_test_kubsau.database import Result, ResultFaculty, SessionLocal, Faculty
from sqlalchemy.orm import Session

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/api/test/result/', response_model=ResponseResult)
async def get_result(result_info: ResultInfo, db: Session = Depends(get_db)):
    """Получает данные в теле запроса, производит поиск по номеру телефона.
    Если результат не найден, возвращает ошибку 404."""
    statement = (
        db.query(Result, ResultFaculty, Faculty)
        .join(ResultFaculty, Result.id == ResultFaculty.result_id)
        .join(Faculty, Faculty.id == ResultFaculty.faculty_id)
        .where(
            Result.name == result_info.name,
            Result.surname == result_info.surname,
            Result.patronymic == result_info.patronymic,
            Result.phone_number == result_info.phone_number,
        )
    )
    result = db.execute(statement).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found !')
    return result
