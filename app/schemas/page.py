# app/schemas/page.py
from pydantic import BaseModel, AnyHttpUrl
from typing import List, Optional

class PageBase(BaseModel):
    page_id: str
    name: Optional[str] = None
    url: Optional[str] = None
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    followers_count: Optional[int] = None
    head_count: Optional[str] = None
    specialities: Optional[str] = None

class PageCreate(PageBase):
    linkedin_id: Optional[str] = None


class PageUpdate(PageBase):
    pass

class PageInDBBase(PageBase):
    id: int
    linkedin_id: Optional[str]

    class Config:
        from_attributes = True

class Page(PageInDBBase):
    pass

class PageSearchResults(BaseModel):
    results: List[Page]