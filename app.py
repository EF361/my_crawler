import streamlit as st
import json
import pandas as pd
from scraper import scrape_multiple_pages

st.set_page_config(layout="wide")

left_panel, right_panel = st.columns([1, 2])

with left_panel:
    st.title("Deep Web Crawler")
    
    url_input = st.text_input("Enter website URL to crawl:", "https://ftke.utem.edu.my/en/")
    max_pages_input = st.number_input("Maximum pages to crawl:", min_value=1, max_value=50, value=5)
    
    ignore_input = st.text_input("Ignore URLs containing (comma-separated):", "contact, login, register, admin")
    
    # NEW: Option to rename the output JSON file
    filename_input = st.text_input("Save file as:", "my_smart_crawler_data.json")
    
    start_crawling = st.button("Start Crawling")

with right_panel:
    if start_crawling:
        ignore_list = [word.strip() for word in ignore_input.split(',')]
        
        # Make sure the user didn't forget the .json extension
        if not filename_input.endswith(".json"):
            filename_input += ".json"
            
        with st.spinner(f"Crawling up to {max_pages_input} pages..."):
            
            scraped_data, error_msg = scrape_multiple_pages(url_input, max_pages_input, ignore_list)
            
            if error_msg:
                st.error(error_msg)
                
            elif scraped_data:
                json_string = json.dumps(scraped_data, indent=4)
                
                # Updated download button with custom filename
                st.download_button(
                    label="Download JSON",
                    data=json_string,
                    file_name=filename_input,
                    mime="application/json"
                )
                
                st.success(f"Crawling successful! Found {len(scraped_data)} clean items.")
                st.dataframe(pd.DataFrame(scraped_data), width='stretch')