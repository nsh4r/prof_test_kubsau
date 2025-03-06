from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime


class ResultFaculty(SQLModel, table=True):
    """
    This class represents the result faculty relation in the database.
    """
    __tablename__ = 'result_faculty'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    compliance: int | None = Field(default=None)

    result_id: UUID = Field(default=None, foreign_key='result.uid')
    faculty_type_id: UUID = Field(default=None, foreign_key='facultytype.uid')


class AnswerFaculty(SQLModel, table=True):
    """
    This class represents the answer faculty relation in the database.
    """
    __tablename__ = 'answer_faculty'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    score: int | None = Field(default=None)

    answer_id: UUID = Field(default=None, foreign_key='answer.uid')
    faculty_type_id: UUID = Field(default=None, foreign_key='facultytype.uid')


class Result(SQLModel, table=True):
    """
    This class represents a result in the database.
    """
    __tablename__ = 'result'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    surname: str | None = Field(max_length=30)
    name: str | None = Field(max_length=30)
    patronymic: str | None = Field(max_length=30, default=None)
    phone_number: str | None = Field(max_length=11)
    dt_created: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))


class FacultyType(SQLModel, table=True):
    """
    This class represents a faculty type in the database.
    """
    __tablename__ = 'faculty_type'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    name: str | None = Field(max_length=50)


class Faculty(SQLModel, table=True):
    """
    This class represents a faculty in the database.
    """
    __tablename__ = 'faculty'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    name: str | None = Field(max_length=50)
    url: str | None = Field(max_length=200)

    type_id: UUID = Field(default=None, foreign_key='facultytype.uid')


class Answer(SQLModel, table=True):
    """
    This class represents an answer in the database.
    """
    __tablename__ = 'answer'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    text: str | None = Field(max_length=200)

    question_id: UUID = Field(foreign_key='question.uid')


class Question(SQLModel, table=True):
    """
    This class represents a question in the database.
    """
    __tablename__ = 'question'
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    text: str | None = Field(max_length=200)
