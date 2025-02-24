import factory

from backend.modules.database import Result
from backend.tests.utils import Session


class ResultFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Result
        sqlalchemy_session = Session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: 'Name %d' % n)
    surname = factory.Sequence(lambda n: 'Surname %d' % n)
    patronymic = factory.Sequence(lambda n: 'Patronymic %d' % n)
