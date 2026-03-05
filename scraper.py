import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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
    
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def clean_text(text):
    # Removes weird spaces and invisible code
    return re.sub(r'\s+', ' ', text).strip()

def scrape_multiple_pages(start_url, max_pages=5, ignore_words=None):
    if ignore_words is None:
        ignore_words = []
        
    data = []
    error_message = None
    visited_urls = set()
    urls_to_visit = [start_url]
    base_domain = urlparse(start_url).netloc
    
    # Common junk words found in website menus and footers
    junk_phrases = ["student resources", "highlight", "others", "contact", "follow us", "read more", "academic handbooks"]
    
    try:
        driver = get_driver()
        
        while urls_to_visit and len(visited_urls) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            driver.get(current_url)
            time.sleep(3) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 1. Scrape FAQ style data - SMART FILTERING
            for q in soup.find_all(['h2', 'h3', 'h4', 'strong']):
                title_text = clean_text(q.text)
                
                # Skip empty titles or titles that are known menus/footers
                if not title_text or len(title_text) < 5 or title_text.lower() in junk_phrases:
                    continue
                    
                answer = q.find_next('p')
                if answer:
                    ans_text = clean_text(answer.text)
                    
                    # A good FAQ answer should be an actual sentence (more than 30 characters)
                    # We also skip it if it just repeats a menu word
                    if len(ans_text) > 30 and ans_text.lower() not in junk_phrases and "@ 20" not in ans_text:
                        
                        # Prevent duplicate entries
                        if not any(d['title'] == title_text and d['details'] == ans_text for d in data):
                            data.append({
                                "id": len(data) + 1,
                                "data_type": "FAQ",
                                "title": title_text,
                                "details": ans_text,
                                "source_url": current_url
                            })
                    
            # 2. Scrape Table style data
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows[1:]: 
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        title_col = clean_text(cols[0].text)
                        # Only grab valid table rows
                        if title_col and len(title_col) > 2:
                            data.append({
                                "id": len(data) + 1,
                                "data_type": "Table",
                                "title": title_col,
                                "details": f"Info: {clean_text(cols[1].text)} | Meta: {clean_text(cols[2].text)}",
                                "source_url": current_url
                            })
            
            # 3. Queue new internal links
            for link in soup.find_all('a', href=True):
                full_url = urljoin(current_url, link['href']).split('#')[0] 
                should_ignore = any(word.lower() in full_url.lower() for word in ignore_words)
                
                if not should_ignore and urlparse(full_url).netloc == base_domain and full_url not in visited_urls and full_url not in urls_to_visit:
                    urls_to_visit.append(full_url)
                    
        driver.quit() 
        
        if not data:
            error_message = "No useful text found on the visited pages."
            
    except Exception as e:
        error_message = f"Error: {str(e)}"
        
    return data, error_message