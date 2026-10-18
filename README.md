# My Crawler

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-%E2%AD%90-EA4C89)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12.2-green)
![Pandas](https://img.shields.io/badge/Pandas-1.5.0-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Demo](https://img.shields.io/badge/LiveDemo-StreamlitApp-ff69b4)

## 🚀 Executive Summary

**My Crawler** is a robust web scraping solution designed to handle both static and dynamic content efficiently. Leveraging Python, Streamlit, and industry-standard libraries like BeautifulSoup and Selenium, My Crawler empowers users to automate data extraction tasks seamlessly, ensuring fast and reliable results for modern web environments.

## ✨ Key Features

- **Static Content Extraction**: Retrieve data from HTML-based web pages efficiently using BeautifulSoup.
- **Dynamic Content Support**: Scrape AJAX-loaded or JavaScript-driven pages with Selenium integration.
- **Streamlit UI for Accessibility**: Intuitive interface for both non-technical and technical users to manage scraping workflows.
- **Flexible Output Formats**: Export scraped data easily to CSV or Excel using Pandas.
- **Customizable Rules**: Specify target elements using CSS selectors, XPath, or tags for precision scraping.
- **Error Handling**: Resilient fault tolerance for dealing with timeouts or page load failures.
- **Scalable Implementation**: Modular design for easy integration into evolving projects or advanced workflows.

## 🛠️ Architecture & Workflow

The architecture of **My Crawler** harmonizes simplicity and power. See the simplified flow below:

```mermaid
graph TD;
    User[User Input]
    User -->|Input webpage URL(s), options| StreamlitUI[Streamlit UI]
    StreamlitUI -->|Validate & Configure| Controller[Controller Service]
    Controller -->|Static Pages| BeautifulSoup[BeautifulSoup Extractor]
    Controller -->|Dynamic Pages| Selenium[Selenium Driver]
    BeautifulSoup --> Pandas[Data Formatting with Pandas]
    Selenium --> Pandas
    Pandas --> Output[Export to CSV/Excel]
    Output --> User[Download Results]
```

## 🧰 Tech Stack & Tools Breakdown

- **Programming Language**: Python 3.9+
- **Frontend**: Streamlit for intuitive UI/UX
- **Web Scraping**: BeautifulSoup for static content scraping, Selenium for dynamic content handling
- **Data Handling**: Pandas for transformation and export
- **Testing**: Selenium WebDriver for dynamic content validation
- **File Export**: CSV and Excel support for flexible data management

## 🚀 Quickstart / Installation

Follow these simple steps to get **My Crawler** running locally:

1. Clone this repository:
   ```bash
   git clone https://github.com/EF361/my_crawler.git
   cd my_crawler
   ```

2. Set up a Python virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

5. Visit the application in your browser at `http://localhost:8501` and start scraping!

---

**Maintainer**: [Alicia Goh (EF361)](https://github.com/EF361)  
This project proudly demonstrates cutting-edge web scraping, helping data-driven professionals extract insights effortlessly. Contributions are welcome—feel free to open an issue or submit a pull request!