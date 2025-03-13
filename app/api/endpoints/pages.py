# app/api/endpoints/pages.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import page_service
from app.schemas import page as page_schema, social_media_user as user_schema, post as post_schema

router = APIRouter(prefix="/pages", tags=["pages"])

@router.get("/", response_model=List[page_schema.Page])
async def read_pages(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = Query(None, description="Search by page name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    min_followers: Optional[int] = Query(None, description="Filter by minimum followers"),
    max_followers: Optional[int] = Query(None, description="Filter by maximum followers"),
):
    """
    Get a list of pages, with optional filters and pagination.
    """
    pages = page_service.get_paged_pages(db, skip=skip, limit=limit, name=name, industry=industry, min_followers=min_followers, max_followers=max_followers)
    return pages

@router.get("/{page_id}", response_model=page_schema.Page)
async def read_page(page_id: str, db: Session = Depends(get_db)):
    """
    Get details of a page by its page_id.
    If the page is not in the database, it will be scraped and stored.
    """
    db_page = page_service.get_page_by_page_id(db, page_id=page_id)
    if db_page:
        return db_page
    else:
        db_page = page_service.scrape_and_save_page(db, page_id=page_id)
        if db_page:
            return db_page
        else:
            raise HTTPException(status_code=404, detail="Page not found or could not be scraped")

@router.get("/{page_id}/employees", response_model=List[user_schema.SocialMediaUser])
async def read_page_employees(page_id: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    Get employees of a page.
    """
    employees = page_service.get_page_employees(db, page_id=page_id, skip=skip, limit=limit)
    return employees

@router.get("/{page_id}/posts", response_model=List[post_schema.Post])
async def read_page_posts(page_id: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 15): # Default limit to 15 as per requirement
    """
    Get recent posts of a page.
    """
    posts = page_service.get_page_posts(db, page_id=page_id, skip=skip, limit=limit)
    return posts