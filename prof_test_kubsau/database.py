from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import validates, relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from datetime import datetime
import re

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)


class Base(DeclarativeBase):
    pass


class ResultFaculty(Base):
    __tablename__ = 'result_faculty'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    result_id: Mapped[int] = mapped_column(ForeignKey('result.id'), primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey('faculty.id'), primary_key=True)
    compliance: Mapped[int] = mapped_column(Integer())


class AnswerFaculty(Base):
    __tablename__ = 'answer_faculty'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey('answer.id'), primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey('faculty.id'), primary_key=True)
    score: Mapped[int] = mapped_column(Integer())


class Result(Base):
    __tablename__ = 'result'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    surname: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    patronymic: Mapped[str] = mapped_column(String(30))
    phone_number: Mapped[str] = mapped_column(String())
    dt_created: Mapped[str] = mapped_column(DateTime, default=datetime.now())

    faculties: Mapped[List['ResultFaculty']] = relationship(back_populates='result')

    @validates('phone_number')
    def validate_phone(self, key, phone_number):
        if not re.match(r'79\d{9}', phone_number):
            raise ValueError('Phone number should match the pattern "79#########"')
        return phone_number


class Faculty(Base):
    __tablename__ = 'faculty'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(String(200))

    results: Mapped[List['ResultFaculty']] = relationship(back_populates='faculty')
    answers: Mapped[List['AnswerFaculty']] = relationship(back_populates='faculty')


class Answer(Base):
    __tablename__ = 'answer'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(200))
    question_id: Mapped[int] = mapped_column(ForeignKey('question.id'))

    question: Mapped['Question'] = relationship(back_populates='answers')
    faculties: Mapped[List['AnswerFaculty']] = relationship(back_populates='answer')


class Question(Base):
    __tablename__ = 'question'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(200))
    answers: Mapped[List['Answer']] = relationship(back_populates='question')


Base.metadata.create_all(bind=engine)
