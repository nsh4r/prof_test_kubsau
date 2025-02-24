from sqlmodel import Field, SQLModel, create_engine, Session
from datetime import datetime


class ResultFaculty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    compliance: int | None = Field(default=None)    # посчитанный результат для каждого класса

    result_id: int | None = Field(default=None, foreign_key='result.id')
    faculty_type_id: int | None = Field(default=None, foreign_key='facultytype.id')


class AnswerFaculty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    score: int | None = Field(default=None)

    answer_id: int | None = Field(default=None, foreign_key='answer.id')
    faculty_type_id: int | None = Field(default=None, foreign_key='facultytype.id')


class Result(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    surname: str | None = Field(max_length=30)
    name: str | None = Field(max_length=30)
    patronymic: str | None = Field(max_length=30, default=None)
    phone_number: str | None = Field(max_length=11)
    dt_created: datetime = Field(default=datetime.now())


class FacultyType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str | None = Field(max_length=50)


class Faculty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str | None = Field(max_length=50)
    url: str | None = Field(max_length=200)

    type_id: str | None = Field(default=None, foreign_key='facultytype.id')


class Answer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    text: str | None = Field(max_length=200)

    question_id: int | None = Field(foreign_key='question.id')


class Question(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True, index=True)
    text: str | None = Field(max_length=200)


sqlite_url = 'sqlite:///../sql_app.db'

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
