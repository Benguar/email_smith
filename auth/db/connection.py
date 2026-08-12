from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from core.settings import settings

try:
    engine = create_async_engine(settings.URL)

    Asyncsession = async_sessionmaker(bind= engine,autoflush=False,autocommit= False)
    async def get_db():
        async with Asyncsession() as session:
            yield session
except Exception as e:
    print(f' there is an error {e}')