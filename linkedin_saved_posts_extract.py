import time
import re
import gspread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# --- CONFIGURATION ---

# LinkedIn Credentials
LINKEDIN_EMAIL = "xxx@gmail.com"
LINKEDIN_PASSWORD = "xxxx"

# Google Sheets Configuration
GSHEET_NAME = "My LinkedIn Posts"
GSHEET_WORKSHEET_NAME = "Saved Post URLs"
GCREDS_FILE = r"C:\xxxxxxxxxxxxxxxxxxx.json"
YOUR_PERSONAL_EMAIL = "xxx@gmail.com"

# Paste the ID of the Google Drive folder you created and shared.
# For example: "1a2b3c4d5e6f7g8h9i0j..."
GDRIVE_FOLDER_ID = "your_folder_ID"


# --- FUNCTIONS ---

def scrape_linkedin_post_urls():
    """
    Scrapes the URLs of saved posts from your LinkedIn account using Google Chrome.
    """
    print("Logging in to LinkedIn using Google Chrome...")
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)

    try:
        driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        print("Login submitted. Waiting for page to load...")
        time.sleep(10)
    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()
        return []

    print("Navigating to saved posts...")
    driver.get("https://www.linkedin.com/my-items/saved-posts/")
    time.sleep(10)

    print("Scrolling to load all posts...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    while scroll_attempts < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
        last_height = new_height

    # --- FIX STARTS HERE ---
    print("Extracting post URLs...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    found_urls = set()

    # New strategy: Find the main content container for the feed/list.
    # This class is often used for the scrollable content area.
    content_container = soup.find("div", class_=re.compile(r"scaffold-finite-scroll__content"))

    if not content_container:
        print("Could not find the main content container. The LinkedIn page structure may have changed.")
        link_elements = []
    else:
        # Find all links within that container.
        link_elements = content_container.find_all("a", href=True)

    if not link_elements:
         print("Found content container, but it contains no links.")

    for link_element in link_elements:
        try:
            href = link_element['href']
            
            # We only want links to actual posts (activities) or articles (pulse).
            # This is a more targeted filter.
            if "/feed/update/urn:li:activity:" in href or "/pulse/" in href:
                # Check if the URL is relative or absolute to build the correct full URL.
                if href.startswith('/'):
                    full_url = f"https://www.linkedin.com{href}"
                else:
                    full_url = href

                # Clean the URL by removing query parameters (like ?utm_source=...).
                clean_url = full_url.split("?")[0]
                
                if clean_url not in found_urls:
                    print(f"Found URL: {clean_url}")
                    found_urls.add(clean_url)
        except Exception as e:
            print(f"Could not parse a link element: {e}")
            continue
    # --- FIX ENDS HERE ---

    driver.quit()
    return list(found_urls)

def save_to_google_sheets(urls):
    """
    Saves the extracted URLs to a Google Sheet inside a specific Drive folder.
    """
    print("Authenticating with Google Sheets...")
    gc = gspread.service_account(filename=GCREDS_FILE)

    try:
        sh = gc.open(GSHEET_NAME, folder_id=GDRIVE_FOLDER_ID)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Spreadsheet '{GSHEET_NAME}' not found, creating a new one in your specified folder.")
        # Create the new sheet inside the folder you specified.
        sh = gc.create(GSHEET_NAME, folder_id=GDRIVE_FOLDER_ID)
        print(f"Sharing sheet with {YOUR_PERSONAL_EMAIL}")
        sh.share(YOUR_PERSONAL_EMAIL, perm_type='user', role='writer')

    try:
        worksheet = sh.worksheet(GSHEET_WORKSHEET_NAME)
        worksheet.clear()
        print("Cleared existing data from worksheet.")
    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{GSHEET_WORKSHEET_NAME}' not found, creating a new one.")
        worksheet = sh.add_worksheet(title=GSHEET_WORKSHEET_NAME, rows="1000", cols="1")
    
    worksheet.append_row(["Post URL"])
    print(f"Adding {len(urls)} new URLs to the sheet...")
    rows_to_add = [[url] for url in urls]

    if rows_to_add:
        worksheet.append_rows(rows_to_add)

# --- MAIN ---

if __name__ == "__main__":
    urls = scrape_linkedin_post_urls()
    if urls:
        print(f"Found {len(urls)} post URLs. Saving to Google Sheets...")
        save_to_google_sheets(urls)
        print(f"Successfully extracted and saved {len(urls)} URLs to your Google Sheet!")
    else:
        print("No posts were found or extracted. Please check your LinkedIn 'Saved Posts' page.")
