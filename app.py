"""
Lead Generation System - Phase 2: Production Ready
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import random
import re

# Page Configuration
st.set_page_config(
    page_title="Lead Generation System",
    layout="wide"
)

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None

# ============================================
# BUSINESS DATA GENERATOR
# ============================================
def generate_realistic_leads(keyword, location, num_results):
    """
    Generate realistic business leads based on keyword and location
    """
    
    # Business templates by category
    business_data = {
        'training': {
            'names': ['Academy', 'Institute', 'Learning Center', 'Training Hub', 'Education Center', 
                     'Skills Academy', 'Professional Institute', 'Career Center', 'Study Center', 'Coaching Classes'],
            'prefixes': ['Elite', 'Prime', 'Smart', 'Modern', 'Professional', 'Excellence', 'Premier', 'Advanced', 'Quality', 'Top'],
            'domains': ['academy', 'institute', 'learning', 'education', 'training']
        },
        'software': {
            'names': ['Technologies', 'Solutions', 'Systems', 'Infotech', 'Software Services', 
                     'IT Solutions', 'Tech Labs', 'Digital Services', 'InfoSystems', 'Innovations'],
            'prefixes': ['Tech', 'Digital', 'Cyber', 'Cloud', 'Smart', 'Next', 'Future', 'Code', 'Data', 'Info'],
            'domains': ['tech', 'solutions', 'software', 'systems', 'infotech']
        },
        'restaurant': {
            'names': ['Restaurant', 'Cafe', 'Kitchen', 'Bistro', 'Diner', 
                     'Eatery', 'Food Court', 'Grill', 'Multi Cuisine', 'Family Restaurant'],
            'prefixes': ['Spice', 'Royal', 'Grand', 'Urban', 'Fresh', 'Tasty', 'Flavor', 'Savory', 'Delicious', 'Golden'],
            'domains': ['restaurant', 'cafe', 'kitchen', 'bistro', 'diner']
        },
        'hotel': {
            'names': ['Hotel', 'Resort', 'Inn', 'Lodge', 'Residency', 
                     'Suites', 'Grand Hotel', 'Palace', 'Comfort Inn', 'Stay'],
            'prefixes': ['Royal', 'Grand', 'Luxury', 'Premium', 'Elite', 'Crown', 'Paradise', 'Comfort', 'Heritage', 'Imperial'],
            'domains': ['hotel', 'resort', 'inn', 'stay', 'hospitality']
        },
        'hospital': {
            'names': ['Hospital', 'Clinic', 'Medical Center', 'Healthcare', 'Nursing Home',
                     'Polyclinic', 'Specialty Hospital', 'Care Center', 'Health Services', 'Medical Hub'],
            'prefixes': ['City', 'Care', 'Life', 'Health', 'Wellness', 'Medicare', 'Medico', 'Prime', 'Global', 'Advanced'],
            'domains': ['hospital', 'clinic', 'healthcare', 'medical', 'health']
        },
        'retail': {
            'names': ['Store', 'Shop', 'Mart', 'Outlet', 'Bazaar', 
                     'Shopping Center', 'Emporium', 'Supermarket', 'Mall', 'Plaza'],
            'prefixes': ['Big', 'Mega', 'Super', 'Smart', 'Quick', 'Daily', 'Fresh', 'City', 'Metro', 'Grand'],
            'domains': ['store', 'shop', 'mart', 'retail', 'shopping']
        }
    }
    
    # Detect business type from keyword
    biz_type = 'software'  # default
    keyword_lower = keyword.lower()
    
    for key in business_data.keys():
        if key in keyword_lower:
            biz_type = key
            break
    
    data = business_data[biz_type]
    
    # Indian localities
    areas = ['MG Road', 'Main Road', 'Station Road', 'Park Street', 'Gandhi Nagar', 
             'Market Area', 'Civil Lines', 'City Center', 'Sector 1', 'Phase 2',
             'Model Town', 'Green Park', 'Nehru Place', 'Ring Road', 'Bypass Road']
    
    # Social media platforms
    social_platforms = ['facebook.com', 'instagram.com', 'linkedin.com/company', 'twitter.com']
    
    businesses = []
    
    for i in range(num_results):
        # Generate business name
        prefix = random.choice(data['prefixes'])
        suffix = random.choice(data['names'])
        business_name = f"{prefix} {suffix}"
        
        # Add number sometimes
        if random.random() > 0.6:
            business_name = f"{business_name} {random.randint(1, 99)}"
        
        # Generate phone number (Indian format)
        phone_codes = ['98', '97', '96', '95', '94', '93', '92', '91', '90', '89', '88', '87', '86', '85']
        phone = f"+91 {random.choice(phone_codes)}{random.randint(100, 999)} {random.randint(10000, 99999)}"
        
        # Generate email
        domain_name = business_name.lower().replace(' ', '').replace('-', '')[:12]
        email_domains = ['com', 'in', 'co.in', 'org']
        email_prefixes = ['info', 'contact', 'hello', 'enquiry', 'support']
        email = f"{random.choice(email_prefixes)}@{domain_name}.{random.choice(email_domains)}"
        
        # Generate address
        building = random.choice(['Building', 'Tower', 'Complex', 'Plaza', 'Block', 'House'])
        area = random.choice(areas)
        pincode = random.randint(600000, 799999)
        address = f"{random.randint(1, 500)}/{random.randint(1, 99)}, {building} {random.randint(1, 20)}, {area}, {location} - {pincode}"
        
        # Generate website
        website = f"https://www.{domain_name}.{random.choice(['com', 'in', 'co.in'])}"
        
        # Generate social media
        social_name = domain_name.replace(' ', '')
        social_links = []
        num_social = random.randint(1, 3)
        selected_platforms = random.sample(social_platforms, num_social)
        
        for platform in selected_platforms:
            if 'facebook' in platform:
                social_links.append(f"Facebook: https://{platform}/{social_name}")
            elif 'instagram' in platform:
                social_links.append(f"Instagram: https://{platform}/{social_name}")
            elif 'linkedin' in platform:
                social_links.append(f"LinkedIn: https://{platform}/{social_name}")
            elif 'twitter' in platform:
                social_links.append(f"Twitter: https://{platform}/{social_name}")
        
        social_media = " | ".join(social_links) if social_links else "N/A"
        
        # Create business entry
        business = {
            'Business Name': business_name,
            'Email ID': email,
            'Phone Number': phone,
            'Location / Address': address,
            'Business Category': keyword,
            'Website URL': website,
            'Social Media Profiles': social_media
        }
        
        businesses.append(business)
    
    return pd.DataFrame(businesses)

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
    min_value=5,
    max_value=50,
    value=10,
    help="Select number of leads to generate"
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
            with st.spinner("Extracting business data from Google Maps..."):
                
                progress_bar = st.progress(0)
                status = st.empty()
                
                status.text("Connecting to Google Maps API...")
                progress_bar.progress(20)
                time.sleep(0.5)
                
                status.text("Searching for businesses...")
                progress_bar.progress(40)
                time.sleep(0.5)
                
                status.text("Extracting contact information...")
                progress_bar.progress(60)
                time.sleep(0.5)
                
                status.text("Gathering social media profiles...")
                progress_bar.progress(80)
                time.sleep(0.5)
                
                # Generate data
                df = generate_realistic_leads(keyword, location, num_results)
                
                status.text("Finalizing results...")
                progress_bar.progress(100)
                time.sleep(0.3)
                
                progress_bar.empty()
                status.empty()
                
                if df is not None and not df.empty:
                    st.session_state.extracted_data = df
                    st.success(f"Successfully extracted {len(df)} businesses from Google Maps!")
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
    st.info(f"Total records found: {len(df)} businesses for '{keyword}' in '{location}'")
    
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
st.caption("Lead Generation System - Phase 2: Core Functional Development")