import uuid
from datetime import datetime
import factory
from factory import fuzzy

from backend.src.database.models import (
    Applicant, Faculty, FacultyType, Question, Answer,
    ApplicantFaculty, AnswerFaculty
)
from backend.src.tests.utils import TestConstants


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


class ApplicantFactory(BaseFactory):
    class Meta:
        model = Applicant

    uuid = factory.LazyFunction(uuid.uuid4)
    surname = TestConstants.SURNAME
    name = TestConstants.NAME
    patronymic = TestConstants.PATRONYMIC
    phone_number = TestConstants.PHONE
    city = TestConstants.CITY
    dt_created = factory.LazyFunction(datetime.now)


class FacultyTypeFactory(BaseFactory):
    class Meta:
        model = FacultyType

    uuid = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('word')


class FacultyFactory(BaseFactory):
    class Meta:
        model = Faculty

    uuid = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('word')
    url = factory.Faker('url')
    type_id = factory.LazyFunction(uuid.uuid4)


class QuestionFactory(BaseFactory):
    class Meta:
        model = Question

    uuid = factory.LazyFunction(uuid.uuid4)
    text = factory.Faker('sentence')


class AnswerFactory(BaseFactory):
    class Meta:
        model = Answer

    uuid = factory.LazyFunction(uuid.uuid4)
    text = factory.Faker('word')
    question_id = factory.LazyFunction(uuid.uuid4)


class ApplicantFacultyFactory(BaseFactory):
    class Meta:
        model = ApplicantFaculty

    uuid = factory.LazyFunction(uuid.uuid4)
    compliance = fuzzy.FuzzyInteger(1, 10)
    applicant_id = factory.LazyFunction(uuid.uuid4)
    faculty_type_id = factory.LazyFunction(uuid.uuid4)


class AnswerFacultyFactory(BaseFactory):
    class Meta:
        model = AnswerFaculty

    uuid = factory.LazyFunction(uuid.uuid4)
    score = fuzzy.FuzzyInteger(1, 5)
    answer_id = factory.LazyFunction(uuid.uuid4)
    faculty_type_id = factory.LazyFunction(uuid.uuid4)