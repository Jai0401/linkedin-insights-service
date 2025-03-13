# app/schemas/social_media_user.py
from pydantic import BaseModel
from typing import Optional, List

class SocialMediaUserBase(BaseModel):
    name: Optional[str] = None
    profile_url: Optional[str] = None
    profile_picture: Optional[str] = None

class SocialMediaUserCreate(SocialMediaUserBase):
    linkedin_id: str

class SocialMediaUserUpdate(SocialMediaUserBase):
    pass

class SocialMediaUserInDBBase(SocialMediaUserBase):
    id: int
    linkedin_id: str
    page_id: int

    class Config:
        from_attributes = True

class SocialMediaUser(SocialMediaUserInDBBase):
    pass

class SocialMediaUserSearchResults(BaseModel):
    results: List[SocialMediaUser]