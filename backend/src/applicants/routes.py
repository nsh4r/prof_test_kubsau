from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.database.main import get_session
from backend.src.applicants.schemas import ResponseResult, ApplicantAnswers, ApplicantInfo
from .service import ResultService, QuestionService

api_router = APIRouter(prefix="/backend/api")


@api_router.post("/applicant/by-data/", status_code=status.HTTP_201_CREATED, response_model=ResponseResult)
async def post_result_by_data(user_data: ApplicantInfo, session: AsyncSession = Depends(get_session)):
    """
    Find or create an applicant by full name and phone number.

    Args:
        user_data: The user data containing surname, name, patronymic, and phone_number.
        session

    Returns:
        ResponseResult: The result object.
    """
    return await ResultService(session).post_result_by_data(user_data)


@api_router.post("/results/", status_code=status.HTTP_201_CREATED, response_model=ResponseResult)
async def process_user_answers(user_data: ApplicantAnswers, session: AsyncSession = Depends(get_session)):
    """
    Process user answers and create a new result.

    Args:
        user_data: The user data containing answers.
        session

    Returns:
        ResponseResult: The result object.
    """
    return await ResultService(session).process_user_answers(user_data)


@api_router.get("/questions/", status_code=status.HTTP_200_OK)
async def get_all_questions(session: AsyncSession = Depends(get_session)):
    """
    Get all questions with their answers.

    Returns:
        list: A list of questions with answers.
    """
    return await QuestionService(session).get_all_questions()
