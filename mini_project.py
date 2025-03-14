from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Configuration
TARGET_CONNECTIONS = 100
MAX_CONNECTIONS_PER_RUN = 10
SCROLL_PAUSE = 5
ACTION_DELAY = random.uniform(2, 5)

# Step 1: Set up the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.linkedin.com/login")

# Step 2: Log in to LinkedIn
try:
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys("email")  # Replace with your LinkedIn email
    password.send_keys("pass")   # Replace with your LinkedIn password
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    time.sleep(5)
    print("Logged in successfully.")
except Exception as e:
    print(f"Login failed: {e}")
    print("LinkedIn may have sent a one-time link to your email. Please click the link to log in manually, then press Enter to continue.")
    input("Press Enter after logging in...")
    time.sleep(2)

# Step 3: Search for profiles
try:
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".search-global-typeahead__input"))
    )
    search_box.send_keys("Embedded Software Engineer")
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    print("Search completed.")
except Exception as e:
    print(f"Search failed: {e}")
    driver.quit()
    exit()

# Step 4: Navigate to the "People" tab
try:
    people_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'People')]"))
    )
    people_tab.click()
    print("Navigated to 'People' section successfully.")
    time.sleep(5)
except Exception as e:
    print(f"Error navigating to 'People' section: {e}")
    driver.quit()
    exit()

# Step 5: Send connection requests
connections_sent = 0

try:
    while connections_sent < TARGET_CONNECTIONS:
        # Scroll to load more profiles
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(SCROLL_PAUSE)

        # Find all "Connect" buttons
        connect_buttons = driver.find_elements(By.XPATH, "//button[span[text()='Connect']]")
        print(f"Found {len(connect_buttons)} 'Connect' buttons on this scroll.")

        if not connect_buttons:
            print("No 'Connect' buttons found. Checking for next page...")
            next_page = driver.find_elements(By.XPATH, "//button[@aria-label='Next']")
            if next_page and next_page[0].is_enabled():
                next_page[0].click()
                print("Moved to next page.")
                time.sleep(5)
                continue
            else:
                print("No more pages or buttons available.")
                break

        # Process each "Connect" button
        for i, button in enumerate(connect_buttons):
            if connections_sent >= TARGET_CONNECTIONS:
                break

            try:
                # Scroll to the button and click it
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                print(f"Attempting to click 'Connect' button {i+1}/{len(connect_buttons)}...")
                try:
                    button.click()
                except:
                    driver.execute_script("arguments[0].click();", button)
                time.sleep(ACTION_DELAY)

                # Click the "Send without a note" button in the pop-up
                send_without_note_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Send without a note']]"))
                )
                driver.execute_script("arguments[0].click();", send_without_note_button)  # JS click for reliability
                connections_sent += 1
                print(f"Connection {connections_sent}/{TARGET_CONNECTIONS} sent successfully without a note.")
                time.sleep(ACTION_DELAY)

                # Refresh the list of buttons after each successful send
                connect_buttons = driver.find_elements(By.XPATH, "//button[span[text()='Connect']]")

            except Exception as e:
                print(f"Error with connection attempt {i+1}: {e}")
                # Fallback: Try JS click for both "Connect" and "Send without a note"
                try:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(ACTION_DELAY)
                    send_without_note_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Send without a note']]"))
                    )
                    driver.execute_script("arguments[0].click();", send_without_note_button)
                    connections_sent += 1
                    print(f"Connection {connections_sent}/{TARGET_CONNECTIONS} sent via JS click.")
                    time.sleep(ACTION_DELAY)
                    connect_buttons = driver.find_elements(By.XPATH, "//button[span[text()='Connect']]")
                except Exception as js_error:
                    print(f"JS click or 'Send without a note' failed: {js_error}")
                    continue

        # Pause after a batch to avoid detection
        if connections_sent % MAX_CONNECTIONS_PER_RUN == 0 and connections_sent < TARGET_CONNECTIONS:
            print(f"Pausing for 5 minutes after {connections_sent} connections...")
            time.sleep(30)

except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    print(f"Script completed. Total connections sent: {connections_sent}")
    driver.quit()
