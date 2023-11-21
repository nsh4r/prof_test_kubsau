from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import validates, relationship, backref
import datetime, re

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

Base = declarative_base()


class Result(Base):
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    phone_number = Column(String)
    dt_created = Column(DateTime, default=datetime.datetime.utcnow().isoformat())

    @validates('phone_number')
    def validate_phone(self, key, phone_number):
        if not re.match(r'79\d{9}', phone_number):
            raise ValueError('Phone number should match the pattern "79#########"')
        return phone_number

    result_faculty = relationship('ResultFaculty', backref='result')


class ResultFaculty(Base):
    __tablename__ = 'result_faculty'

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey('result.id'))
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    compliance = Column(Integer)

    result = relationship('Result', backref='result_faculty')
    faculty = relationship('Faculty', backref='result_faculty')


class AnswerFaculty(Base):
    __tablename__ = 'answer_faculty'

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey('answer.id'))
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    score = Column(Integer)

    answer = relationship('Answer', backref='answer_faculty')
    faculty = relationship('Faculty', backref='answer_faculty')


class Answer(Base):
    __tablename__ = 'answer'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('quest.id'))
    text = Column(String(200))

    quest = relationship('Quest', backref='answer')


class Quest(Base):
    __tablename__ = 'quest'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(200))

    answer = relationship('Answer', backref='quest')


class Faculty(Base):
    __tablename__ = 'faculty'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    url = Column(String(200))

    answer_faculty = relationship("AnswerFaculty", backref="faculty")
    result_faculty = relationship("ResultFaculty", backref="faculty")


Base.metadata.create_all(bind=engine)
