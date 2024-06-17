from sqlmodel import Field, SQLModel


class ResultInfo(SQLModel):
    """Входные данные для API получения результата"""
    surname: str = Field(schema_extra={'example': 'Ivanov'})
    name: str = Field(schema_extra={'example': 'Ivan'})
    patronymic: str | None = Field(default=None, schema_extra={'example': 'Ivanovich'})
    phone_number: str = Field(schema_extra={'example': '79000000000'}, max_length=11, regex=r'^79\d{9}$')


class FacultyType(SQLModel):
    """Информация о классификации факультета"""

    name: str = Field(min_length=1, schema_extra={'example': 'Человек-Природа'})


class Faculty(SQLModel):
    """Информация о факультете"""

    name: str = Field(min_length=1)
    url: str = Field(min_length=1)


class ResponseResult(ResultInfo):
    """Выходные данные для API получения результата"""

    faculty_type: str = Field(min_length=1)
    faculties: list[Faculty]
    compliance: int = Field(gt=0)

