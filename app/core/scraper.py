import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse

def scrape_linkedin_page(page_id: str):
    base_url = "https://www.linkedin.com/company/"
    url = f"{base_url}{page_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    page_data = {}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        canonical_link = soup.find('link', rel='canonical')
        if canonical_link:
            page_data['url'] = canonical_link.get('href')
        else:
            page_data['url'] = url

        page_data['linkedin_id'] = page_id


        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                json_data = json.loads(json_ld.string)
                #print(f"JSON-LD Data: {json.dumps(json_data, indent=2)}")

                if isinstance(json_data, dict):  # Check if it's a dictionary
                    if json_data.get('@type') == 'Organization':
                        page_data['name'] = json_data.get('name')
                        page_data['description'] = json_data.get('description')
                        page_data['website'] = json_data.get('sameAs')

                        if 'logo' in json_data and isinstance(json_data['logo'], dict) and 'contentUrl' in json_data['logo']:
                            page_data['profile_picture'] = json_data['logo']['contentUrl']

                        if 'numberOfEmployees' in json_data and isinstance(json_data['numberOfEmployees'], dict) and 'value' in json_data['numberOfEmployees']:
                            page_data['head_count'] = str(json_data['numberOfEmployees']['value'])

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON-LD: {e}")
                print(f"JSON-LD String: {json_ld.string}")
            except Exception as e:
                print(f"Error processing JSON-LD: {e}")


        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            desc_content = meta_desc.get('content', '')
            #print(f"Meta description: {desc_content}")  # Keep this for debugging

            followers_match = re.search(r'(\d+,?\d*)\s+followers', desc_content)
            if followers_match:
                followers_text = followers_match.group(1).replace(',', '')
                try:
                    page_data['followers_count'] = int(followers_text)
                except ValueError:
                    page_data['followers_count'] = None

        if not page_data.get('name'):
            name_tag = soup.find("h1", class_="top-card-layout__title")
            if not name_tag:
                name_tag = soup.find("h1")
            page_data['name'] = name_tag.text.strip() if name_tag else None

        # Profile Picture (Fallback)
        if not page_data.get('profile_picture'):
            profile_picture_tag = soup.find("img", class_="top-card-layout__entity-image") # class name changed.
            if profile_picture_tag and 'data-delayed-url' in profile_picture_tag.attrs:
                page_data['profile_picture'] = profile_picture_tag['data-delayed-url']
            else: # added fallback
                profile_picture_tag = soup.find("img", class_="org-top-card-primary-content__logo")
                if profile_picture_tag and 'src' in profile_picture_tag.attrs:
                     page_data['profile_picture'] = profile_picture_tag['src']


        # Followers Count (Fallback - Multiple Locations)
        if not page_data.get('followers_count'):
            followers_tag = soup.find("h3", class_="top-card-layout__first-subline")
            if followers_tag:
                followers_text = followers_tag.text.strip()
                followers_match = re.search(r'(\d+,?\d*)\s+followers', followers_text)
                if followers_match:
                    try:
                        page_data['followers_count'] = int(followers_match.group(1).replace(',', ''))
                    except ValueError:
                        page_data['followers_count'] = None
            # Fallback to another common location if the first one fails
            if not page_data.get('followers_count'):
                followers_tag = soup.find("div", {"class": "org-top-card-summary-info-list__info-item"}) # another class name.
                if followers_tag:
                    followers_text = followers_tag.get_text(strip=True)
                    followers_match = re.search(r'(\d[\d,.]*)', followers_text)
                    if followers_match:
                        cleaned_followers = followers_match.group(1).replace(",", "").replace(".", "")
                        try:
                            page_data['followers_count'] = int(cleaned_followers)
                        except ValueError:
                            page_data['followers_count'] = None



        # Description (Fallback - Multiple Locations)
        if not page_data.get('description'):
            about_us_description_tag = soup.find("p", attrs={"data-test-id": "about-us__description"})
            if about_us_description_tag:
                page_data['description'] = about_us_description_tag.text.strip()
            else:
                headline_tag = soup.find("h4", class_="top-card-layout__second-subline")
                if headline_tag:
                     page_data['description'] = headline_tag.text.strip()
                else: # added fallback
                    description_tag = soup.find("div", {"class": "org-about-company-module__about-us-container"})
                    if description_tag:
                        page_data['description'] = description_tag.get_text(strip=True)


        if not page_data.get('website'):
            website_tag = soup.find("a", attrs={"aria-describedby": "websiteLinkDescription"}) # class for website
            if website_tag and 'href' in website_tag.attrs:
                redirect_url = website_tag['href']
                if "linkedin.com/redir/redirect" in redirect_url:
                    url_param = re.search(r'url=([^&]+)', redirect_url)
                    if url_param:
                        page_data['website'] = urllib.parse.unquote(url_param.group(1))
                else:
                    page_data['website'] = redirect_url

        # Industry (Fallback)
        if not page_data.get('industry'):
            industry_tag = soup.find("dd", attrs={"data-test-id": "about-us__industry"})
            page_data['industry'] = industry_tag.text.strip() if industry_tag else None

        # Company Size / Headcount (Fallback)
        if not page_data.get('head_count'):
            headcount_tag = soup.find("dd", attrs={"data-test-id": "about-us__size"})
            page_data['head_count'] = headcount_tag.text.strip() if headcount_tag else None
            if not page_data.get('head_count'): # fallback
                headcount_tag_2 = soup.find("a", {"data-tracking-control-name":"org-employees_cta_face-pile-cta"})
                if headcount_tag_2:
                        headcount_text = headcount_tag_2.get_text(strip=True)
                        match = re.search(r'Discover all (\d+(?:,\d+)*) employees', headcount_text)
                        if match:
                            count_str = match.group(1).replace(',', '')
                            try:
                                page_data['head_count'] = int(count_str)
                            except ValueError:
                                 page_data['head_count'] = None

        # Specialities (Fallback)
        if not page_data.get('specialities'):
             specialities_tag = soup.find("dd", attrs={"data-test-id": "about-us__specialties"})
             page_data['specialities'] = specialities_tag.text.strip() if specialities_tag else None
        
        posts_data = []
        article_tags = soup.find_all("article", class_="main-feed-activity-card")
        for article_tag in article_tags[:3]:
            content_tag = article_tag.find("p", class_="attributed-text-segment-list__content")
            if content_tag:
                post_content = content_tag.get_text(strip=True)
            else:
                post_content = "No content found"
            posts_data.append({"content": post_content})
        page_data['posts'] = posts_data

        employees_data = []
        employees_section = soup.find("section", attrs={"data-test-id": "employees-at"}) 
        if employees_section:
            employee_list_items = employees_section.find_all("li")
            for emp_li in employee_list_items[:3]:
                employee_card = emp_li.find("a", class_="base-card")
                if employee_card:
                    employee_name_tag = employee_card.find("h3", class_="base-main-card__title")
                    employee_name = employee_name_tag.text.strip() if employee_name_tag else "Name not found"

                    employee_title_tag = employee_card.find("h4", class_="base-main-card__subtitle")
                    employee_title = employee_title_tag.text.strip() if employee_title_tag else "Title not found"

                    employee_profile_url_tag = employee_card.get('href')
                    employee_profile_url =  "https://www.linkedin.com" + employee_profile_url_tag if employee_profile_url_tag  else None
                    
                    employee_profile_picture_tag = employee_card.find("img", class_="base-main-card__image")
                    employee_profile_picture = employee_profile_picture_tag['data-delayed-url'] if employee_profile_picture_tag and 'data-delayed-url' in employee_profile_picture_tag.attrs else None


                    employees_data.append({
                        "name": employee_name,
                        "title": employee_title,
                        "profile_url": employee_profile_url,
                        "profile_picture" : employee_profile_picture
                    })
        page_data['employees'] = employees_data


        return page_data

    except requests.exceptions.RequestException as e:
        print(f"Request Exception for page {page_id}: {e}")
        return None
    except Exception as e:
        print(f"Parsing Exception for page {page_id}: {e}")
        return None



if __name__ == '__main__':

    page_id_to_scrape = "deepsolv"
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