"""
Lead Generation System - Real Data with Selenium
Optimized for Render.com deployment
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os

# Page Configuration
st.set_page_config(
    page_title="Lead Generation System",
    layout="wide"
)

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None

# ============================================
# SELENIUM SCRAPING FUNCTION - REAL DATA
# ============================================
@st.cache_data(ttl=3600, show_spinner=False)
def scrape_google_maps_real(keyword, location, max_results=10):
    """
    Scrape REAL data from Google Maps using Selenium
    """
    businesses = []
    driver = None
    
    try:
        # Setup Chrome options for Render.com
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # For Render.com - use system Chrome
        chrome_options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium-browser")
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Build search URL
        search_query = f"{keyword} in {location}".replace(" ", "+")
        url = f"https://www.google.com/maps/search/{search_query}"
        
        st.info(f"🌐 Connecting to Google Maps...")
        driver.get(url)
        time.sleep(5)
        
        # Wait for results panel
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
            )
        except:
            st.warning("⚠️ Could not load results panel")
            return pd.DataFrame()
        
        # Find scrollable panel
        panel = driver.find_element(By.XPATH, "//div[@role='feed']")
        
        st.info(f"📜 Scrolling to load {max_results} results...")
        
        # Scroll to load results
        last_height = driver.execute_script("return arguments[0].scrollHeight", panel)
        scroll_attempts = 0
        max_scroll_attempts = 10
        
        while scroll_attempts < max_scroll_attempts:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", panel)
            
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
        
        # Get all business links
        business_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/maps/place/')]")
        
        if not business_elements:
            st.error("❌ No businesses found")
            return pd.DataFrame()
        
        # Limit to requested number
        business_elements = business_elements[:max_results]
        
        st.info(f"✅ Found {len(business_elements)} businesses. Extracting details...")
        
        # Progress tracking
        progress_placeholder = st.empty()
        
        # Extract each business
        for idx, element in enumerate(business_elements):
            try:
                progress_placeholder.text(f"⏳ Extracting {idx + 1}/{len(business_elements)}: Please wait...")
                
                # Click on business
                driver.execute_script("arguments[0].click();", element)
                time.sleep(4)
                
                # Extract business name
                name = "N/A"
                try:
                    name_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
                    )
                    name = name_element.text
                except:
                    try:
                        name = driver.find_element(By.XPATH, "//h1").text
                    except:
                        pass
                
                if name == "N/A" or not name:
                    continue
                
                # Extract phone number
                phone = "N/A"
                try:
                    phone_elements = driver.find_elements(By.XPATH, "//button[contains(@data-item-id, 'phone')]")
                    if phone_elements:
                        aria_label = phone_elements[0].get_attribute('aria-label')
                        if aria_label:
                            phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,}', aria_label)
                            if phone_match:
                                phone = phone_match.group().strip()
                except:
                    pass
                
                # Extract address
                address = "N/A"
                try:
                    address_elements = driver.find_elements(By.XPATH, "//button[contains(@data-item-id, 'address')]")
                    if address_elements:
                        aria_label = address_elements[0].get_attribute('aria-label')
                        if aria_label and ':' in aria_label:
                            address = aria_label.split(':', 1)[1].strip()
                except:
                    pass
                
                # Extract website
                website = "N/A"
                try:
                    website_elements = driver.find_elements(By.XPATH, "//a[contains(@data-item-id, 'authority')]")
                    if website_elements:
                        website = website_elements[0].get_attribute('href')
                except:
                    pass
                
                # Extract category
                category = keyword
                try:
                    category_element = driver.find_element(By.XPATH, "//button[contains(@class, 'DkEaL')]")
                    category = category_element.text
                except:
                    pass
                
                # Extract rating (bonus)
                rating = "N/A"
                try:
                    rating_element = driver.find_element(By.XPATH, "//div[contains(@class, 'F7nice')]//span[@aria-hidden='true']")
                    rating = rating_element.text
                except:
                    pass
                
                # Create business entry
                business = {
                    'Business Name': name,
                    'Email ID': 'N/A',  # Not available on Google Maps
                    'Phone Number': phone,
                    'Location / Address': address,
                    'Business Category': category,
                    'Website URL': website,
                    'Social Media Profiles': 'N/A'  # Not available on Google Maps
                }
                
                businesses.append(business)
                progress_placeholder.text(f"✅ Extracted {idx + 1}/{len(business_elements)}: {name}")
                
            except Exception as e:
                progress_placeholder.text(f"⚠️ Skipped business {idx + 1}: {str(e)}")
                time.sleep(1)
                continue
        
        progress_placeholder.empty()
        return pd.DataFrame(businesses)
        
    except Exception as e:
        st.error(f"❌ Scraping error: {str(e)}")
        return pd.DataFrame()
    
    finally:
        if driver:
            driver.quit()

# ============================================
# HEADER
# ============================================
st.title("Lead Generation Automation System")
st.write("Real-time Data Extraction from Google Maps")

st.info("🔥 This system extracts 100% REAL business data from Google Maps using web scraping technology.")

st.divider()

# ============================================
# MODE SELECTION
# ============================================
st.subheader("Select Extraction Mode")

mode = st.radio(
    "Choose mode:",
    ["Target based lead extraction module", "Keyword Search Mode"]
)

st.divider()

# ============================================
# INPUT FIELDS
# ============================================
st.subheader("Search Parameters")

col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input(
        "Search Keyword",
        placeholder="e.g., Training Institute, Restaurant, Hotel",
        help="Enter the type of business you want to find"
    )

with col2:
    location = st.text_input(
        "Location",
        placeholder="e.g., Kochi, Mumbai, Bangalore",
        help="Enter the city or area"
    )

num_results = st.slider(
    "Number of Results",
    min_value=3,
    max_value=20,
    value=5,
    help="⚠️ Each result takes ~5 seconds. Recommended: 5-10 results"
)

st.warning(f"⏱️ Estimated time: ~{num_results * 5} seconds")

st.divider()

# ============================================
# START EXTRACTION BUTTON
# ============================================
st.subheader("Start Extraction")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🚀 Start Extraction", type="primary", use_container_width=True):
        if not keyword or not location:
            st.error("⚠️ Please enter both keyword and location")
        else:
            with st.spinner("🔄 Extracting real business data from Google Maps..."):
                
                # Clear cache for fresh data
                st.cache_data.clear()
                
                # Scrape real data
                df = scrape_google_maps_real(keyword, location, num_results)
                
                if df is not None and not df.empty:
                    st.session_state.extracted_data = df
                    st.success(f"✅ Successfully extracted {len(df)} REAL businesses from Google Maps!")
                else:
                    st.error("❌ No results found. Please try different keywords or location.")

st.divider()

# ============================================
# DISPLAY RESULTS
# ============================================
st.subheader("📊 Extracted Leads")

if st.session_state.extracted_data is not None:
    df = st.session_state.extracted_data
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(df))
    with col2:
        email_count = len(df[df['Email ID'] != 'N/A'])
        st.metric("With Email", email_count)
    with col3:
        phone_count = len(df[df['Phone Number'] != 'N/A'])
        st.metric("With Phone", phone_count)
    with col4:
        website_count = len(df[df['Website URL'] != 'N/A'])
        st.metric("With Website", website_count)
    
    st.write("")
    
    # Data table
    st.dataframe(df, use_container_width=True, height=400)
    
    # Total records message
    st.info(f"📋 Total records found: **{len(df)} REAL businesses** for '{keyword}' in '{location}'")
    
    # Data authenticity note
    st.success("✅ All data extracted is 100% REAL from Google Maps")
    
else:
    # Empty table
    empty_df = pd.DataFrame(columns=[
        'Business Name', 'Email ID', 'Phone Number',
        'Location / Address', 'Business Category',
        'Website URL', 'Social Media Profiles'
    ])
    st.dataframe(empty_df, use_container_width=True, height=200)
    st.info("👆 No data yet. Enter search parameters and click 'Start Extraction'")

st.divider()

# ============================================
# EXPORT SECTION
# ============================================
st.subheader("💾 Export Data")

if st.session_state.extracted_data is not None:
    # Generate CSV
    csv = st.session_state.extracted_data.to_csv(index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_keyword = keyword.replace(' ', '_').lower() if keyword else 'leads'
    filename = f"real_leads_{clean_keyword}_{location.lower().replace(' ', '_')}_{timestamp}.csv"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="⬇️ Download Real Data as CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
            use_container_width=True
        )
    
    st.success(f"✅ File ready: {filename}")
    
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button("⬇️ Download as CSV", disabled=True, use_container_width=True)
    st.caption("⚠️ Extract leads first to enable download")

# Footer
st.divider()
st.caption("🔥 Lead Generation System - Powered by Real-time Google Maps Scraping")