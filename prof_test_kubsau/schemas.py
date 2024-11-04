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

    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(min_length=1, max_length=200, schema_extra={'example': 'Возможно'})


class QuestionSch(SQLModel):
    """Вопрос с ответами"""

    id: int | None = Field(default=None, primary_key=True)
    question: str = Field(min_length=1, max_length=200, schema_extra={'example': 'Любите гладить траву?'})
    answers: list[AnswerSch]
