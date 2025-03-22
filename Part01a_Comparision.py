import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

import psutil

folder_path = 'Part01_Result'

# CPU testing
def resource_monitor():
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),  # CPU 
        "memory_usage": psutil.virtual_memory().percent  # RAM
    }

# time testing
def benchmark_function(func, *args, **kwargs):
    start_time = time.time() # time
    resource_before = resource_monitor()  #  CPU , RAM
    result, success_rate = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    resource_after = resource_monitor()
    return result, execution_time , resource_before, resource_after, success_rate


BASE_URL = "https://www.coffeereview.com/category/articles/"
PAGES_TO_SCRAPE = 2  # scraping pages for test


##### Approch 01: Selenium

def scrape_with_selenium():

    articles = []
    failure_count=0
    
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # start Selenium
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        for page in range(1, PAGES_TO_SCRAPE + 1):
            # URL set, page 1 differ with other pages
            if page == 1:
                url = BASE_URL
            else:
                url = f"{BASE_URL}page/{page}/"
            
            print(f"Selenium: Page {page}  - {url}")
            driver.get(url)
            time.sleep(5)  # page loading
            
            # if loading sucessfully
            print(f"Current URL: {driver.current_url}")
            
            # scraping the articles
            article_elements = driver.find_elements(By.CSS_SELECTOR, "article.post")
            if not article_elements:
                article_elements = driver.find_elements(By.CSS_SELECTOR, "article")
            
            print(f"Getting {len(article_elements)} articles.")
            
            # storage
            article_links = []
            for article in article_elements:
                try:
                    # title + link
                    title_element = article.find_element(By.CSS_SELECTOR, "h2 a, h1 a, .entry-title a")
                    title = title_element.text.strip()
                    link = title_element.get_attribute("href")
                    
                    # store link for scraping article
                    article_links.append({"title": title, "url": link, "page": page})
                    print(f"The article : {title}")
                except Exception as e:
                    failure_count +=1
                    print(f"❌ Article Scraping Fail : {e}")
                    continue
            
            # connect to the articles
            for article_info in article_links:
                try:
                    print(f"Reading : {article_info['title']}")
                    driver.get(article_info['url'])
                    time.sleep(3)  
                    
                    # get title
                    try:
                        title = driver.find_element(By.CSS_SELECTOR, "h1.entry-title").text.strip()
                    except:
                        title = article_info['title']
                    
                    # get date
                    try:
                        date = driver.find_element(By.CSS_SELECTOR, ".entry-meta .entry-date, .post-date").text.strip()
                    except:
                        date = "No date available"
                    
                    # get catagory
                    try:
                        category_elements = driver.find_elements(By.CSS_SELECTOR, ".entry-meta .entry-categories a, .cat-links a")
                        categories = ", ".join([cat.text.strip() for cat in category_elements])
                    except:
                        categories = "No category available"
                    
                    # get content
                    try:
                        # content container
                        content_selectors = [
                            ".entry-content",
                            ".post-content",
                            "article .content",
                            ".post .entry"
                        ]
                        
                        content = ""
                        for selector in content_selectors:
                            try:
                                content_element = driver.find_element(By.CSS_SELECTOR, selector)
                                content = content_element.text.strip()
                                if content:
                                    break
                            except:
                                continue
                        
                        if not content:
                            content = "Getting Article Error"
                    except Exception as e:
                        print(f"Error: {e}")
                        content = "Error"
                    
                    # add to list
                    articles.append({
                        "title": title,
                        "url": article_info['url'],
                        "date": date,
                        "categories": categories,
                        "content": content,
                        "source_page": article_info['page'],
                        "method": "Selenium"
                    })
                    
                    print(f"✅ : {title}")
                except Exception as e:
                    failure_count +=1
                    print(f"❌ : {e}")
                    continue
                
                # pending
                time.sleep(2)
    finally:
        driver.quit()
    
    denominator = len(articles) + failure_count
    success_rate = 100 * len(articles) / denominator if denominator > 0 else 0
    
    return articles,success_rate


##### Approch 02: Requests + BeautifulSoup

def scrape_with_beautifulsoup():

    articles = []
    failure_count = 0
    
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
                    failure_count += 1
                    print(f"❌ : {e}")
                    continue
                
                # pending
                time.sleep(2)
                
        except Exception as e:
            failure_count += 1
            print(f"❌ Fail in Page {page} : {e}")
            continue
        
        time.sleep(3)
    denominator = len(articles) + failure_count
    success_rate = 100 * len(articles) / denominator if denominator > 0 else 0
    return articles,success_rate

# Testing Result
if __name__ == "__main__":
    print("-" * 50)
    print("Comparison Result Report")
    print("-" * 50)
    
    # Selenium
    print("\nSelenium Scraping......")
    selenium_articles, selenium_time, selenium_res_before, selenium_res_after, selenium_success_rate = benchmark_function(scrape_with_selenium)
    selenium_df = pd.DataFrame(selenium_articles)
    selenium_df.to_csv(f"{folder_path}/Article(se).csv", index=False, encoding='utf-8')
    
    # BeautifulSoup
    print("\nBeautifulSoup Scraping......")
    bs_articles, bs_time, bs_res_before, bs_res_after, bs_success_rate = benchmark_function(scrape_with_beautifulsoup)
    bs_df = pd.DataFrame(bs_articles)
    bs_df.to_csv(f"{folder_path}/Article(bs).csv", index=False, encoding='utf-8')
    
    # Create a DataFrame for the report instead of writing to a text file
    reportArray = {
        " ": ["Articles", "Timing(s)", "Performance(s/article)", 
              "Success Rate(%)", "CPU Usage(%)", "RAM Usage(%)"],
        "Selenium": [len(selenium_articles), f"{selenium_time:.2f}", f"{selenium_time/len(selenium_articles):.2f}",
                     f"{selenium_success_rate:.2f}", f"{selenium_res_after['cpu_usage']:.2f}",f"{selenium_res_after['memory_usage']:.2f}"],
        "BeautifulSoup": [len(bs_articles), f"{bs_time:.2f}", f"{bs_time/len(bs_articles):.2f}",
                          f"{bs_success_rate:.2f}", f"{bs_res_after['cpu_usage']:.2f}",f"{bs_res_after['memory_usage']:.2f}"]
    }
    
    df_reportArray = pd.DataFrame(reportArray)
    df_reportArray.to_csv("Part01_Benchmark Report.csv", index=False)
    
    # Print the report to console
    print("\n" + "=" * 50)
    print("Comparison Result Report:")
    print(df_reportArray)
    print("=" * 50)
    
    print("\nFinishing Processing")
