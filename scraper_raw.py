import time
import re
import threading
import shutil
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
active_drivers = [] 

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
    
    # --- THE GPS FIX START ---
    # Dynamically find the exact paths on the server
    chrome_path = shutil.which("chromium") or shutil.which("google-chrome")
    driver_path = shutil.which("chromedriver") or shutil.which("chromium-driver")
    
    if chrome_path:
        options.binary_location = chrome_path
        
    if driver_path:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # Ultimate fallback: let Selenium try to figure it out
        driver = webdriver.Chrome(options=options)
    # --- THE GPS FIX END ---
        
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

def process_single_page(url, base_domain, ignore_words):
    """Raw worker: Extracts the entire page text as one large document."""
    driver = get_thread_driver()
    page_data = []
    new_urls = []
    
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass 
            
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 1. Grab the official Page Title
        title_tag = soup.find('title')
        page_title = title_tag.text.strip() if title_tag else "No Title"
        
        # 2. Grab EVERYTHING inside the body tag
        body_tag = soup.find('body')
        if body_tag:
            # get_text(separator='\n') mimics how a human sees the text on screen with line breaks
            full_page_text = body_tag.get_text(separator='\n', strip=True)
        else:
            full_page_text = ""
            
        # 3. Save it exactly like the "Other Crawler" format
        if full_page_text:
            page_data.append({
                "title": page_title,
                "url": url,
                "html": full_page_text
            })
                    
        # 4. Find Links to continue crawling
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
    
    max_workers = 2 
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while urls_to_visit and len(visited_urls) < max_pages:
                
                batch_size = min(max_workers, max_pages - len(visited_urls), len(urls_to_visit))
                current_batch = []
                
                for _ in range(batch_size):
                    url = urls_to_visit.pop(0)
                    if url not in visited_urls:
                        current_batch.append(url)
                        visited_urls.add(url)
                
                if not current_batch:
                    continue
                    
                futures = {executor.submit(process_single_page, url, base_domain, ignore_words): url for url in current_batch}
                
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
        for d in active_drivers:
            try:
                d.quit()
            except:
                pass
        active_drivers.clear()
        
    if not data and not error_message:
        error_message = "No text found on the visited pages."
        
    return data, error_message