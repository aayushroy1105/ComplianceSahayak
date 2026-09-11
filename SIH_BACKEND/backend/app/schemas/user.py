from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

class OfficerProfile(BaseModel):
    id: UUID
    badge_number: Optional[str] = None
    department: Optional[str] = None
    jurisdiction: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    officer_profile: Optional[OfficerProfile] = None

    model_config = ConfigDict(from_attributes=True)
