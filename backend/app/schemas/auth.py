from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str
    user_id: int


class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    phone: str
    status: str

    class Config:
        from_attributes = True
