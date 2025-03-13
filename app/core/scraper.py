# app/core/scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_linkedin_page(page_id: str):
    url = f"https://www.linkedin.com/company/{page_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    page_data = {}  # Initialize page_data HERE, BEFORE the try block

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Basic Details
        name_tag = soup.find("h1", class_="top-card-layout__title")
        page_data['name'] = name_tag.text.strip() if name_tag else None
        print(f"Name: {page_data['name']}")
        page_data['url'] = url
        page_data['linkedin_id'] = page_id # Use page_id as linkedin_id
        profile_picture_tag = soup.find("img", class_="inline-block relative w-16 h-16 top-card-layout__entity-image")
        page_data['profile_picture'] = profile_picture_tag['data-delayed-url'] if profile_picture_tag and 'data-delayed-url' in profile_picture_tag.attrs else None

        headline_tag = soup.find("h2", class_="top-card-layout__headline")
        second_subline_tag = soup.find("h4", class_="top-card-layout__second-subline")
        about_us_description_tag = soup.find("p", attrs={"data-test-id": "about-us__description"})

        description_parts = []
        if headline_tag:
            description_parts.append(headline_tag.text.strip())
        if second_subline_tag:
            description_parts.append(second_subline_tag.text.strip())
        if about_us_description_tag:
            description_parts.append(about_us_description_tag.text.strip())

        page_data['description'] = " ".join(description_parts).strip() if description_parts else None


        website_tag = soup.find("a", attrs={"aria-describedby": "websiteLinkDescription"})
        page_data['website'] = website_tag['href'] if website_tag and 'href' in website_tag.attrs else None

        industry_tag = soup.find("dd", attrs={"data-test-id": "about-us__industry"})
        page_data['industry'] = industry_tag.text.strip() if industry_tag else None

        followers_tag = soup.find("h3", class_="top-card-layout__first-subline")
        page_data['followers_count'] = None
        if followers_tag:
            followers_text = followers_tag.text.strip()
            if "followers" in followers_text:
                try:
                    page_data['followers_count'] = int(followers_text.split(" followers")[0].strip().replace(",", ""))
                except ValueError:
                    page_data['followers_count'] = None


        headcount_tag = soup.find("dd", attrs={"data-test-id": "about-us__size"})
        page_data['head_count'] = headcount_tag.text.strip() if headcount_tag else None
        page_data['specialities'] = None # Specialities section not found, setting to None

        # Posts - Basic extraction
        posts_data = []
        article_tags = soup.find_all("article", class_="main-feed-activity-card")
        for article_tag in article_tags[:3]: # Get only first 3 posts
            content_tag = article_tag.find("p", class_="attributed-text-segment-list__content")
            post_content = content_tag.text.strip() if content_tag else "No content found"
            posts_data.append({"content": post_content})
        page_data['posts'] = posts_data

        # People working there - Basic extraction
        employees_data = []
        employees_section = soup.find("section", attrs={"data-test-id": "employees-at"})
        if employees_section:
            employee_list_items = employees_section.find_all("li")
            for emp_li in employee_list_items[:3]: # Get only first 3 employees
                employee_card = emp_li.find("a", class_="base-card")
                if employee_card:
                    employee_name_tag = employee_card.find("h3", class_="base-main-card__title")
                    employee_name = employee_name_tag.text.strip() if employee_name_tag else "Name not found"
                    employee_title_tag = employee_card.find("h4", class_="base-main-card__subtitle")
                    employee_title = employee_title_tag.text.strip() if employee_title_tag else "Title not found"
                    employee_profile_url_tag = employee_card.get('href')
                    employee_profile_url =  "https://www.linkedin.com" + employee_profile_url_tag if employee_profile_url_tag else None

                    employee_profile_picture_tag = employee_card.find("img", class_="inline-block relative rounded-\[50%\] w-6 h-6")
                    employee_profile_picture = employee_profile_picture_tag['data-delayed-url'] if employee_profile_picture_tag and 'data-delayed-url' in employee_profile_picture_tag.attrs else None


                    employees_data.append({
                        "name": employee_name,
                        "title": employee_title,
                        "profile_url": employee_profile_url,
                        "profile_picture": employee_profile_picture
                    })
        page_data['employees'] = employees_data


        return page_data

    except requests.exceptions.RequestException as e:
        print(f"Request Exception for page {page_id}: {e}")
        return None
    except Exception as e:
        print(f"Parsing Exception for page {page_id}: {e}")
        print(f"Exception details: {e}")
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
            print(f"- {emp.get('name', 'No Name')} - {emp.get('title', 'No Title')}")
    else:
        print("\nScraping failed. Check error messages above.")