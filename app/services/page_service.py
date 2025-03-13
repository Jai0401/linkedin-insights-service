# app/services/page_service.py
from sqlalchemy.orm import Session
from app.models import Page, Post, SocialMediaUser
from app.schemas import page as page_schema, post as post_schema, social_media_user as user_schema
from app.core.scraper import scrape_linkedin_page
from typing import List, Optional
from urllib.parse import urlparse
import hashlib
import time

def get_page_by_page_id(db: Session, page_id: str) -> Optional[Page]:
    return db.query(Page).filter(Page.page_id == page_id).first()

def create_page(db: Session, page: page_schema.PageCreate) -> Page:
    db_page = Page(**page.dict())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_page(db: Session, db_page: Page, page_update: page_schema.PageUpdate) -> Page:
    for key, value in page_update.dict(exclude_unset=True).items():
        setattr(db_page, key, value)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def generate_unique_id(prefix: str, *args) -> str:
    """Generate a unique ID based on multiple arguments"""
    combined = "-".join(str(arg) for arg in args)
    hash_object = hashlib.md5(combined.encode())
    return f"{prefix}-{hash_object.hexdigest()[:8]}"

def clean_url(url: str) -> Optional[str]:
    if not url:
        return None
    # Remove any redirect prefixes from LinkedIn URLs
    if 'linkedin.com/redir/redirect?' in url and 'url=' in url:
        try:
            # Extract the actual URL from LinkedIn's redirect URL
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(url)
            actual_url = parse_qs(parsed.query)['url'][0]
            return actual_url
        except:
            pass
    
    # Fix various LinkedIn URL formats
    if url.startswith('https://www.linkedin.comhttps://'):
        url = url.replace('https://www.linkedin.comhttps://', 'https://')
    elif url.startswith('https://in.linkedin.com'):
        url = url.replace('https://in.linkedin.com', 'https://www.linkedin.com')
    elif url.startswith('https://www.linkedin.com/in/'):
        # Remove any query parameters from profile URLs
        url = url.split('?')[0]
    
    # Ensure the URL is properly formatted
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def scrape_and_save_page(db: Session, page_id: str) -> Optional[Page]:
    try:
        # Get data from the scraper
        scraped_data = scrape_linkedin_page(page_id)
        if not scraped_data:
            print(f"No data returned from scraper for page_id: {page_id}")
            return None

        # Clean URLs but don't validate them - let the schema handle validation
        url = clean_url(scraped_data.get('url'))
        profile_picture = clean_url(scraped_data.get('profile_picture'))
        website = clean_url(scraped_data.get('website'))

        # Prepare page data for database
        page_data = {
            'page_id': page_id,
            'linkedin_id': page_id,  # Using page_id as linkedin_id since it's the same
            'name': scraped_data.get('name'),
            'url': url,
            'profile_picture': profile_picture,
            'description': scraped_data.get('description'),
            'website': website,
            'industry': scraped_data.get('industry'),
            'followers_count': scraped_data.get('followers_count', 0),  # Default to 0 if not found
            'head_count': scraped_data.get('head_count'),
            'specialities': scraped_data.get('specialities')
        }

        # Remove None values for optional fields to avoid validation errors
        page_data = {k: v for k, v in page_data.items() if v is not None}

        # Check if page exists
        db_page = get_page_by_page_id(db, page_id)
        if db_page:
            # Page exists, update it
            page_update_schema = page_schema.PageUpdate(**page_data)
            db_page = update_page(db, db_page, page_update_schema)
        else:
            # Page does not exist, create new
            page_create_schema = page_schema.PageCreate(**page_data)
            db_page = create_page(db, page_create_schema)

        # Handle posts
        if 'posts' in scraped_data and scraped_data['posts']:
            for idx, post_data in enumerate(scraped_data['posts']):
                # Create a placeholder user for the author if needed
                author_user = db.query(SocialMediaUser).filter(
                    SocialMediaUser.page_id == db_page.id,
                    SocialMediaUser.name == "Default Page Author"
                ).first()
                
                if not author_user:
                    author_user = SocialMediaUser(
                        linkedin_id=generate_unique_id("author", db_page.id, "default"),
                        name="Default Page Author",
                        page_id=db_page.id
                    )
                    db.add(author_user)
                    db.flush()  # Get the ID

                # Generate a unique post ID based on content and timestamp
                post_id = generate_unique_id("post", db_page.id, post_data.get('content', ''), idx)
                
                # Check if post already exists
                existing_post = db.query(Post).filter(Post.linkedin_id == post_id).first()
                if not existing_post:
                    # Create the post
                    post_create = post_schema.PostCreate(
                        linkedin_id=post_id,
                        content=post_data.get('content', ''),
                        likes_count=0,  # Default values since they're not in the scraped data
                        comments_count=0,
                        page_id=db_page.id,
                        author_user_id=author_user.id
                    )
                    db_post = Post(**post_create.dict())
                    db.add(db_post)

        # Handle employees
        if 'employees' in scraped_data and scraped_data['employees']:
            for employee_data in scraped_data['employees']:
                try:
                    # Clean URLs
                    profile_url = clean_url(employee_data.get('profile_url'))
                    profile_picture = clean_url(employee_data.get('profile_picture'))
                    name = employee_data.get('name', 'Unknown Employee')

                    # Generate a unique employee ID based on their name and profile URL
                    employee_id = generate_unique_id("employee", db_page.id, name, profile_url or '')

                    # Check if employee already exists
                    existing_employee = db.query(SocialMediaUser).filter(
                        SocialMediaUser.linkedin_id == employee_id
                    ).first()

                    if not existing_employee:
                        # Create employee data
                        employee_data_clean = {
                            'linkedin_id': employee_id,
                            'name': name,
                            'page_id': db_page.id
                        }
                        
                        # Only add URLs if they exist and are valid
                        if profile_url:
                            employee_data_clean['profile_url'] = profile_url
                        if profile_picture:
                            employee_data_clean['profile_picture'] = profile_picture

                        # Create the employee directly without using the schema
                        db_employee = SocialMediaUser(**employee_data_clean)
                        db.add(db_employee)
                        db.flush()  # Get the ID immediately
                except Exception as e:
                    print(f"Error creating employee {name}: {e}")
                    db.rollback()  # Rollback just this employee
                    continue

        db.commit()
        db.refresh(db_page)
        return db_page
        
    except Exception as e:
        print(f"Error in scrape_and_save_page for page_id {page_id}: {e}")
        db.rollback()
        return None

def get_paged_pages(db: Session, skip: int = 0, limit: int = 10, name: Optional[str] = None, industry: Optional[str] = None, min_followers: Optional[int] = None, max_followers: Optional[int] = None) -> List[Page]:
    query = db.query(Page)

    if name:
        query = query.filter(Page.name.ilike(f"%{name}%")) # ilike for case-insensitive search

    if industry:
        query = query.filter(Page.industry == industry)

    if min_followers is not None and max_followers is not None:
        query = query.filter(Page.followers_count >= min_followers, Page.followers_count <= max_followers)
    elif min_followers is not None:
        query = query.filter(Page.followers_count >= min_followers)
    elif max_followers is not None:
        query = query.filter(Page.followers_count <= max_followers)

    return query.offset(skip).limit(limit).all()

def get_page_employees(db: Session, page_id: str, skip: int = 0, limit: int = 10) -> List[SocialMediaUser]:
    db_page = get_page_by_page_id(db, page_id)
    if not db_page:
        return []
    return db.query(SocialMediaUser).filter(SocialMediaUser.page_id == db_page.id).offset(skip).limit(limit).all()

def get_page_posts(db: Session, page_id: str, skip: int = 0, limit: int = 10) -> List[Post]:
    db_page = get_page_by_page_id(db, page_id)
    if not db_page:
        return []
    return db.query(Post).filter(Post.page_id == db_page.id).offset(skip).limit(limit).all()