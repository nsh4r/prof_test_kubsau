import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.__init__ import app
from backend.src.tests.factories import ApplicantFactory
from backend.src.tests.utils import TestConstants

client = TestClient(app)


@pytest.mark.asyncio
class TestApplicantRoutes:
    async def test_post_result_by_data(self, session: AsyncSession):
        response = client.post(
            "/backend/api/applicant/by-data/",
            json={
                "surname": TestConstants.SURNAME,
                "name": TestConstants.NAME,
                "patronymic": TestConstants.PATRONYMIC,
                "phone_number": TestConstants.PHONE,
                "city": TestConstants.CITY
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["surname"] == TestConstants.SURNAME
        assert data["name"] == TestConstants.NAME
        assert data["phone_number"] == TestConstants.PHONE

    async def test_post_result_by_data_invalid_phone(self):
        response = client.post(
            "/backend/api/applicant/by-data/",
            json={
                "surname": TestConstants.SURNAME,
                "name": TestConstants.NAME,
                "patronymic": TestConstants.PATRONYMIC,
                "phone_number": "invalid",
                "city": TestConstants.CITY
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_process_user_answers(self, session: AsyncSession):
        applicant = await ApplicantFactory.create()

        response = client.post(
            "/backend/api/results/",
            json={
                "uuid": str(applicant.uuid),
                "answers": []
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["uuid"] == str(applicant.uuid)

    async def test_get_questions(self, session: AsyncSession):
        response = client.get("/backend/api/questions/")

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND)