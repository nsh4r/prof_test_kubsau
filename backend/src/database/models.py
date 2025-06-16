from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List

class ApplicantFaculty(SQLModel, table=True):
    """
    This class represents the applicant faculty relation in the database.
    """
    __tablename__ = 'applicant_faculty'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    compliance: int | None = Field(default=None)

    applicant_id: UUID = Field(default=None, foreign_key='applicant.uuid')
    faculty_type_id: UUID = Field(default=None, foreign_key='faculty_type.uuid')


class AnswerFaculty(SQLModel, table=True):
    """
    This class represents the answer faculty relation in the database.
    """
    __tablename__ = 'answer_faculty'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    score: int | None = Field(default=None)

    answer_id: UUID = Field(default=None, foreign_key='answer.uuid')
    faculty_type_id: UUID = Field(default=None, foreign_key='faculty_type.uuid')


class Applicant(SQLModel, table=True):
    """
    This class represents an applicant in the database.
    """
    __tablename__ = 'applicant'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    surname: str | None = Field(max_length=30)
    name: str | None = Field(max_length=30)
    patronymic: str | None = Field(max_length=30, default=None)
    phone_number: str | None = Field(max_length=11, unique=True)
    city: str | None = Field(max_length=30)
    dt_created: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    passed_exams: List["ApplicantExam"] = Relationship(back_populates="applicant")


class FacultyType(SQLModel, table=True):
    """
    This class represents a faculty type in the database.
    """
    __tablename__ = 'faculty_type'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    name: str | None = Field(max_length=50)


class Faculty(SQLModel, table=True):
    """
    This class represents a faculty in the database.
    """
    __tablename__ = 'faculty'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    name: str | None = Field(max_length=50)
    url: str | None = Field(max_length=200)

    type_id: UUID = Field(default=None, foreign_key='faculty_type.uuid')
    required_exams: List["FacultyExamRequirement"] = Relationship(
        back_populates="faculty",
        sa_relationship_kwargs={"primaryjoin": "Faculty.uuid == FacultyExamRequirement.faculty_id"})


class Answer(SQLModel, table=True):
    """
    This class represents an answer in the database.
    """
    __tablename__ = 'answer'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    text: str | None = Field(max_length=200)

    question_id: UUID = Field(foreign_key='question.uuid')


class Question(SQLModel, table=True):
    """
    This class represents a question in the database.
    """
    __tablename__ = 'question'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    text: str | None = Field(max_length=200)


class Exam(SQLModel, table=True):
    """
    This class represent a EGE Exams in the database.
    """
    __tablename__ = 'exam'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    name: str = Field(max_length=50, nullable=False)
    code: str = Field(max_length=50, nullable=False, unique=True)


class FacultyExamRequirement(SQLModel, table=True):
    """
    This class contains what exams are required for the faculty + minimum scores.
    """
    __tablename__ = 'faculty_exam_requirement'
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    faculty_id: UUID = Field(foreign_key="faculty.uuid")
    exam_id: UUID = Field(foreign_key="exam.uuid")
    min_score: int

    faculty: Faculty = Relationship(back_populates="required_exams")
    exam: Exam = Relationship()


class ApplicantExam(SQLModel, table=True):
    """
    This class contains what exams the applicant passed and his scores.
    """
    uuid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, unique=True, default=uuid4)
    )
    applicant_id: UUID = Field(foreign_key="applicant.uuid")
    exam_id: UUID = Field(foreign_key="exam.uuid")
    score: int

    applicant: Applicant = Relationship(back_populates="passed_exams")
    exam: Exam = Relationship()