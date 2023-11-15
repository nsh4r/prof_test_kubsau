from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


class Applicant:
    def __init__(self, phone: str, surname: str, name: str, patronymic: str, city: str):
        self.phone = phone
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.city = city


@app.get("/")
def main():
    return FileResponse('public/main.html')


@app.post("/items/{item_id}")
def create_applicant(phone: str, surname: str, name: str, city: str, patronymic: str = None):
    pass
