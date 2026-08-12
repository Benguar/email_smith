from fastapi import APIRouter,status,HTTPException,Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from core.settings import settings
import httpx
route = APIRouter()


GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"
 
@route.get("/google-auth/signup",)
async def google_auth():
    query_params = {
    "client_id": settings.GOOGLE_CLIENT_ID ,
    "redirect_uri": settings.GOOGLE_REDIRECT_URL ,
    "response_type": "code",
    "scope": "openid email profile https://www.googleapis.com/auth/gmail.send https://mail.google.com/",
    "access_type": "offline",
    "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(query_params)}"
    return RedirectResponse(url)
@route.get("/google-auth/callback",)
async def google_auth(request: Request):
    code = request.query_params.get("code")
    print(f'code: {code}')
    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'authorization code not found')
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URL,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data=data
        )
        response_data= response.json()
        print(f'response: {response_data}')
        access_token = response_data.get("access_token")
        get_user_info =await client.get(GOOGLE_USERINFO_ENDPOINT,headers= {"Authorization": f'Bearer {access_token}'})
        user_info = get_user_info.json()
        print(f'user_info: {user_info}')

      
    return RedirectResponse(f"http://127.0.0.1:8000/users/v1/google-authentication?email={user_info.get("email")}&verified_email={user_info.get("verified_email")}&picture={user_info.get("picture")}&refresh_token={response_data.get("refresh_token")}")