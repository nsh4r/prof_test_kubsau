from fastapi import FastAPI, Depends, HTTPException
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


@app.post('/test/result/', response_model=schemas.Result)
async def send_result(result_info: schemas.Result, db: Session = Depends(get_db)):
    """Получает результат в теле запроса, производит поиск по номеру телефона. """
    result = db.query(database.Result).filter(database.Result.phone_number == result_info.phone_number).first()
    if not result:
        new_result = database.Result(surname=result_info.surname,
                                     name=result_info.name,
                                     patronymic=result_info.patronymic,
                                     phone_number=result_info.phone_number,)
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
    return result


