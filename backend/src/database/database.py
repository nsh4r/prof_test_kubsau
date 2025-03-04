from sqlalchemy.ext.asyncio import create_async_engine

from backend.src.config import settings


engine = create_async_engine(url=settings.database_url, echo=True)



