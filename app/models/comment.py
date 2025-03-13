# app/models/comment.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    linkedin_id = Column(String(255), unique=True, index=True) # LinkedIn comment ID
    content = Column(Text)
    likes_count = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_user_id = Column(Integer, ForeignKey("social_media_users.id"))

    post = relationship("Post", back_populates="comments")
    author = relationship("SocialMediaUser", back_populates="comments")