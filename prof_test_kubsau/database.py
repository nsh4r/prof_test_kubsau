from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import datetime as dt

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

Base = declarative_base()
today = dt.datetime.now()


class Result(Base):
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    phone_number = Column(Integer)
    dt_created = Column(DateTime, default=today.isoformat())


class ResultFaculty(Base):
    __tablename__ = 'result_faculty'

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey('result.id'))
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    compliance = Column(Integer)


class AnswerFaculty(Base):
    __tablename__ = 'answer_faculty'

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey('answer.id'))
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    score = Column(Integer)


class Answer(Base):
    __tablename__ = 'answer'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('quest.id'))
    text = Column(String(200))


class Quest(Base):
    __tablename__ = 'quest'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(200))


class Faculty(Base):
    __tablename__ = 'faculty'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    url = Column(String(200))


Base.metadata.create_all(bind=engine)
