from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.database.main import get_session
from backend.src.applicants.schemas import (
    ResponseResult, ApplicantAnswers, ApplicantInfo, ApplicantUUIDResponse
)
from uuid import UUID
from .service import ResultService, QuestionService

api_router = APIRouter(prefix="/backend/api")

@api_router.post("/applicant/register/", 
                status_code=status.HTTP_200_OK, 
                response_model=ApplicantUUIDResponse,
                summary="Register or get applicant",
                description="Registers new applicant or returns existing one by phone number")
async def register_applicant(user_data: ApplicantInfo, 
                           session: AsyncSession = Depends(get_session)):
    """
    Register new applicant or get existing one by phone number.
    
    Args:
        user_data: Contains applicant personal information
        
    Returns:
        Dictionary with applicant UUID: {"uuid": "..."}
    """
    service = ResultService(session)
    uuid = await service.register_or_get_applicant(user_data)
    return {"uuid": uuid}

@api_router.get("/applicant/{applicant_uuid}", 
               status_code=status.HTTP_200_OK, 
               response_model=ResponseResult,
               summary="Get applicant results",
               description="Returns applicant data and test results by UUID")
async def get_applicant_results(applicant_uuid: UUID, 
                              session: AsyncSession = Depends(get_session)):
    """
    Get applicant results by UUID.
    
    Args:
        applicant_uuid: UUID of the applicant
        
    Returns:
        Complete applicant data with test results
        
    Raises:
        HTTPException: 404 if applicant not found
    """
    service = ResultService(session)
    return await service.get_applicant_results(applicant_uuid)

@api_router.post("/results/", 
                status_code=status.HTTP_201_CREATED, 
                response_model=ResponseResult,
                summary="Process test answers",
                description="Processes test answers and updates applicant results")
async def process_user_answers(user_data: ApplicantAnswers, 
                             session: AsyncSession = Depends(get_session)):
    """
    Process user answers and create/update test results.
    
    Args:
        user_data: Contains applicant UUID and list of answers
        
    Returns:
        Updated applicant data with test results
        
    Raises:
        ValueError: If applicant not found
    """
    service = ResultService(session)
    return await service.process_user_answers(user_data)

@api_router.get("/questions/", 
               status_code=status.HTTP_200_OK,
               summary="Get all questions",
               description="Returns all questions with possible answers")
async def get_all_questions(session: AsyncSession = Depends(get_session)):
    """
    Get all questions with their answers.
    
    Returns:
        List of questions with answer options
        
    Raises:
        HTTPException: 404 if no questions found
    """
    service = QuestionService(session)
    return await service.get_all_questions()