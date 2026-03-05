import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_faq(url):
    data = []
    error_message = None
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(5) 
        html = driver.page_source
        driver.quit() 
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for standard FAQ headings
        questions = soup.find_all(['h3', 'h4', 'strong'])
        
        for i, q in enumerate(questions, 1):
            answer = q.find_next('p')
            if answer:
                data.append({
                    "id": i,
                    "question": q.text.strip(),
                    "category": "general",
                    "answer": answer.text.strip(),
                    "source_url": url
                })
                
        if not data:
            error_message = "No data found. The website might use different HTML tags."
            
    except Exception as e:
        error_message = f"Error: {str(e)}"
        
    return data, error_message