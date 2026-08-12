from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import DateTime,func,ForeignKey
from uuid6 import uuid7
from datetime import datetime
import uuid
from db.connection import engine
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_table"
    id:Mapped[uuid.UUID] = mapped_column(primary_key= True,nullable= False, default= uuid7)
    email: Mapped[str] = mapped_column(nullable=False,unique=True)
    auth_method:Mapped[str] = mapped_column(nullable=False)
    verified_email:Mapped[bool] = mapped_column(nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

class Refresh(Base):
    __tablename__ = "refresh_table"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('user_table.id', ondelete="CASCADE"), nullable=False)
    refresh_jti: Mapped[str] = mapped_column(primary_key=True,nullable=False)
    is_revoked: Mapped[bool] = mapped_column(nullable=False) #This is for Logouts 
    is_used: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)
    ip: Mapped[str] = mapped_column(nullable=True) 

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)