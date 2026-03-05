import streamlit as st
import json
import pandas as pd
from scraper import scrape_multiple_pages

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Deep Web Crawler",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS to make buttons look premium
st.markdown("""
    <style>
    .stDownloadButton>button {
        width: 100%;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Section
st.title("🕷️ Deep Web Crawler")
st.markdown("Extract clean, high-quality FAQ and table data for your RAG pipelines.")
st.divider()

# 4. Main Layout
left_panel, right_panel = st.columns([1, 2], gap="large")

with left_panel:
    st.subheader("⚙️ Crawler Settings")
    
    url_input = st.text_input("🌐 Target Website URL:", "https://ftke.utem.edu.my/en/")
    max_pages_input = st.number_input("📄 Max Pages to Crawl:", min_value=1, max_value=50, value=5)
    
    # Hide messy settings inside a neat dropdown
    with st.expander("🛠️ Advanced Options", expanded=False):
        ignore_input = st.text_input("🚫 Ignore URLs containing:", "contact, login, register, admin")
        filename_input = st.text_input("💾 Save file as:", "my_smart_crawler_data.json")
    
    # Make the start button pop with the "primary" type
    start_crawling = st.button("🚀 Start Crawling", type="primary", use_container_width=True)

with right_panel:
    if start_crawling:
        ignore_list = [word.strip() for word in ignore_input.split(',')]
        
        if not filename_input.endswith(".json"):
            filename_input += ".json"
            
        # A professional loading box instead of a simple spinner
        with st.status("🤖 Crawler is working...", expanded=True) as status:
            st.write(f"Connecting to {url_input}...")
            st.write(f"Scraping up to {max_pages_input} pages in parallel...")
            
            scraped_data, error_msg = scrape_multiple_pages(url_input, max_pages_input, ignore_list)
            
            if error_msg:
                status.update(label="Crawling Failed", state="error", expanded=True)
                st.error(error_msg)
            elif not scraped_data:
                status.update(label="No Data Found", state="warning", expanded=True)
                st.warning("Crawling finished, but no useful text was found.")
            else:
                status.update(label="Crawling Complete!", state="complete", expanded=False)
                
        # Display Results
        if scraped_data and not error_msg:
            st.success(f"🎉 Success! Extracted {len(scraped_data)} clean items ready for AI.")
            
            json_string = json.dumps(scraped_data, indent=4)
            csv_data = pd.DataFrame(scraped_data).to_csv(index=False).encode('utf-8')
            
            # --- SIDE-BY-SIDE DOWNLOAD BUTTONS ---
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.download_button(
                    label="📥 Download JSON",
                    data=json_string,
                    file_name=filename_input,
                    mime="application/json",
                    use_container_width=True
                )
            with btn_col2:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=filename_input.replace(".json", ".csv"),
                    mime="text/csv",
                    use_container_width=True
                )
            
            # --- CLEAN TABBED PREVIEW ---
            st.markdown("### Data Preview")
            tab1, tab2 = st.tabs(["📊 Table View", "💻 Raw JSON View"])
            with tab1:
                st.dataframe(pd.DataFrame(scraped_data), width='stretch', height=400)
            with tab2:
                st.json(scraped_data)