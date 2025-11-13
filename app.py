"""
Lead Generation System - Phase 2: Real Data with Selenium
Scrapes real business data from Google Maps
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
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import requests
from bs4 import BeautifulSoup
                
# Page Configuration
st.set_page_config(
    page_title="Lead Generation System",
    layout="wide"
)

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None

# ============================================
# HELPER FUNCTIONS TO EXTRACT EMAIL & SOCIAL MEDIA
# ============================================
def extract_email_from_website(website_url):
    """
    Visit website and try to extract email address
    """
    if website_url == "N/A" or not website_url:
        return "N/A"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(website_url, headers=headers, timeout=5)
        
        # Look for email patterns in the HTML
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, response.text)
        
        if emails:
            # Filter out common non-business emails
            filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['example.com', 'sentry', 'google', 'facebook', 'twitter'])]
            if filtered_emails:
                return filtered_emails[0]
        
        return "N/A"
    except:
        return "N/A"

def extract_social_media_from_website(website_url):
    """
    Visit website and try to extract social media links
    """
    if website_url == "N/A" or not website_url:
        return "N/A"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(website_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        social_links = []
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link['href']
            if 'facebook.com' in href:
                social_links.append(f"Facebook: {href}")
            elif 'instagram.com' in href:
                social_links.append(f"Instagram: {href}")
            elif 'linkedin.com' in href:
                social_links.append(f"LinkedIn: {href}")
            elif 'twitter.com' in href or 'x.com' in href:
                social_links.append(f"Twitter: {href}")
        
        if social_links:
            return " | ".join(social_links[:3])  # Return top 3
        
        return "N/A"
    except:
        return "N/A"

# ============================================
# SELENIUM SCRAPING FUNCTION
# ============================================
def scrape_google_maps_real(keyword, location, max_results=10):
    """
    Scrape real data from Google Maps using Selenium
    """
    businesses = []
    driver = None
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Build search query
        search_query = f"{keyword} in {location}".replace(" ", "+")
        url = f"https://www.google.com/maps/search/{search_query}"
        
        driver.get(url)
        time.sleep(5)
        
        # Wait for results to load
        wait = WebDriverWait(driver, 10)
        
        # Find the scrollable panel
        try:
            panel = driver.find_element(By.XPATH, "//div[@role='feed']")
        except:
            st.error("Could not find results panel")
            return pd.DataFrame()
        
        # Scroll to load results
        scroll_pause = 2
        last_height = driver.execute_script("return arguments[0].scrollHeight", panel)
        
        for _ in range(5):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return arguments[0].scrollHeight", panel)
            if new_height == last_height:
                break
            last_height = new_height
        
        # Get all business links
        business_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://www.google.com/maps/place')]")
        
        # Limit to max_results
        business_links = business_links[:max_results]
        
        st.info(f"Found {len(business_links)} businesses. Extracting details...")
        
        # Extract details for each business
        for idx, link in enumerate(business_links):
            try:
                # Click on business
                driver.execute_script("arguments[0].click();", link)
                time.sleep(3)
                
                # Extract business name
                try:
                    name = driver.find_element(By.XPATH, "//h1[contains(@class, 'DUwDvf')]").text
                except:
                    name = "N/A"
                
                # Extract phone number
                phone = "N/A"
                try:
                    # Look for phone in various ways
                    phone_elements = driver.find_elements(By.XPATH, "//button[contains(@data-item-id, 'phone')]")
                    if phone_elements:
                        phone_text = phone_elements[0].get_attribute('aria-label')
                        if phone_text:
                            # Extract phone from aria-label
                            phone_match = re.search(r'[\d\s\+\-\(\)]+', phone_text)
                            if phone_match:
                                phone = phone_match.group().strip()
                except:
                    pass
                
                # Extract address
                address = "N/A"
                try:
                    address_elements = driver.find_elements(By.XPATH, "//button[contains(@data-item-id, 'address')]")
                    if address_elements:
                        address = address_elements[0].get_attribute('aria-label')
                        if address and ':' in address:
                            address = address.split(':', 1)[1].strip()
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
                
                # Extract rating (bonus info)
                rating = "N/A"
                try:
                    rating_element = driver.find_element(By.XPATH, "//div[contains(@class, 'F7nice')]//span[@aria-hidden='true']")
                    rating = rating_element.text
                except:
                    pass
                
                # Extract email from website (if website exists)
                st.text(f"Checking website for email and social media...")
                email = extract_email_from_website(website)
                social_media = extract_social_media_from_website(website)
                
                # Create business entry
                business = {
                    'Business Name': name,
                    'Email ID': email,
                    'Phone Number': phone,
                    'Location / Address': address,
                    'Business Category': category,
                    'Website URL': website,
                    'Social Media Profiles': social_media
                }
                
                businesses.append(business)
                
                st.text(f"Extracted {idx + 1}/{len(business_links)}: {name}")
                
            except Exception as e:
                st.warning(f"Skipped business {idx + 1}: {str(e)}")
                continue
        
        return pd.DataFrame(businesses)
        
    except Exception as e:
        st.error(f"Scraping error: {str(e)}")
        return pd.DataFrame()
    
    finally:
        if driver:
            driver.quit()

# ============================================
# HEADER
# ============================================
st.title("Lead Generation Automation System")
st.write("Real Data Extraction from Google Maps")

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
        placeholder="e.g., Training Institute, Restaurant, Hotel"
    )

with col2:
    location = st.text_input(
        "Location",
        placeholder="e.g., Kochi, Mumbai, Bangalore"
    )

num_results = st.slider(
    "Number of Results",
    min_value=3,
    max_value=15,
    value=5,
    help="⚠️ More results = longer wait time (5-10 results recommended)"
)

st.divider()

# ============================================
# START EXTRACTION BUTTON
# ============================================
st.subheader("Start Extraction")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("Start Extraction", type="primary", use_container_width=True):
        if not keyword or not location:
            st.error("Please enter both keyword and location")
        else:
            with st.spinner(f"Scraping Google Maps for real data... This will take about {num_results * 5} seconds..."):
                
                progress_text = st.empty()
                progress_text.text("Opening Chrome browser...")
                time.sleep(1)
                
                progress_text.text("Loading Google Maps...")
                time.sleep(1)
                
                progress_text.text("Searching and extracting data...")
                
                # Scrape real data
                df = scrape_google_maps_real(keyword, location, num_results)
                
                progress_text.empty()
                
                if df is not None and not df.empty:
                    st.session_state.extracted_data = df
                    st.success(f"Successfully extracted {len(df)} REAL businesses from Google Maps!")
                else:
                    st.error("No results found. Try different keywords or check your internet connection.")

st.divider()

# ============================================
# DISPLAY RESULTS
# ============================================
st.subheader("Extracted Leads")

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
    st.info(f"Total records found: {len(df)} REAL businesses for '{keyword}' in '{location}'")
    
    # Data quality note
    with st.expander("ℹ️ About the extracted data"):
        st.write("**Real data from Google Maps:**")
        st.write("✅ Business names - Real")
        st.write("✅ Phone numbers - Real (when available)")
        st.write("✅ Addresses - Real")
        st.write("✅ Websites - Real (when available)")
        st.write("❌ Emails - Not available on Google Maps")
        st.write("❌ Social Media - Not available on Google Maps")
    
else:
    # Empty table
    empty_df = pd.DataFrame(columns=[
        'Business Name', 'Email ID', 'Phone Number',
        'Location / Address', 'Business Category',
        'Website URL', 'Social Media Profiles'
    ])
    st.dataframe(empty_df, use_container_width=True, height=200)
    st.info("No data yet. Enter search parameters and click 'Start Extraction'")

st.divider()

# ============================================
# EXPORT SECTION
# ============================================
st.subheader("Export Data")

if st.session_state.extracted_data is not None:
    # Generate CSV
    csv = st.session_state.extracted_data.to_csv(index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_keyword = keyword.replace(' ', '_').lower() if keyword else 'leads'
    filename = f"leads_{clean_keyword}_{location.lower().replace(' ', '_')}_{timestamp}.csv"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
            use_container_width=True
        )
    
    st.success(f"File ready: {filename}")
    
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.button("Download as CSV", disabled=True, use_container_width=True)
    st.caption("Extract leads first to enable download")

# Footer
st.divider()
st.caption("Lead Generation System - Phase 2 with Real Selenium Scraping")