from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.applicants.schemas import ResultInfo, ResponseResult, QuestionSch, UserAnswers
from backend.src.database.main import init_db
from backend.src.applicants.routes import get_result_by_phone, get_all_questions, process_user_answers, api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post('/api/test/result/', response_model=ResponseResult)
def get_specific_result(request_result: ResultInfo):
    return get_result_by_phone(request_result)


@app.get('/api/test/', response_model=list[QuestionSch])
def get_questions_list():
    return get_all_questions()


@app.post('/api/test/answers/', response_model=ResponseResult)
def calc_result(user_data: UserAnswers):
    return process_user_answers(user_data)