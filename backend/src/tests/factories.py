import uuid
from datetime import datetime
import factory
from factory import fuzzy

from backend.src.database.models import (
    Applicant, Faculty, FacultyType, Question, Answer,
    ApplicantFaculty, AnswerFaculty
)
from backend.src.tests.utils import TestConstants


class AsyncSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session
        async with session.begin():
            instance = model_class(*args, **kwargs)
            session.add(instance)
            await session.commit()
        return instance

    @classmethod
    async def create(cls, **kwargs):
        return await cls._generate(enums.CREATE_STRATEGY, kwargs)


class ApplicantFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Applicant

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    surname = TestConstants.SURNAME
    name = TestConstants.NAME
    patronymic = TestConstants.PATRONYMIC
    phone_number = TestConstants.PHONE
    city = TestConstants.CITY
    dt_created = factory.LazyFunction(datetime.now)


class FacultyTypeFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = FacultyType

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    name = factory.Faker('word')


class FacultyFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Faculty

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    name = factory.Faker('word')
    url = factory.Faker('url')
    type_id = factory.LazyAttribute(lambda o: uuid.uuid4())


class QuestionFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Question

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    text = factory.Faker('sentence')


class AnswerFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Answer

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    text = factory.Faker('word')
    question_id = factory.LazyAttribute(lambda o: uuid.uuid4())


class ApplicantFacultyFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = ApplicantFaculty

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    compliance = fuzzy.FuzzyInteger(1, 10)
    applicant_id = factory.LazyAttribute(lambda o: uuid.uuid4())
    faculty_type_id = factory.LazyAttribute(lambda o: uuid.uuid4())


class AnswerFacultyFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = AnswerFaculty

    uuid = factory.LazyAttribute(lambda o: uuid.uuid4())
    score = fuzzy.FuzzyInteger(1, 5)
    answer_id = factory.LazyAttribute(lambda o: uuid.uuid4())
    faculty_type_id = factory.LazyAttribute(lambda o: uuid.uuid4())