import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# --- CONFIGURATION ---
# !! IMPORTANT !!
# It is highly recommended to use a throwaway Facebook account for this.
# Using your personal account risks it being suspended or banned.
FACEBOOK_EMAIL = "marvelwilberto@gmail.com"
FACEBOOK_PASSWORD = "natsudragneel"
POST_URL = "https://web.facebook.com/share/p/15iUeZXKTr/" # <-- Change this to the URL of the post you want to scrape

# Number of times to scroll down to load comments.
# Increase this for posts with more comments.
SCROLL_COUNT = 10

# --- SELENIUM SETUP ---
def setup_driver():
    """Sets up the Selenium WebDriver."""
    chrome_options = Options()
    # This option disables browser notifications (e.g., "Show notifications" popup)
    chrome_options.add_argument("--disable-notifications")
    
    # Use webdriver-manager to automatically handle the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# --- FACEBOOK LOGIN ---
def login_to_facebook(driver, email, password):
    """Navigates to Facebook and logs in."""
    driver.get("https://www.facebook.com")
    
    # Wait for the page to load
    time.sleep(2)

    # Handle cookie consent if it appears
    try:
        # The button might have different identifiers, this is a common one
        cookie_button = driver.find_element(By.CSS_SELECTOR, 'button[data-cookiebanner="accept_button"]')
        cookie_button.click()
        print("Accepted cookies.")
        time.sleep(1)
    except NoSuchElementException:
        print("Cookie banner not found, continuing.")

    # Find email and password fields and log in
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    
    # Wait for the login process to complete
    time.sleep(5)
    print("Logged in successfully.")


# --- REVISED SCRAPING LOGIC ---
def scrape_comments(driver, post_url):
    """Scrolls, clicks 'more comments' links, and scrapes comments."""
    driver.get(post_url)
    print(f"Navigated to post: {post_url}")
    
    # Wait for the main content to load to ensure the page is ready
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))
        )
        print("Main content loaded.")
    except TimeoutException:
        print("Timed out waiting for page to load. The URL may be incorrect or the page is private.")
        return []

    # --- Click "View more comments" and scroll ---
    # This loop is crucial. It scrolls and clicks any "more comments" links.
    print(f"Scrolling and looking for 'more comments' links...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(SCROLL_COUNT):
        # Click "View more comments" or similar buttons if they exist
        try:
            # Facebook uses different text, so we check for multiple possibilities.
            # This looks for a div with a button role whose text contains "comment"
            more_comments_buttons = driver.find_elements(By.XPATH, "//div[@role='button'][contains(., 'comment')]")
            for button in more_comments_buttons:
                if button.is_displayed():
                    driver.execute_script("arguments[0].click();", button)
                    print("Clicked a 'more comments' button.")
                    time.sleep(2) # Wait for new comments to load

        except Exception as e:
            # This will catch errors if the button is not found or stale
            pass

        # Scroll down to the bottom
        # xb57i2i x1q594ok x5lxg6s x78zum5 xdt5ytf x6ikm8r x1ja2u2z x1pq812k x1rohswg xfk6m8 x1yqm8si xjx87ck xx8ngbg xwo3gff x1n2onr6 x1oyok0e x1odjw0f x1iyjqo2 xy5w88m
        driver.execute_script("window.scrollTo(0, document.body.querySelector('div.xb57i2i.x1q594ok.x5lxg6s.x78zum5.xdt5ytf.x6ikm8r').scrollHeight);")
        print(f"Scroll {i+1}/{SCROLL_COUNT}")
        
        # Wait to load the page
        time.sleep(3)

        # Check if we've reached the bottom of the page
        new_height = driver.execute_script("return document.querySelector('div.xb57i2i.x1q594ok.x5lxg6s.x78zum5.xdt5ytf.x6ikm8r').scrollHeight")
        if new_height == last_height:
            print("Reached the bottom of the comments.")
            break
        last_height = new_height

    # --- Extracting data ---
    comments_data = []
    
    # This is a more robust selector for the entire comment block.
    # It looks for a div that has an ARIA label starting with "Comment by".
    comment_elements = driver.find_elements(By.CSS_SELECTOR, 'div[dir="auto"][style="text-align: start;"] > span.html-span')
    print(f"Found {len(comment_elements)} potential comment elements. Extracting text...")

    for comment in comment_elements:
        try:
            # Within each comment block, we find the text.
            # The selector targets a div with a specific style attribute inside the block.
            text_element = comment.find_element(By.CSS_SELECTOR, 'div[style="text-align: start;"]')
            comment_text = text_element.text.strip()
            print(f"Extracted comment: {comment_text[:50]}...")  # Print first 50 characters for brevity    
            
            if comment_text: # Ensure we don't save empty comments
                comments_data.append({"comment": comment_text})

        except NoSuchElementException:
            # This handles cases where an element matching the main selector isn't a standard comment.
            continue
            
    return comments_data


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if FACEBOOK_EMAIL == "your_facebook_email@example.com" or FACEBOOK_PASSWORD == "your_facebook_password":
        print("!! ERROR: Please update FACEBOOK_EMAIL and FACEBOOK_PASSWORD in the script. !!")
    else:
        driver = setup_driver()
        try:
            login_to_facebook(driver, FACEBOOK_EMAIL, FACEBOOK_PASSWORD)
            scraped_data = scrape_comments(driver, POST_URL)

            if scraped_data:
                # Create a DataFrame and save to CSV
                df = pd.DataFrame(scraped_data)
                df.to_csv("facebook_comments.csv", index=False)
                print(f"\nSuccessfully scraped {len(scraped_data)} comments.")
                print("Data saved to facebook_comments.csv")
            else:
                print("\nNo comments were scraped. This could be due to:")
                print("- The post having no comments.")
                print("- Facebook changing its website structure (CSS selectors need updating).")
                print("- The login failing or being blocked.")

        finally:
            print("Closing the browser.")
            driver.quit()