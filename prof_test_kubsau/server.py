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


@app.get('/test/question/')
async def read_test(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получает вопросы и ответы из базы данных."""
    question = db.query(database.Question).offset(skip).limit(limit).all()
    answers = db.query(database.Answer).offset(skip).limit(limit).all()
    return {'question': question, 'answers': answers}


@app.delete('/test/result/', response_model=schemas.Result)
async def del_result(result_info: schemas.Result, db: Session = Depends(get_db)):
    """Удаляет результат из базы данных."""
    result = db.query(database.Result).filter(database.Result.phone_number == result_info.phone_number).first()
    if not result:
        raise HTTPException(status_code=404, detail='Result not found')
    db.delete(result)
    db.commit()
    raise HTTPException(status_code=200, detail='Result deleted')

