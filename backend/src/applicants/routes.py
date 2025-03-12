from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.database.main import get_session
from backend.src.applicants.schemas import ResponseResult, UserAnswers
from .service import ResultService, QuestionService

api_router = APIRouter(prefix="/backend/api")


@api_router.get("/results/{phone_number}", response_model=ResponseResult)
async def get_result_by_phone(phone_number: str, session: AsyncSession = Depends(get_session)):
    """
    Get a result by phone number.

    Args:
        phone_number (str): The phone number of the result.
        session

    Returns:
        ResponseResult: The result object.
    """
    return await ResultService(session).get_result_by_phone(phone_number)


@api_router.post("/results/", status_code=status.HTTP_201_CREATED, response_model=ResponseResult)
async def process_user_answers(user_data: UserAnswers, session: AsyncSession = Depends(get_session)):
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