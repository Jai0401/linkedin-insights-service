# app/schemas/post.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class PostBase(BaseModel):
    content: Optional[str] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None

class PostCreate(PostBase):
    linkedin_id: str
    page_id: int
    author_user_id: int

class PostUpdate(PostBase):
    pass

class PostInDBBase(PostBase):
    id: int
    linkedin_id: str
    page_id: int
    author_user_id: int

    class Config:
        from_attributes = True

class Post(PostInDBBase):
    pass

class PostSearchResults(BaseModel):
    results: List[Post]