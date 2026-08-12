from fastapi import APIRouter,Depends,HTTPException,status,Response
from db.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert,select
from db.models import  Refresh
from schemas.classes import User_class
from db.models import User
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from uuid6 import uuid7
route = APIRouter()




@route.get("/google-authentication")
async def google_authentication(email: str, verified_email: bool,picture: str,refresh_token: str, db: AsyncSession = Depends(get_db)):
    print(verified_email)
    #add users to test here
    try:
        query = await db.execute(insert(User).values(email=email,verified_email = verified_email,auth_method= 'google').returning(User))
        result = query.scalars().first()
        await db.commit()
        response = RedirectResponse(f"http://127.0.0.1:5500/frontend/home.html?email={email}&picture={picture}")
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )
        response.set_cookie(
            key="thread_id",
            value=str(uuid7()),
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )
        return response
    except IntegrityError:
        await db.close()
        query = await db.execute(select(User).filter(User.email ==email))
        result =  query.scalars().first()
        response = RedirectResponse(f"http://127.0.0.1:5500/frontend/home.html?email={email}&picture={picture}")
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )
        response.set_cookie(
            key="thread_id",
            value=str(uuid7()),
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )
        return response