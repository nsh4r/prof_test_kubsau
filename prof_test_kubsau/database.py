from sqlalchemy import create_engine
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class ResultFaculty(Base):
    """Количество очков, факультета у конкретного результата"""

    __tablename__ = 'resultfaculty'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    result_id: Mapped[int] = mapped_column(Integer, ForeignKey('result.id', ondelete='CASCADE'))
    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey('faculty.id', ondelete='CASCADE'))
    score: Mapped[int] = mapped_column(Integer)

    result: Mapped['Result'] = relationship('Result', back_populates='result_faculties')
    faculty: Mapped['Faculty'] = relationship('Faculty', back_populates='result_faculties')


class AnswerFaculty(Base):
    """Количество очков, присуждающее факультету за выбранный ответ"""

    __tablename__ = 'answerfaculty'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    answer_id: Mapped[int] = mapped_column(Integer, ForeignKey('answer.id', ondelete='CASCADE'))
    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey('faculty.id', ondelete='CASCADE'))
    score: Mapped[int] = mapped_column(Integer)

    answer: Mapped['Answer'] = relationship('Answer', back_populates='answer_faculties')
    faculty: Mapped['Faculty'] = relationship('Faculty', back_populates='answer_faculties')


class Result(Base):
    """Результат"""

    __tablename__ = 'result'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    surname: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    patronymic: Mapped[str] = mapped_column(String(30), default='')
    phone_number: Mapped[str] = mapped_column(String(11))
    dt_created: Mapped[str] = mapped_column(DateTime, default=datetime.now())

    result_faculties: Mapped[list['ResultFaculty']] = relationship('ResultFaculty', back_populates='result')


class Faculty(Base):
    __tablename__ = 'faculty'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(String(200))

    result_faculties: Mapped[list['ResultFaculty']] = relationship('ResultFaculty', back_populates='faculty')
    answer_faculties: Mapped[list['AnswerFaculty']] = relationship('AnswerFaculty', back_populates='faculty')


class Answer(Base):
    __tablename__ = 'answer'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(200))
    question_id: Mapped[int] = mapped_column(ForeignKey('question.id'))

    question: Mapped['Question'] = relationship('Question', back_populates='answers')
    answer_faculties: Mapped[list['AnswerFaculty']] = relationship('AnswerFaculty', back_populates='answer')


class Question(Base):
    __tablename__ = 'question'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(200))

    answers: Mapped[list['Answer']] = relationship('Answer', back_populates='question')


Base.metadata.create_all(bind=engine)
