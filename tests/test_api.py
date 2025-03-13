# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base, engine
from sqlalchemy.orm import Session

client = TestClient(app)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

SessionLocal = Session(bind=engine) # Use the same engine for testing
Base.metadata.create_all(bind=engine) # Create tables for testing

app.dependency_overrides[get_db] = override_get_db

def test_read_page_existing():
    page_id = "deepsolv" # Example page ID, might need to pre-populate DB for real test
    response = client.get(f"/pages/{page_id}")
    assert response.status_code == 200
    assert response.json()["page_id"] == page_id

def test_read_page_not_found():
    page_id = "non_existent_page_id"
    response = client.get(f"/pages/{page_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Page not found or could not be scraped"}

# Add more tests as needed for filters, employees, posts, etc.