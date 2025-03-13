# app/models/page.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(String(255), unique=True, index=True, nullable=False) # LinkedIn Page ID (e.g., deepsolv)
    linkedin_id = Column(String(255), unique=True, index=True) # LinkedIn platform specific ID
    name = Column(String(255))
    url = Column(String(255))
    profile_picture = Column(String(255)) # URL to profile picture
    description = Column(Text)
    website = Column(String(255))
    industry = Column(String(255))
    followers_count = Column(Integer)
    head_count = Column(String(255))
    specialities = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    posts = relationship("Post", back_populates="page")
    employees = relationship("SocialMediaUser", back_populates="page")

    __table_args__ = (UniqueConstraint('page_id', name='uq_page_page_id'),)