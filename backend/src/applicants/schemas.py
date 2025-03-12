from sqlmodel import Field, SQLModel


class ResultInfo(SQLModel):
    """Входные данные для API получения результата"""
    surname: str = Field(schema_extra={'example': 'Ivanov'})
    name: str = Field(schema_extra={'example': 'Ivan'})
    patronymic: str | None = Field(default=None, schema_extra={'example': 'Ivanovich'})
    phone_number: str = Field(schema_extra={'example': '79000000000'}, max_length=11, regex=r'^79\d{9}$')


class Faculty(SQLModel):
    """Информация о факультете"""

    name: str = Field(min_length=1, schema_extra={'example': 'Прикладной информатики'})
    url: str = Field(min_length=1, schema_extra={'example': 'https://...'})


class FacultyTypeSch(SQLModel):
    """Информация о классификации факультета"""

    name: str = Field(min_length=1, schema_extra={'example': 'Человек-Природа'})
    compliance: int = Field(gt=0, schema_extra={'example': '85'})
    faculties: list[Faculty]


class ResponseResult(ResultInfo):
    """Выходные данные для API получения результата"""

    faculty_type: list[FacultyTypeSch]


class AnswerSch(SQLModel):
    """Информация о классификации факультета"""

    id: str | None = Field(default=None, primary_key=True)
    text: str = Field(min_length=1, max_length=200, schema_extra={'example': 'Возможно'})


class QuestionSch(SQLModel):
    """Вопрос с ответами"""

    id: str | None = Field(default=None, primary_key=True)
    question: str = Field(min_length=1, max_length=200, schema_extra={'example': 'Любите гладить траву?'})
    answers: list[AnswerSch]


class AnswerInput(SQLModel):
    """Ответ пользователя на конкретный вопрос"""
    question_id: str = Field(schema_extra={"example": "ee1cb691-99b5-4b64-b5af-e97757c7b9ad"})
    answer_ids: list[str] = Field(schema_extra={"example": ["418ec475-5604-4789-a90f-269c879ea9ed",
                                                            "0af41b33-1780-4603-ba5c-4777496fcce7"]})


class UserAnswers(ResultInfo):
    """Ответы пользователя"""
    answers: list[AnswerInput] = Field(schema_extra={'example': [
        {"question_id": "ee1cb691-99b5-4b64-b5af-e97757c7b9ad", "answer_ids": ["418ec475-5604-4789-a90f-269c879ea9ed",
                                                                               "0af41b33-1780-4603-ba5c-4777496fcce7"]},
        {"question_id": "df2c6f0c-4d4f-4803-a573-c74c9c96f57f", "answer_ids": ["8cbbd1d1-e2b1-45b6-a210-b86018adb25b"]}
    ]})
