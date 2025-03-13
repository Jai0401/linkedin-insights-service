# app/models/__init__.py
from app.core.database import Base

# Import models after Base is defined
from .page import Page
from .post import Post
from .social_media_user import SocialMediaUser
from .comment import Comment

__all__ = ["Base", "Page", "Post", "SocialMediaUser", "Comment"]