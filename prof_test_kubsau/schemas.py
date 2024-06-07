from pydantic import BaseModel, Field
from typing import Optional


class ResultInfo(BaseModel):
    """Входные данные для API получения результата"""

    surname: str = Field(examples=['Иванов'], min_length=1)
    name: str = Field(examples=['Иван'], min_length=1)
    patronymic: str = Field(examples=['Иванович', ''], default='')
    phone_number: str = Field(examples=['79000000000'], pattern=r'^79\d{9}$')


class Faculty(BaseModel):
    """Информация о факультете"""

    name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    score: int = Field(gt=0)


class ResponseResult(BaseModel):
    """Выходные данные для API получения результата"""

    surname: str = Field(examples=['Ivanov'])
    name: str = Field(examples=['Ivan'])
    patronymic: Optional[str] = Field(examples=['Ivanovich'])
    phone_number: str = Field(max_length=11, examples=['79000000000'])
    faculties: list[Faculty]

