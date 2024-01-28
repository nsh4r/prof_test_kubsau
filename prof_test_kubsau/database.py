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


ResultFaculty = Table(
    'result_faculty', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('result_id', ForeignKey('result.id'), unique=True),
    Column('faculty_id', ForeignKey('faculty.id'), unique=True),
    Column('compliance', Integer)
)

AnswerFaculty = Table(
    'answer_faculty', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('answer_id', ForeignKey('answer.id'), unique=True),
    Column('faculty_id', ForeignKey('faculty.id'), unique=True),
    Column('score', Integer)
)


class Result(Base):
    __tablename__ = 'result'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    surname: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    patronymic: Mapped[str] = mapped_column(String(30))
    phone_number: Mapped[str] = mapped_column(String())
    dt_created: Mapped[str] = mapped_column(DateTime, default=datetime.now())

    faculties: Mapped[List['Faculty']] = relationship(secondary=ResultFaculty, back_populates='results')

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

    results: Mapped[List['Result']] = relationship(secondary=ResultFaculty, back_populates='faculties')
    answers: Mapped[List['Answer']] = relationship(secondary=AnswerFaculty, back_populates='faculties')


class Answer(Base):
    __tablename__ = 'answer'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(200))
    question_id: Mapped[int] = mapped_column(ForeignKey('question.id'))

    question: Mapped['Question'] = relationship(back_populates='answers')
    faculties: Mapped[List['Faculty']] = relationship(secondary=AnswerFaculty, back_populates='answers')


class Question(Base):
    __tablename__ = 'question'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(200))
    answers: Mapped[List['Answer']] = relationship(back_populates='question')


Base.metadata.create_all(bind=engine)
