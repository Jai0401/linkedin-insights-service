# LinkedIn Insights Microservice Documentation
## Project Overview
### Purpose
The LinkedIn Insights Microservice is designed to scrape and store data from LinkedIn company pages. It provides an API to retrieve information about companies, their employees, and recent posts. This data can be used for market research, lead generation, or competitive analysis.
### Key Features
*   **Scraping LinkedIn Company Pages:** Extracts data such as company name, description, industry, followers count, website, head count, recent posts, and employee information.
*   **Data Storage:** Stores scraped data in a MySQL database.
*   **API Endpoints:** Provides RESTful API endpoints to access the stored data.
*   **Filtering and Pagination:** Supports filtering pages by name, industry, and follower count, with pagination for large datasets.
*   **Automatic Scraping:** If a page is not found in the database, the microservice attempts to scrape it from LinkedIn.
### Supported Platforms/Requirements
*   **Platform:** Dockerized application, designed to run on any platform that supports Docker.
*   **Requirements:**
    *   Docker
    *   Docker Compose
    *   Python 3.9+
    *   MySQL Database
## Getting Started
### Installation/Setup Instructions
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Jai0401/linkedin-insights-service
    cd linkedin-insights-service
    ```
2.  **Configure Environment Variables:**
    *   Create a `.env` file in the root directory.
    *   Add the following environment variables:
        ```bash
          DATABASE_URL=mysql+mysqlconnector://app_user:app_password@db:3306/linkedin_insights_db
        ```
    *   Replace `app_user`, `app_password`, and `linkedin_insights_db` with your MySQL credentials and database name.
3.  **Start the application using Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This command builds the Docker image and starts the application along with the MySQL database.
4.  **Access the API:**
    *   The API will be available at `http://localhost:8000`.
### Dependencies/Prerequisites
The following dependencies are required to run the application. These are automatically installed when building the Docker image.
*   fastapi
*   uvicorn\[standard]
*   SQLAlchemy
*   mysqlclient
*   requests
*   beautifulsoup4
*   python-dotenv
*   mysql-connector-python

## API Documentation
### Endpoints
#### 1. Get a list of pages
*   **Endpoint:** `GET /pages/`
*   **Description:** Retrieves a list of pages with optional filters and pagination.
*   **Parameters:**
    *   `skip` (int, optional): Number of records to skip for pagination (default: 0).
    *   `limit` (int, optional): Maximum number of records to return (default: 10).
    *   `name` (str, optional): Search by page name (case-insensitive).
    *   `industry` (str, optional): Filter by industry.
    *   `min_followers` (int, optional): Filter by minimum followers.
    *   `max_followers` (int, optional): Filter by maximum followers.
*   **Input:** None (parameters are passed in the query string)
*   **Output:** A list of `Page` objects.
*   **Example Request:**
    ```bash
        GET /pages/?skip=0&limit=5&name=deep&industry=Information Technology&min_followers=1000&max_followers=5000
    ```
*   **Example Response:**
    ```json
    [
      {
        "page_id": "deepsolv",
        "name": "DeepSolv",
        "url": "https://www.linkedin.com/company/deepsolv/",
        "profile_picture": "https://media.licdn.com/dms/image/example.jpg",
        "description": "AI-powered solutions for...",
        "website": "https://www.deepsolv.com",
        "industry": "Information Technology",
        "followers_count": 2500,
        "head_count": "11-50 employees",
        "specialities": "AI, Machine Learning,...",
        "id": 1,
        "linkedin_id": "deepsolv"
      }
    ]
    ```
#### 2. Get details of a page by its page_id
*   **Endpoint:** `GET /pages/{page_id}`
*   **Description:** Retrieves details of a page by its `page_id`. If the page is not in the database, it will be scraped and stored.
*   **Parameters:**
    *   `page_id` (str, required): The LinkedIn page ID (e.g., "deepsolv").
*   **Input:** None (page_id is passed in the URL)
*   **Output:** A `Page` object.
*   **Example Request:**
    ```bash
        GET /pages/deepsolv
    ```
*   **Example Response (Page Exists):**
    ```json
    {
      "page_id": "deepsolv",
      "name": "DeepSolv",
      "url": "https://www.linkedin.com/company/deepsolv/",
      "profile_picture": "https://media.licdn.com/dms/image/example.jpg",
      "description": "AI-powered solutions for...",
      "website": "https://www.deepsolv.com",
      "industry": "Information Technology",
      "followers_count": 2500,
      "head_count": "11-50 employees",
      "specialities": "AI, Machine Learning,...",
      "id": 1,
      "linkedin_id": "deepsolv"
    }
    ```
*   **Example Response (Page Not Found):**
    ```json
    {
      "detail": "Page not found or could not be scraped"
    }
    ```
#### 3. Get employees of a page
*   **Endpoint:** `GET /pages/{page_id}/employees`
*   **Description:** Retrieves employees of a page.
*   **Parameters:**
    *   `page_id` (str, required): The LinkedIn page ID (e.g., "deepsolv").
    *   `skip` (int, optional): Number of records to skip for pagination (default: 0).
    *   `limit` (int, optional): Maximum number of records to return (default: 10).
*   **Input:** None (parameters are passed in the query string)
*   **Output:** A list of `SocialMediaUser` objects.
*   **Example Request:**
    ```bash
        GET /pages/deepsolv/employees?skip=0&limit=5
    ```
*   **Example Response:**
    ```json
    [
      {
        "name": "John Doe",
        "profile_url": "https://www.linkedin.com/in/johndoe/",
        "profile_picture": "https://media.licdn.com/dms/image/example.jpg",
        "id": 1,
        "linkedin_id": "employee-123",
        "page_id": 1
      }
    ]
    ```
#### 4. Get recent posts of a page
*   **Endpoint:** `GET /pages/{page_id}/posts`
*   **Description:** Retrieves recent posts of a page.
*   **Parameters:**
    *   `page_id` (str, required): The LinkedIn page ID (e.g., "deepsolv").
    *   `skip` (int, optional): Number of records to skip for pagination (default: 0).
    *   `limit` (int, optional): Maximum number of records to return (default: 15).
*   **Input:** None (parameters are passed in the query string)
*   **Output:** A list of `Post` objects.
*   **Example Request:**
    ```bash
        GET /pages/deepsolv/posts?skip=0&limit=5
    ```
*   **Example Response:**
    ```json
    [
      {
        "content": "Excited to announce our new partnership...",
        "likes_count": 120,
        "comments_count": 30,
        "id": 1,
        "linkedin_id": "post-456",
        "page_id": 1,
        "author_user_id": 1
      }
    ]
    ```
