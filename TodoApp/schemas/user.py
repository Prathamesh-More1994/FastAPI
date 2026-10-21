from pydantic import BaseModel, ConfigDict, Field


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    phone_number: str