# 🕷️ Deep Web Crawler

**An industrial-grade, stealth-enabled web crawler designed for AI Employee pipelines and SME data extraction.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://icrawler.streamlit.app)

## 🚀 Overview

The Deep Web Crawler is a high-performance data extraction dashboard built to feed clean, structured information into Retrieval-Augmented Generation (RAG) systems. Built with **Streamlit**, **Selenium**, and **BeautifulSoup**, it intelligently navigates websites, bypasses security checks (like Cloudflare), and extracts relevant FAQ and table data.

It features a professional UI, multithreaded parallel processing for maximum speed, and **dual extraction engines** to handle different levels of website complexity.

## ✨ Key Features

* **🕵️‍♂️ Stealth Mode:** Utilizes custom user agents and headless browser spoofing to bypass common website firewalls and Cloudflare "waiting rooms."
* **⚡ Parallel Processing:** Employs multithreading to open multiple headless browsers simultaneously, drastically reducing crawl times.
* **🧠 Dual Extraction Engines:** * `scraper.py` (Smart): Automatically detects and removes boilerplate text (like "Contact Us" or "Menu" footers) to ensure AI agents ingest only high-quality data.
  * `scraper_raw.py` (Raw): Pulls the complete text and HTML structure for broader data extraction needs.
* **💾 Dual Export Options:** Download scraped data instantly as perfectly formatted JSON (for vector databases) or CSV (for spreadsheet viewing).
* **🎨 Pro UI:** A clean, side-by-side dashboard with live status monitoring and interactive data preview tabs.

## 🛠️ Tech Stack

* **Python 3.10+**
* **Frontend:** [Streamlit](https://streamlit.io/) (Reactive dashboard & data preview)
* **Parsing Engine:** [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/) (HTML parsing and DOM traversal)
* **Browser Automation:** [Selenium](https://www.selenium.dev/) & webdriver-manager (Headless Chromium control)
* **Data Engine:** [Pandas](https://pandas.pydata.org/) (Dataframe manipulation & CSV conversion)

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/EF361/my_crawler.git](https://github.com/EF361/my_crawler.git)
    cd my_crawler
    ```

2.  **Create a virtual environment (Recommended)**:
    ```bash
    python -m venv env_name
    # Windows
    env_name\Scripts\activate
    # Mac/Linux
    source env_name/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ How to Run

### Option 1: Try the Live Demo
You can access the deployed version immediately without installation:
👉 **[Click here to open Deep Web Crawler](https://icrawler.streamlit.app)**

### Option 2: Run Locally
1.  **Launch the application**:
    ```bash
    streamlit run app.py
    ```

2.  **Access the Dashboard**:
    Open your browser and navigate to `http://localhost:8501`.

## 📖 Usage Guide

1.  **Configure Target:** Enter the starting URL of the website you want to scrape in the main input field.
2.  **Set Depth:** Adjust the "Max Pages to Crawl" counter to determine how deep the robot should explore the website's internal links.
3.  **Advanced Filtering (Optional):** Open the "🛠️ Advanced Options" dropdown to add specific words to the ignore list (e.g., `login, admin`) or to customize your output file name.
4.  **Execute:** Click **"🚀 Start Crawling"**. The live status monitor will update you as the parallel workers process the pages.
5.  **Review & Export:** Once complete, preview the clean data in the interactive table or raw JSON tabs, then download your preferred format.

## 📂 Project Structure

```text
my_crawler/
├── app.py                  # Main Streamlit dashboard interface
├── scraper.py              # Smart scraping logic with advanced text filtering
├── scraper_raw.py          # Raw scraping logic with Cloudflare bypasses
├── requirements.txt        # Python dependency list
├── packages.txt            # System-level dependencies (for Linux/Cloud hosting)
└── README.md               # Documentation