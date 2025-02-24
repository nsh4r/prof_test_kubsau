from fastapi import FastAPI, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import ResultInfo, ResponseResult, QuestionSch, UserAnswers
from backend.database import create_db_and_tables
from backend.modules.api_test import get_result_by_phone, get_all_questions, process_user_answers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/api/test/result/', response_model=ResponseResult)
def get_specific_result(request_result: ResultInfo):
    return get_result_by_phone(request_result)


@app.get('/api/test/', response_model=list[QuestionSch])
def get_questions_list():
    return get_all_questions()


@app.post('/api/test/answers/', response_model=ResponseResult)
def calc_result(user_data: UserAnswers):
    return process_user_answers(user_data)
