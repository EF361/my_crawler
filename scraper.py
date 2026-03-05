import time
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
    
    # --- STEALTH MODE START ---
    # 1. Dress up as a normal Windows 10 Chrome user
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 2. Hide the automation flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 3. Give the browser a normal monitor size (headless defaults to a tiny weird square)
    options.add_argument("--window-size=1920,1080")
    # --- STEALTH MODE END ---
    
    # Keep your custom Streamlit Linux paths
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # 4. The Magic Trick: Erase the "I am a bot" variable hidden inside Chrome's brain
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scrape_multiple_pages(start_url, max_pages=5, ignore_words=None):
    if ignore_words is None:
        ignore_words = []
        
    data = []
    error_message = None
    visited_urls = set()
    urls_to_visit = [start_url]
    base_domain = urlparse(start_url).netloc
    
    try:
        # Initialize the fixed driver
        driver = get_driver()
        
        while urls_to_visit and len(visited_urls) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            driver.get(current_url)
            
            # Allow JavaScript-heavy SME sites to load
            time.sleep(3) 
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Scrape FAQ style data
            for q in soup.find_all(['h3', 'h4', 'strong']):
                answer = q.find_next('p')
                if answer and len(answer.text.strip()) > 5:
                    data.append({
                        "id": len(data) + 1,
                        "data_type": "FAQ",
                        "title": q.text.strip(),
                        "details": answer.text.strip(),
                        "source_url": current_url
                    })
                    
            # 2. Scrape Table style data
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows[1:]: 
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        data.append({
                            "id": len(data) + 1,
                            "data_type": "Table",
                            "title": cols[0].text.strip(),
                            "details": f"Author: {cols[1].text.strip()} | Hits: {cols[2].text.strip()}",
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
            error_message = "No data found on the visited pages."
            
    except Exception as e:
        error_message = f"Error: {str(e)}"
        
    return data, error_message