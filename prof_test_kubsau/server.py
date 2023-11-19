from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import FileResponse
from database import *

app = FastAPI()


class Applicant(BaseModel):
    phone: int
    surname: str
    name: str
    patronymic: str
    city: str


@app.get("/")
def main():
    return FileResponse('public/main.html')


@app.post("/items/{item_id}")
def create_applicant(applicant: list[Applicant]):
    pass
