from fastapi import FastAPI, Depends, HTTPException, status
from prof_test_kubsau import database, schemas
from sqlalchemy.orm import Session, selectinload, subqueryload, joinedload

app = FastAPI()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/api/test/result/', response_model=schemas.ResponseResult)
async def get_result(result_info: schemas.QueryResult, db: Session = Depends(get_db)):
    """Получает данные в теле запроса, производит поиск по номеру телефона.
    Если результат не найден, возвращает ошибку 404."""
    result = (db.query(database.Result, database.Faculty.name, database.Faculty.url, database.ResultFaculty.compliance)
              .filter(database.Result.phone_number == result_info.phone_number)
              .all())
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found !')
    return result
