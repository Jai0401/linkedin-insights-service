# app/core/scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def clean_linkedin_url(url: str) -> str:
    """Clean and standardize LinkedIn URLs"""
    if not url:
        return None
    
    # Remove the linkedin.com prefix if it's duplicated
    if url.startswith('https://www.linkedin.comhttps://'):
        url = url.replace('https://www.linkedin.comhttps://', 'https://')
    elif url.startswith('https://www.linkedin.comhttp://'):
        url = url.replace('https://www.linkedin.comhttp://', 'http://')
    
    # Convert regional domains to main domain
    if '//in.linkedin.com' in url:
        url = url.replace('//in.linkedin.com', '//www.linkedin.com')
    
    # Remove query parameters from profile URLs
    if '/in/' in url:
        base_url = url.split('?')[0]
        return base_url.rstrip('/')
    
    return url.rstrip('/')

def scrape_linkedin_page(page_id: str):
    base_url = "https://www.linkedin.com"
    company_url = f"{base_url}/company/{page_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        response = requests.get(company_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize page_data with default values
        page_data = {
            'page_id': page_id,
            'linkedin_id': page_id,
            'name': None,
            'url': company_url,
            'profile_picture': None,
            'description': None,
            'website': None,
            'industry': None,
            'followers_count': 0,
            'head_count': None,
            'specialities': None,
            'posts': [],
            'employees': []
        }

        # Company Name - Multiple possible selectors
        for name_selector in [
            "h1.top-card-layout__title",
            "h1.org-top-card-summary__title",
            "h1.ember-view"
        ]:
            name_tag = soup.select_one(name_selector)
            if name_tag:
                page_data['name'] = name_tag.text.strip()
                break

        # Profile Picture - Multiple possible selectors
        for img_selector in [
            "img.org-top-card-primary-content__logo",
            "img.artdeco-entity-image",
            "img.inline-block"
        ]:
            img_tag = soup.select_one(img_selector)
            if img_tag and img_tag.get('src'):
                page_data['profile_picture'] = clean_linkedin_url(img_tag['src'])
                break

        # Description - Multiple sections
        description_parts = []
        for desc_selector in [
            "p.org-top-card-summary__tagline",
            "p.org-about-us-organization-description__text",
            "div.org-about-us-organization-description",
            "div.white-space-pre-wrap"
        ]:
            desc_tag = soup.select_one(desc_selector)
            if desc_tag:
                description_parts.append(desc_tag.text.strip())
        
        if description_parts:
            page_data['description'] = " ".join(description_parts).strip()

        # Industry
        industry_tag = soup.select_one("dd[data-test-id='about-us__industry'], .org-about-company-module__industry")
        if industry_tag:
            page_data['industry'] = industry_tag.text.strip()

        # Followers Count
        followers_tag = soup.select("div.org-top-card-summary-info-list__info-item")
        print(followers_tag)
        if followers_tag:
            followers_text = followers_tag.text.strip()
            if "followers" in followers_text.lower():
                try:
                    count_str = ''.join(filter(str.isdigit, followers_text))
                    if count_str:
                        page_data['followers_count'] = int(count_str)
                except ValueError:
                    pass

        # Website
        website_tag = soup.select_one("a[data-test-id='about-us__website'], .org-about-company-module__website")
        if website_tag and website_tag.get('href'):
            page_data['website'] = clean_linkedin_url(website_tag['href'])

        # Head Count
        headcount_tag = soup.select_one("dd[data-test-id='about-us__size'], .org-about-company-module__company-size")
        if headcount_tag:
            page_data['head_count'] = headcount_tag.text.strip()

        # Posts
        posts_section = soup.select("div.org-update-card, article.main-feed-activity-card")
        for post in posts_section[:5]:  # Get latest 5 posts
            content_tag = post.select_one(".feed-shared-text, .feed-shared-update-v2__description")
            if content_tag:
                page_data['posts'].append({
                    "content": content_tag.text.strip()
                })

        # Employees
        employees_section = soup.select("li.org-people-profiles-module__profile-item, .org-people-profile-card")
        for emp in employees_section[:10]:  # Get first 10 employees
            name_tag = emp.select_one(".org-people-profile-card__profile-title, .artdeco-entity-lockup__title")
            profile_link = emp.select_one("a.app-aware-link")
            profile_img = emp.select_one("img.artdeco-entity-image")
            
            if name_tag:
                employee_data = {
                    "name": name_tag.text.strip(),
                    "profile_url": clean_linkedin_url(profile_link['href']) if profile_link and profile_link.get('href') else None,
                    "profile_picture": clean_linkedin_url(profile_img['src']) if profile_img and profile_img.get('src') else None
                }
                page_data['employees'].append(employee_data)

        return page_data

    except requests.exceptions.RequestException as e:
        print(f"Request Exception for page {page_id}: {e}")
        return None
    except Exception as e:
        print(f"Parsing Exception for page {page_id}: {e}")
        return None


if __name__ == '__main__':
    page_id_to_scrape = "deepsolv" # Example page ID
    scraped_data = scrape_linkedin_page(page_id_to_scrape)
    print(f"Scraping URL: https://www.linkedin.com/company/{page_id_to_scrape}/")

    if scraped_data:
        print("\nScraped data:")
        for key, value in scraped_data.items():
            if key != 'posts' and key != 'employees':
                print(f"{key}: {value}")
        print("\nPosts (first 3):")
        for post in scraped_data.get('posts', [])[:3]:
            print(f"- {post.get('content', 'No Content')[:100]}...")
        print("\nEmployees (first 3):")
        for emp in scraped_data.get('employees', [])[:3]:
            print(f"- {emp.get('name', 'No Name')} - {emp.get('profile_url', 'No URL')}")
    else:
        print("\nScraping failed. Check error messages above.")

