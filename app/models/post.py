# app/models/post.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    linkedin_id = Column(String(255), unique=True, index=True) # LinkedIn post ID
    content = Column(Text)
    likes_count = Column(Integer)
    comments_count = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    page_id = Column(Integer, ForeignKey("pages.id"))
    author_user_id = Column(Integer, ForeignKey("social_media_users.id"))

    page = relationship("Page", back_populates="posts")
    author = relationship("SocialMediaUser", back_populates="posts")
    comments = relationship("Comment", back_populates="post")