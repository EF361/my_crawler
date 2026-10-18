# my_crawler

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-brightgreen)
![Selenium](https://img.shields.io/badge/Automation-Selenium-yellow)
![License](https://img.shields.io/badge/License-MIT-informational)
![Tests](https://img.shields.io/badge/pytest-Coverage-green)
![Status](https://img.shields.io/badge/Status-Security%20Audited-warning)

## 🕵️ Executive Summary
**my_crawler** is a secure and extensible web crawler designed for high-performance and compliance-conscious web scraping. It integrates safeguards against DNS rebinding, SSRF attacks, and formula injection, while providing robust export capabilities and browser automation in tightly controlled environments.

## ✨ Key Features
- **Advanced Resolver & Redirect Validation**:
  - Resolves and validates all redirect targets and IP addresses (IPv4, IPv6, and alternative representations) prior to connection.
  - Mitigates DNS rebinding, blocks internal/loopback destinations, and ensures robust request validation.
- **Selenium Sandbox Isolation**:
  - Executes browser jobs in secure, isolated containers with configurable limits for CPU, memory, page-count, wall-clock time, and downloads.
- **Adherence to Standards**:
  - Enforces robots.txt and terms-of-service compliance with configurable, identifiable user-agent settings.
  - Applies host-specific rate-limiting to prevent overloading servers.
- **Structured Exports**:
  - Outputs clean datasets in CSV and Excel formats with safeguards against formula injection by neutralizing malicious characters.
- **Security-Oriented Testing**:
  - Includes adversarial testing for edge scenarios such as redirect loops, decompression bombs, malformed encodings, large responses, and partial failures.
- **Streamlit Interface**:
  - Intuitive and interactive visualization and control panel for managing crawling tasks and analyzing results.

## 🏗️ Architecture & Workflow
The architecture of **my_crawler** ensures modularity, security, and extensibility at every layer.

```mermaid
graph TD
    A[Start Crawler] --> B[Streamlit UI]
    B --> C[Input URLs]
    B --> D[Set Parameters]
    C --> E[Resolve DNS & Validate IPs]
    E --> F{Redirects?}
    F -->|Yes| G[Follow Redirects Safely]
    G --> H[Validate Destination]
    F -->|No| H[Validate Destination]
    H --> I[Check Robots.txt & ToS]
    I --> J[Scrape with Selenium in Sandbox]
    J --> K[Parse with BeautifulSoup]
    K --> L[Export Data (CSV/Excel)]
    L --> M[End Process]
```

## 💻 Tech Stack & Tools Breakdown
- **Programming Language**: Python 3.9+
- **Frameworks & Libraries**:
  - **Streamlit**: Interactive UI for controlling and visualizing crawls.
  - **Selenium**: Browser automation with sandboxing for secure website interactions.
  - **BeautifulSoup4**: HTML parsing and content extraction.
  - **Pandas**: Data processing and structuring.
- **Formats**:
  - **CSV/Excel**: Export structured data securely with injection-neutral sanitization.
- **Testing**:
  - **pytest**: Robust and adversarial test cases for security and reliability.

## 🚀 Quickstart / Installation
Follow these steps to install and run **my_crawler**:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/EF361/my_crawler.git
   cd my_crawler
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**:
   ```bash
   pytest
   ```

5. **Start the Streamlit interface**:
   ```bash
   streamlit run app.py
   ```

6. **Configure and start crawling**:
   - Use the Streamlit interface to input URLs, configure crawling parameters, and begin the process.

7. **View and export results**:
   - Download crawled data directly from the interface in CSV or Excel formats.

---

**Disclaimer**: Always ensure compliance with the target website's terms of service and applicable regulations before crawling.