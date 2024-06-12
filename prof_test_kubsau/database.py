from sqlmodel import Field, SQLModel, create_engine, Session
from datetime import datetime


class ResultFaculty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    compliance: int | None = Field(default=None)    # посчитанный результат для каждого класса

    result_id: int | None = Field(default=None, foreign_key='result.id')
    faculty_type_id: int | None = Field(default=None, foreign_key='faculty.type_id')


class AnswerFaculty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    score: int | None = Field(default=None)

    answer_id: int | None = Field(default=None, foreign_key='answer.id')
    faculty_type_id: int | None = Field(default=None, foreign_key='faculty.type_id')


class Result(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    surname: str | None = Field(max_length=30)
    name: str | None = Field(max_length=30)
    patronymic: str | None = Field(max_length=30, default=None)
    phone_number: str | None = Field(max_length=11)
    dt_created: datetime = Field(default=datetime.now())


class Faculty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str | None = Field(max_length=50)
    url: str | None = Field(max_length=200)

    type_id: str | None = Field(default=None, foreign_key='facultytype.id')


class FacultyType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str | None = Field(max_length=50)


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

#
# create_db_and_tables()
# def fill_db():
#     session = Session(engine)
#
#     # Adding questions
#     questions = [
#         Question(text="Question 1"),
#         Question(text="Question 2"),
#         Question(text="Question 3")
#     ]
#     session.add_all(questions)
#     session.commit()  # Commit to get question IDs
#
#     # Adding answers
#     answers = [
#         Answer(text="Answer 1.1", question_id=1),
#         Answer(text="Answer 1.2", question_id=1),
#         Answer(text="Answer 1.3", question_id=1),
#         Answer(text="Answer 2.1", question_id=2),
#         Answer(text="Answer 2.2", question_id=2),
#         Answer(text="Answer 2.3", question_id=2),
#         Answer(text="Answer 3.1", question_id=3),
#         Answer(text="Answer 3.2", question_id=3),
#         Answer(text="Answer 3.3", question_id=3)
#     ]
#     session.add_all(answers)
#
#     faculty_types = [
#         FacultyType(name="Человек-природа"),
#         FacultyType(name="Человек-техника"),
#         FacultyType(name="Человек-знаковая система"),
#         FacultyType(name="Человек-искусство"),
#         FacultyType(name="Человек-человек")
#     ]
#     session.add_all(faculty_types)
#
#     # Adding faculties
#     faculties = [
#         Faculty(name="Faculty 1", type_id="1", url="http://faculty1.com"),
#         Faculty(name="Faculty 2", type_id="2", url="http://faculty2.com"),
#         Faculty(name="Faculty 3", type_id="3", url="http://faculty3.com"),
#         Faculty(name="Faculty 4", type_id="4", url="http://faculty4.com"),
#         Faculty(name="Faculty 5", type_id="5", url="http://faculty5.com")
#     ]
#     session.add_all(faculties)
#
#     # Adding results
#     results = [
#         Result(surname="Surname1", name="Name1", patronymic='patronymic1', phone_number="72345678901"),
#         Result(surname="Surname2", name="Name2", patronymic='patronymic2', phone_number="72345678902"),
#         Result(surname="Surname3", name="Name3", phone_number="72345678903"),
#         Result(surname="Surname4", name="Name4", patronymic='patronymic3', phone_number="72345678904"),
#         Result(surname="Surname5", name="Name5", patronymic='patronymic4', phone_number="72345678905")
#     ]
#     session.add_all(results)
#
#     # Adding ResultFaculty with random compliance values for demonstration
#     result_faculties = [
#         ResultFaculty(compliance=75, result_id=1, faculty_type_id=1),
#         ResultFaculty(compliance=85, result_id=5, faculty_type_id=5),
#         ResultFaculty(compliance=95, result_id=2, faculty_type_id=2),
#         ResultFaculty(compliance=65, result_id=3, faculty_type_id=3),
#         ResultFaculty(compliance=55, result_id=4, faculty_type_id=4)
#     ]
#     session.add_all(result_faculties)
#
#     # Adding AnswerFaculty with random scores for demonstration
#     answer_faculties = [
#         AnswerFaculty(score=10, answer_id=0, faculty_type_id=2),
#         AnswerFaculty(score=20, answer_id=1, faculty_type_id=1),
#         AnswerFaculty(score=30, answer_id=2, faculty_type_id=2),
#         AnswerFaculty(score=40, answer_id=3, faculty_type_id=3),
#         AnswerFaculty(score=50, answer_id=4, faculty_type_id=4),
#         AnswerFaculty(score=60, answer_id=5, faculty_type_id=1),
#         AnswerFaculty(score=70, answer_id=6, faculty_type_id=1),
#         AnswerFaculty(score=80, answer_id=7, faculty_type_id=5),
#         AnswerFaculty(score=90, answer_id=8, faculty_type_id=3)
#     ]
#     session.add_all(answer_faculties)
#
#     session.commit()
#
#
# fill_db()