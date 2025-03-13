# app/models/social_media_user.py
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class SocialMediaUser(Base):
    __tablename__ = "social_media_users"

    id = Column(Integer, primary_key=True, index=True)
    linkedin_id = Column(String(255), unique=True, index=True) # LinkedIn user ID
    name = Column(String(255))
    profile_url = Column(String(255))
    profile_picture = Column(String(255)) # URL to profile picture
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    page_id = Column(Integer, ForeignKey("pages.id")) # For people working there, linked to page

    page = relationship("Page", back_populates="employees")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")