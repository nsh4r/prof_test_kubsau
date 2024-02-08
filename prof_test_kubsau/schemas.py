from pydantic import BaseModel, Field, field_validator
from typing import Optional


class QueryResult(BaseModel):
    surname: str = Field(examples=['Ivanov'])
    name: str = Field(examples=['Ivan'])
    patronymic: Optional[str] = Field(examples=['Ivanovich'])
    phone_number: str = Field(max_length=11, examples=['79000000000'])


class ResponseResult(BaseModel):
    surname: str = Field(examples=['Ivanov'])
    name: str = Field(examples=['Ivan'])
    patronymic: Optional[str] = Field(examples=['Ivanovich'])
    phone_number: str = Field(max_length=11, examples=['79000000000'])
    faculty_name: str = Field(examples=['Факультет информационных технологий'])
    faculty_url: str = Field(examples=['https://kubsau.ru'])
    compliance: int = Field(examples=[100])

