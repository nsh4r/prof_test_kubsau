import factory
from uuid import uuid4
import datetime
from sqlmodel import SQLModel
from backend.src.database.models import (
    Applicant,
    Faculty,
    FacultyType,
    Question,
    Answer,
    ApplicantFaculty,
    AnswerFaculty
)
from backend.src.tests.utils import async_session


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = async_session
        sqlalchemy_session_persistence = "commit"


class ApplicantFactory(BaseFactory):
    class Meta:
        model = Applicant

    uuid = factory.LazyFunction(uuid4)
    surname = factory.Faker('last_name')
    name = factory.Faker('first_name')
    patronymic = factory.Faker('middle_name')
    phone_number = factory.Sequence(lambda n: f'79{n:09d}')
    city = factory.Faker('city')
    dt_created = factory.LazyFunction(datetime.datetime.now)


class FacultyTypeFactory(BaseFactory):
    class Meta:
        model = FacultyType

    uuid = factory.LazyFunction(uuid4)
    name = factory.Faker('word')


class FacultyFactory(BaseFactory):
    class Meta:
        model = Faculty

    uuid = factory.LazyFunction(uuid4)
    name = factory.Faker('company')
    url = factory.Faker('url')
    type_id = factory.LazyFunction(uuid4)


class QuestionFactory(BaseFactory):
    class Meta:
        model = Question

    uuid = factory.LazyFunction(uuid4)
    text = factory.Faker('sentence')


class AnswerFactory(BaseFactory):
    class Meta:
        model = Answer

    uuid = factory.LazyFunction(uuid4)
    text = factory.Faker('word')
    question_id = factory.LazyFunction(uuid4)


class ApplicantFacultyFactory(BaseFactory):
    class Meta:
        model = ApplicantFaculty

    uuid = factory.LazyFunction(uuid4)
    compliance = factory.Faker('random_int', min=1, max=10)
    applicant_id = factory.LazyFunction(uuid4)
    faculty_type_id = factory.LazyFunction(uuid4)


class AnswerFacultyFactory(BaseFactory):
    class Meta:
        model = AnswerFaculty

    uuid = factory.LazyFunction(uuid4)
    score = factory.Faker('random_int', min=1, max=5)
    answer_id = factory.LazyFunction(uuid4)
    faculty_type_id = factory.LazyFunction(uuid4)