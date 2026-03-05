import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_multiple_pages(start_url, max_pages=5, ignore_words=None):
    if ignore_words is None:
        ignore_words = []
        
    data = []
    error_message = None
    
    visited_urls = set()
    urls_to_visit = [start_url]
    
    base_domain = urlparse(start_url).netloc
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        while urls_to_visit and len(visited_urls) < max_pages:
            
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            
            driver.get(current_url)
            time.sleep(3) 
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Scrape FAQ style data (Headings and Paragraphs)
            questions = soup.find_all(['h3', 'h4', 'strong'])
            for q in questions:
                answer = q.find_next('p')
                if answer:
                    data.append({
                        "id": len(data) + 1,
                        "data_type": "FAQ",
                        "title": q.text.strip(),
                        "details": answer.text.strip(),
                        "source_url": current_url
                    })
                    
            # 2. Scrape Table style data (Like the FTKE Postgraduate page)
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if not rows:
                    continue
                
                # Skip the very first row because it is just the header (Title, Author, Hits)
                for row in rows[1:]: 
                    cols = row.find_all('td')
                    
                    # If the table has at least 3 columns, grab the data
                    if len(cols) >= 3:
                        data.append({
                            "id": len(data) + 1,
                            "data_type": "Table",
                            "title": cols[0].text.strip(),
                            "details": f"Author: {cols[1].text.strip()} | Hits: {cols[2].text.strip()}",
                            "source_url": current_url
                        })
            
            # Find new links to visit
            for link in soup.find_all('a', href=True):
                full_url = urljoin(current_url, link['href']).split('#')[0] 
                
                should_ignore = False
                for word in ignore_words:
                    if word.lower() in full_url.lower():
                        should_ignore = True
                        break
                
                if not should_ignore and urlparse(full_url).netloc == base_domain and full_url not in visited_urls and full_url not in urls_to_visit:
                    urls_to_visit.append(full_url)
                    
        driver.quit() 
        
        if not data:
            error_message = "No data found on the visited pages."
            
    except Exception as e:
        error_message = f"Error: {str(e)}"
        
    return data, error_message

def get_driver():
    options = Options()
    options.add_argument("--headless") # Run without a UI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Use the system-installed chromium-driver from packages.txt
    service = Service("/usr/bin/chromedriver")
    
    return webdriver.Chrome(service=service, options=options)