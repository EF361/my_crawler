import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Thread-local storage so each "worker" gets its own browser
thread_local = threading.local()
active_drivers = [] # Keep track of browsers so we can close them later

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--window-size=1920,1080")
    
    # Block images to save bandwidth
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheet": 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_thread_driver():
    """Assigns a specific Chrome browser to the current working thread."""
    if not hasattr(thread_local, "driver"):
        driver = get_driver()
        thread_local.driver = driver
        active_drivers.append(driver)
    return thread_local.driver

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def process_single_page(url, base_domain, ignore_words, junk_phrases):
    """This is the job that each parallel worker will perform."""
    driver = get_thread_driver()
    page_data = []
    new_urls = []
    
    try:
        driver.get(url)
        try:
            # Smart Wait
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass 
            
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        seen_answers = set()
        
        # 1. Scrape FAQ
        for q in soup.find_all(['h2', 'h3', 'h4', 'strong']):
            title_text = clean_text(q.text)
            if not title_text or len(title_text) < 5 or title_text.lower() in junk_phrases:
                continue
                
            answer = q.find_next('p')
            if answer:
                ans_text = clean_text(answer.text)
                if len(ans_text) > 30 and ans_text.lower() not in junk_phrases and "@ 20" not in ans_text:
                    if ans_text not in seen_answers:
                        seen_answers.add(ans_text) 
                        page_data.append({
                            "data_type": "FAQ",
                            "title": title_text,
                            "details": ans_text,
                            "source_url": url
                        })
                        
        # 2. Scrape Tables
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows[1:]: 
                cols = row.find_all('td')
                if len(cols) >= 3:
                    title_col = clean_text(cols[0].text)
                    if title_col and len(title_col) > 2:
                        page_data.append({
                            "data_type": "Table",
                            "title": title_col,
                            "details": f"Info: {clean_text(cols[1].text)} | Meta: {clean_text(cols[2].text)}",
                            "source_url": url
                        })
                        
        # 3. Find Links
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href']).split('#')[0] 
            should_ignore = any(word.lower() in full_url.lower() for word in ignore_words)
            if not should_ignore and urlparse(full_url).netloc == base_domain:
                new_urls.append(full_url)
                
    except Exception as e:
        print(f"Failed on {url}: {e}")
        
    return page_data, new_urls

def scrape_multiple_pages(start_url, max_pages=5, ignore_words=None):
    if ignore_words is None:
        ignore_words = []
        
    data = []
    error_message = None
    visited_urls = set()
    urls_to_visit = [start_url]
    base_domain = urlparse(start_url).netloc
    
    junk_phrases = ["student resources", "highlight", "others", "contact", "follow us", "read more", "academic handbooks"]
    
    # Only 2 workers to prevent Streamlit memory crash
    max_workers = 2 
    
    try:
        # Start the Parallel Engine
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while urls_to_visit and len(visited_urls) < max_pages:
                
                # Grab a batch of URLs based on how many workers we have
                batch_size = min(max_workers, max_pages - len(visited_urls), len(urls_to_visit))
                current_batch = []
                
                for _ in range(batch_size):
                    url = urls_to_visit.pop(0)
                    if url not in visited_urls:
                        current_batch.append(url)
                        visited_urls.add(url)
                
                if not current_batch:
                    continue
                    
                # Assign URLs to the workers
                futures = {executor.submit(process_single_page, url, base_domain, ignore_words, junk_phrases): url for url in current_batch}
                
                # Collect results as they finish
                for future in as_completed(futures):
                    page_data, new_urls = future.result()
                    
                    for item in page_data:
                        item['id'] = len(data) + 1
                        data.append(item)
                        
                    for new_url in new_urls:
                        if new_url not in visited_urls and new_url not in urls_to_visit:
                            urls_to_visit.append(new_url)
                            
    except Exception as e:
        error_message = f"Error during crawl: {str(e)}"
        
    finally:
        # Crucial for industrial grade: Kill all invisible browsers to free up server RAM
        for d in active_drivers:
            try:
                d.quit()
            except:
                pass
        active_drivers.clear()
        
    if not data and not error_message:
        error_message = "No useful text found on the visited pages."
        
    return data, error_message