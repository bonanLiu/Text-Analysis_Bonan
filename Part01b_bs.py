import time
import pandas as pd
import requests
from bs4 import BeautifulSoup




BASE_URL = "https://www.coffeereview.com/category/articles/"
PAGES_TO_SCRAPE = 6  # scraping pages 



def scrape_with_beautifulsoup():

    articles = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for page in range(1, PAGES_TO_SCRAPE + 1):
        # URL
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page}/"
        
        print(f"BeautifulSoup: Page {page}  - {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # catch error?
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            article_elements = soup.select('article.post')
            if not article_elements:
                article_elements = soup.select('article')
            
            print(f"Getting {len(article_elements)} articles.")
            
            article_links = []
            for article in article_elements:
                try:
                    # title + link
                    title_element = article.select_one('h2 a, h1 a, .entry-title a')
                    if not title_element:
                        continue
                        
                    title = title_element.text.strip()
                    link = title_element['href']
                    
                    # store link
                    article_links.append({"title": title, "url": link, "page": page})
                    print(f"The article: {title}")
                except Exception as e:
                    failure_count += 1
                    print(f"❌ Article Scraping Fail : {e}")
                    continue
            
            # connect to the articles
            for article_info in article_links:
                try:
                    print(f"Reading: {article_info['title']}")
                    
                    article_response = requests.get(article_info['url'], headers=headers, timeout=10)
                    article_response.raise_for_status()
                    
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # title
                    title_element = article_soup.select_one('h1.entry-title')
                    title = title_element.text.strip() if title_element else article_info['title']
                    
                    # date
                    date_element = article_soup.select_one('.entry-meta .entry-date, .post-date')
                    date = date_element.text.strip() if date_element else "No date available"
                    
                    # dategory
                    category_elements = article_soup.select('.entry-meta .entry-categories a, .cat-links a')
                    categories = ", ".join([cat.text.strip() for cat in category_elements]) if category_elements else "No category available"
                    
                    # content
                    content = ""
                    # different container
                    content_selectors = [
                        '.entry-content',
                        '.post-content',
                        'article .content',
                        '.post .entry'
                    ]
                    
                    for selector in content_selectors:
                        content_element = article_soup.select_one(selector)
                        if content_element:
                            # combine paragraphs
                            paragraphs = content_element.select('p')
                            if paragraphs:
                                content = "\n".join([p.text.strip() for p in paragraphs])
                                break
                            else:
                                content = content_element.text.strip()
                                break
                    
                    if not content:
                        content = "Getting Article Error"
                    
                    # list
                    articles.append({
                        "title": title,
                        "url": article_info['url'],
                        "date": date,
                        "categories": categories,
                        "content": content,
                        "source_page": article_info['page'],
                        "method": "BeautifulSoup"
                    })
                    
                    print(f"✅ : {title}")
                except Exception as e:
                    print(f"❌ : {e}")
                    continue
                
                # pending
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Fail in Page {page} : {e}")
            continue
        
        time.sleep(3)

    return articles


# Processing
print("\nBeautifulSoup Scraping......")
bs_articles= scrape_with_beautifulsoup()
bs_df = pd.DataFrame(bs_articles)
bs_df.to_csv("Articles_Coffee.csv", index=False, encoding='utf-8')
    

    
print("\nFinishing Processing")
