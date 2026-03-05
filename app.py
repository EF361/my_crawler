import streamlit as st
import json
import pandas as pd
from scraper import scrape_faq

# Make the page wide to fit the two panels nicely
st.set_page_config(layout="wide")

# Create two columns (panels). The [1, 2] means the right panel is twice as wide.
left_panel, right_panel = st.columns([1, 2])

with left_panel:
    st.title("Normal Web Crawler")
    
    url_input = st.text_input("Enter website URL to crawl:", "https://audit.utem.edu.my/en/faq.html")
    
    # We assign the button to a variable to trigger actions in the right panel
    start_crawling = st.button("Start Crawling")

with right_panel:
    if start_crawling:
        with st.spinner("Crawling in progress..."):
            
            scraped_data, error_msg = scrape_faq(url_input)
            
            if error_msg:
                st.error(error_msg)
                
            elif scraped_data:
                # Prepare JSON string for the download button
                json_string = json.dumps(scraped_data, indent=4)
                
                # 1. Download button at the top
                st.download_button(
                    label="Download JSON",
                    data=json_string,
                    file_name="crawler_data.json",
                    mime="application/json"
                )
                
                st.success("Crawling successful!")
                
                # 2. Table output (Updated to fix the warning)
                st.dataframe(pd.DataFrame(scraped_data), width='stretch')
                
                # 3. Raw JSON output
                st.json(scraped_data)