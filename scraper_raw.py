import time
import re
import shutil
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

thread_local = threading.local()
active_drivers = [] 

def get_driver():
    options = Options()
    
    # 1. Background processing and stability
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # 2. Stealth Mode (Look like a normal Windows user)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 3. Speed Upgrade (Block heavy images and styling)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheet": 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    # 4. Universal Setup (Using Built-in Selenium Manager)
    # No Service or ChromeDriverManager needed! Selenium handles it automatically.
    driver = webdriver.Chrome(options=options)
    
    # 5. Final Stealth Trick
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def get_thread_driver():
    if not hasattr(thread_local, "driver"):
        driver = get_driver()
        thread_local.driver = driver
        active_drivers.append(driver)
    return thread_local.driver

def process_single_page(url, base_domain, ignore_words):
    driver = get_thread_driver()
    page_data = []
    new_urls = []
    
    try:
        driver.get(url)
        
        # --- NEW: CLOUDFLARE WAITER ---
        # Wait up to 15 seconds in the "waiting room" for the security check to pass
        for _ in range(15):
            page_text = driver.page_source.lower()
            if "performing security verification" in page_text or "just a moment" in page_text:
                time.sleep(1) # Wait 1 second and check again
            else:
                break # Security passed, proceed to scrape!
        # ------------------------------
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        title_tag = soup.find('title')
        page_title = title_tag.text.strip() if title_tag else "No Title"
        
        body_tag = soup.find('body')
        if body_tag:
            full_page_text = body_tag.get_text(separator='\n', strip=True)
        else:
            full_page_text = ""
            
        if full_page_text:
            page_data.append({
                "title": page_title,
                "url": url,
                "html": full_page_text
            })
                    
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href']).split('#')[0] 
            should_ignore = any(word.lower() in full_url.lower() for word in ignore_words)
            if not should_ignore and urlparse(full_url).netloc == base_domain:
                new_urls.append(full_url)
                
    except Exception as e:
        print(f"Failed on {url}: {e}")
        
    return page_data, new_urls

def get_base_directory(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path
    if not path:
        path = '/'
    
    # If the path does not end with a slash, check if it's a file
    if not path.endswith('/'):
        # Check if the last segment contains a dot, meaning it's a file
        last_slash = path.rfind('/')
        if last_slash != -1:
            last_segment = path[last_slash + 1:]
            if '.' in last_segment:
                # It has a dot (e.g. index.html), so get directory prefix
                path = path[:last_slash + 1]
            else:
                # No dot, treat it as a folder name and append /
                path = path + '/'
        else:
            # Path is like 'folder', no slashes
            if '.' in path:
                path = '/'
            else:
                path = '/' + path + '/'
    return netloc, path.lower()

def is_in_scope(url, start_netloc, start_dir):
    parsed = urlparse(url)
    if parsed.netloc.lower() != start_netloc:
        return False
    path = parsed.path.lower()
    if not path:
        path = '/'
    
    # Normalize target path
    if not path.endswith('/'):
        last_slash = path.rfind('/')
        if last_slash != -1:
            last_segment = path[last_slash + 1:]
            if '.' not in last_segment:
                path = path + '/'
        else:
            if '.' not in path:
                path = '/' + path + '/'
                
    return path.startswith(start_dir)

def scrape_multiple_pages(start_url, max_pages=5, ignore_words=None):
    if ignore_words is None:
        ignore_words = []
        
    data = []
    error_message = None
    
    start_netloc, start_dir = get_base_directory(start_url)
    
    # Queue system tracks (url, current_depth)
    urls_to_visit = deque([(start_url, 0)])
    visited_urls = {start_url}
    
    max_workers = 2 
    pages_crawled_count = 0
    active_futures = {}
    
    try:
        from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while urls_to_visit or active_futures:
                # Submit tasks up to max_workers limit and max_pages limit
                while urls_to_visit and len(active_futures) < max_workers and pages_crawled_count < max_pages:
                    url, depth = urls_to_visit.popleft()
                    future = executor.submit(process_single_page, url, start_netloc, ignore_words)
                    active_futures[future] = (url, depth)
                    pages_crawled_count += 1
                
                if not active_futures:
                    break
                
                # Wait for at least one worker to finish
                done, _ = wait(active_futures.keys(), return_when=FIRST_COMPLETED)
                
                for future in done:
                    url, depth = active_futures.pop(future)
                    try:
                        page_data, new_urls = future.result()
                        
                        for item in page_data:
                            item['id'] = len(data) + 1
                            data.append(item)
                            
                        # If current depth is strictly less than 5, increment and push scoped URLs
                        if depth < 5:
                            for new_url in new_urls:
                                if new_url not in visited_urls:
                                    if is_in_scope(new_url, start_netloc, start_dir):
                                        visited_urls.add(new_url)
                                        urls_to_visit.append((new_url, depth + 1))
                                        
                    except Exception as e:
                        print(f"Failed to process {url}: {e}")
                        
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