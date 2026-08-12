from pydantic import BaseModel,ConfigDict,EmailStr,SecretStr,Field
from datetime import datetime
class User_class(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr = Field(min_length= 8)

class Login(BaseModel):
    username: str
    password: SecretStr
class Token(BaseModel):
    access_token: str
    refresh_token: str
    jti: str
class RefreshInput(BaseModel):
    user_id: str
    refresh_jti: str
    is_revoked: bool = False
    is_used: bool = False
    expire_at: datetime
class TokenData(BaseModel):
    id: str|None = None
    jti: str| None = None
class SendPrompt(BaseModel):
    email: str
    prompt: str
class ResumePrompt(BaseModel):
    decision: str
    email: str
    recipient_email: str
    subject: str
    body: str