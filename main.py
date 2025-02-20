from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instagram credentials
USERNAME = "ronin.4x"
PASSWORD = "timur20030304"

# Auto-reply messages
AUTO_REPLY_MESSAGES = [
    "Hey there! How can I help you?",
    "Hello! I'm currently unavailable, but I'll get back to you soon.",
    "Thanks for reaching out! Let me know how I can assist you."
]


class InstagramBot:
    def __init__(self):
        # Set up Chrome options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-extensions')
        # Add these options to help with click intercepted issues
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')

        # Initialize driver
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)
        # Maximize window to avoid mobile view issues
        self.driver.maximize_window()

    def login(self):
        """Login to Instagram"""
        try:
            # Navigate to Instagram
            self.driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(4, 6))  # Increased initial wait time

            # Accept cookies if prompted
            try:
                cookie_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]"))
                )
                cookie_button.click()
                time.sleep(random.uniform(1, 2))
            except:
                pass

            # Find and fill username
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(USERNAME)
            time.sleep(random.uniform(0.5, 1.5))

            # Find and fill password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(PASSWORD)
            time.sleep(random.uniform(0.5, 1.5))

            # Click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            time.sleep(random.uniform(5, 7))  # Increased wait time after login

            # Handle various post-login prompts
            self.handle_prompts()

            print("✅ Successfully logged in!")
            return True

        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False

    def handle_prompts(self):
        """Handle various Instagram prompts"""
        prompts = [
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Skip')]",
            "//button[contains(text(), 'Maybe Later')]"
        ]

        for prompt in prompts:
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.XPATH, prompt)))
                button.click()
                time.sleep(random.uniform(1, 2))
            except:
                continue

    def navigate_to_messages(self):
        """Navigate to Instagram Direct Messages with retry mechanism"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Try multiple selectors for the messages button
                selectors = [
                    "//a[contains(@href, '/direct/inbox')]",
                    "//a[@aria-label='Direct messaging']",
                    "//a[contains(@aria-label, 'Direct messaging')]",
                    "//a[contains(@aria-label, 'Messages')]"
                ]

                # Try each selector
                for selector in selectors:
                    try:
                        # Wait for element to be present and visible
                        messages_button = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )

                        # Scroll the button into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", messages_button)
                        time.sleep(1)  # Wait for scroll to complete

                        # Try using JavaScript click if regular click fails
                        try:
                            messages_button.click()
                        except ElementClickInterceptedException:
                            self.driver.execute_script("arguments[0].click();", messages_button)

                        time.sleep(random.uniform(3, 5))
                        return True
                    except:
                        continue

                if attempt < max_attempts - 1:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                    # Refresh the page before retrying
                    self.driver.refresh()
                    time.sleep(3)
                    self.handle_prompts()

            except Exception as e:
                print(f"❌ Navigation attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(2)

        print("❌ Failed to navigate to messages after all attempts")
        return False

    def get_unread_messages(self):
        """Get unread message threads"""
        try:
            # Wait for messages to load
            time.sleep(random.uniform(2, 3))

            # Try different selectors for unread messages
            selectors = [
                "//div[contains(@class, 'unread')]",
                "//div[contains(@aria-label, 'Unread')]",
                "//div[contains(@class, 'x1lliihq')]//span[contains(text(), 'Unread')]/..",
                "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/section/div/div/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div/div"
            ]

            unread_threads = []
            for selector in selectors:
                try:
                    unread_threads = self.driver.find_elements(By.XPATH, selector)
                    if unread_threads:
                        break
                except:
                    continue

            return unread_threads
        except Exception as e:
            print(f"❌ Failed to get unread messages: {str(e)}")
            return []

    def reply_to_message(self, thread):
        """Reply to a specific message thread"""
        try:
            # Click on the thread
            self.driver.execute_script("arguments[0].click();", thread)
            time.sleep(random.uniform(2, 3))

            # Find message input field
            input_selectors = [
                "//textarea[@placeholder='Message...']",
                "//div[@role='textbox']",
                "//textarea[@aria-label='Message...']",
                "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/section/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div[2]/div/div/div[2]"
            ]

            message_input = None
            for selector in input_selectors:
                try:
                    message_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except:
                    continue

            if not message_input:
                raise Exception("Could not find message input field")

            # Type and send message
            reply_text = random.choice(AUTO_REPLY_MESSAGES)
            for char in reply_text:
                message_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))

            time.sleep(random.uniform(0.5, 1))
            message_input.send_keys(Keys.RETURN)
            time.sleep(random.uniform(1, 2))

            return True

        except Exception as e:
            print(f"❌ Failed to reply to message: {str(e)}")
            return False

    def run(self):
        """Main bot loop"""
        if not self.login():
            return

        if not self.navigate_to_messages():
            return

        while True:
            try:
                # Check for unread messages
                unread_threads = self.get_unread_messages()

                if not unread_threads:
                    print("📭 No new messages.")
                else:
                    print(f"📨 Found {len(unread_threads)} unread messages")

                    for thread in unread_threads:
                        if self.reply_to_message(thread):
                            print("✅ Successfully replied to message")

                        # Add random delay between messages
                        time.sleep(random.uniform(30, 60))

                # Wait before checking for new messages again
                time.sleep(random.uniform(60, 120))

            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                # If there's an error, wait a bit longer before trying again
                time.sleep(random.uniform(180, 300))

    def cleanup(self):
        """Clean up resources"""
        try:
            self.driver.quit()
        except:
            pass


if __name__ == "__main__":
    bot = InstagramBot()
    try:
        bot.run()
    finally:
        bot.cleanup()