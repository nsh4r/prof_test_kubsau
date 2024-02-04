from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Result(BaseModel):
    surname: str = Field(examples=['Ivanov'])
    name: str = Field(examples=['Ivan'])
    patronymic: Optional[str] = Field(examples=['Ivanovich'])
    phone_number: str = Field(max_length=11, examples=['79#########'])

