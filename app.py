import streamlit as st
import json
import pandas as pd

from scraper import scrape_multiple_pages

st.set_page_config(layout="wide")

left_panel, right_panel = st.columns([1, 2])

with left_panel:
    st.title("Deep Web Crawler")
    
    url_input = st.text_input("Enter website URL to crawl:", "https://audit.utem.edu.my/en/faq.html")
    
    max_pages_input = st.number_input("Maximum pages to crawl:", min_value=1, max_value=50, value=5)
    
    # Add an input to let you type the words you want to ignore
    ignore_input = st.text_input("Ignore URLs containing (comma-separated):", "contact, login, register, admin")
    
    start_crawling = st.button("Start Crawling")

with right_panel:
    if start_crawling:
        # Convert your comma-separated words into a neat list for the robot
        ignore_list = [word.strip() for word in ignore_input.split(',')]
        
        with st.spinner(f"Crawling up to {max_pages_input} pages... this will take longer."):
            
            # Pass the new ignore list to the scraper
            scraped_data, error_msg = scrape_multiple_pages(url_input, max_pages_input, ignore_list)
            
            if error_msg:
                st.error(error_msg)
                
            elif scraped_data:
                json_string = json.dumps(scraped_data, indent=4)
                
                st.download_button(
                    label="Download JSON",
                    data=json_string,
                    file_name="deep_crawler_data.json",
                    mime="application/json"
                )
                
                st.success(f"Crawling successful! Found {len(scraped_data)} items.")
                
                st.dataframe(pd.DataFrame(scraped_data), width='stretch')
                
                st.json(scraped_data)