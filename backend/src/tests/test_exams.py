import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from ..applicants.service import ExamsService

@pytest.mark.asyncio
async def test_get_all_exams(test_data):
    async with AsyncSession(bind=test_data.bind) as session:
        service = ExamsService(session)
        result = await service.get_all_exams()
        assert len(result.exams) >= 2
        codes = [exam.code for exam in result.exams]
        assert "rus" in codes
        assert "math_basic" in codes

@pytest.mark.asyncio
async def test_get_all_required_exams(test_data):
    async with AsyncSession(bind=test_data.bind) as session:
        service = ExamsService(session)
        result = await service.get_all_required_exams()
        assert len(result.required_exams) >= 2
        codes = [req.exam_code for req in result.required_exams]
        assert "rus" in codes
        assert "math_basic" in codes
