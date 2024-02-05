from fastapi import FastAPI, Depends, HTTPException, status
from prof_test_kubsau import database, schemas
from sqlalchemy.orm import Session

app = FastAPI()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/api/test/result/', response_model=schemas.Result)
async def get_result(result_info: schemas.Result, db: Session = Depends(get_db)):
    """Получает результат в теле запроса, производит поиск по номеру телефона. """
    result = db.query(database.Result).filter(database.Result.phone_number == result_info.phone_number).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Result not found !')
    return result


