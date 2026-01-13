import time
import re
import json
from pathlib import Path
import requests

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---

DOWNLOAD_DIRECTORY = r"C:\Users\admin\Documents\ResearchProjectVault\Research Base\Videos"

class TikTokFetcher:
    def __init__(self):
        print("Initializing TikTok Fetcher...")

        # Configure Chrome to mimic real browser
        chrome_options = Options()

        # Anti-detection flags
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(r'--user-data-dir=C:\Users\admin\chrome_tiktok_profile')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Realistic browser profile
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')

        self.driver = webdriver.Chrome(options=chrome_options)

        # Override webdriver detection
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """
        })

        self.video_data = []
        self.download_path = Path(DOWNLOAD_DIRECTORY)
        self.download_path.mkdir(parents=True, exist_ok=True)
        print(f"Videos will be saved to: {self.download_path.resolve()}")

    def load_cookies_and_login(self):
        """Loads and cleans cookies, then pauses for manual CAPTCHA solving."""
        print("Navigating to TikTok to load session cookies...")
        self.driver.get("https://www.tiktok.com/")
        time.sleep(2)

        try:
            with open('cookies.json', 'r') as f:
                cookies = json.load(f)

            # --- COOKIE CLEANING: Fix sameSite errors ---
            for cookie in cookies:
                if 'sameSite' in cookie:
                    if cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                        if cookie['sameSite'].lower() in ["strict", "lax", "none"]:
                            cookie['sameSite'] = cookie['sameSite'].capitalize()
                        else:
                            del cookie['sameSite']
            # --- END COOKIE CLEANING ---

            # Load cookies into browser
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie {cookie.get('name', 'unknown')}: {e}")

            print("Cookies loaded successfully.")

            # --- DIAGNOSTIC: Check cookie domains ---
            loaded_domains = set()
            for cookie in cookies:
                loaded_domains.add(cookie.get('domain', 'unknown'))
            print(f"DEBUG: Cookies loaded for domains: {loaded_domains}")
            # --- END DIAGNOSTIC ---

        except FileNotFoundError:
            print(
                "ERROR: cookies.json not found! Please export your cookies and save the file in the same folder as this script."
            )
            return False

        print("Refreshing page to apply logged-in state...")
        self.driver.refresh()
        time.sleep(3)

        # --- DIAGNOSTIC: Verify login state ---
        print("\n🔍 DEBUG: Testing if cookies resulted in logged-in state...")
        try:
            # Try to find profile button (indicates logged in)
            profile_element = self.driver.find_element(By.XPATH, "//span[@data-e2e='profile-icon']")
            print("✅ DEBUG: Profile icon found - cookies appear VALID (logged in)")
        except:
            print("❌ DEBUG: Profile icon NOT found - cookies may be EXPIRED (logged out)")
            print(f"DEBUG: Current URL: {self.driver.current_url}")
            print(f"DEBUG: Page title: {self.driver.title}")
        # --- END DIAGNOSTIC ---

        print("\n--- HUMAN INTERVENTION REQUIRED ---")
        input(
            "A CAPTCHA may have appeared. Please solve it in the browser window. Once the main page has loaded, press Enter in this terminal to continue..."
        )
        time.sleep(3)
        return True

    def wait_and_click(self, by, value, timeout=20):
        """Waits for an element to be clickable and then clicks it."""
        print(f"Waiting for element: {value}")

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            print("Element found. Clicking...")
            element.click()
            time.sleep(3)  # A brief pause for page transitions
            return True
        except Exception as e:
            print(f"ERROR: Could not find or click element '{value}'. The script cannot continue.")
            return False

    def navigate_to_collection(self):
        """Follows the user-provided full path to the 'References' collection."""
        print("Navigating to your 'References' collection...")

        # --- Using the specific, user-provided XPaths that were successful in testing ---
        profile_button_left_panel_xpath = "//*[@id='app']/div[2]/div/div/div[3]/div[1]/h2[8]/div/a/button/div/div[1]/div/img"
        favorites_tab_xpath = "//*[@id='main-content-others_homepage']/div/div[2]/div[1]/div[1]/p[3]/span"
        collections_button_id = "collections"
        references_collection_xpath = "//*[@id='main-content-others_homepage']/div/div[2]/div[2]/div[2]/div/div/div[1]/div/div/div/a/div/div[1]/div"

        if not self.wait_and_click(By.XPATH, profile_button_left_panel_xpath):
            return False
        if not self.wait_and_click(By.XPATH, favorites_tab_xpath):
            return False
        if not self.wait_and_click(By.ID, collections_button_id):
            return False
        if not self.wait_and_click(By.XPATH, references_collection_xpath):
            return False

        print("Navigation to collection successful. ✅")
        return True

    def harvest_video_data(self):
        """Scrolls the entire collection and harvests data using flexible logic."""
        print("Phase 1: Harvesting all video data. This will take some time...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print("Scrolling...")
        print("Scrolling complete. Harvesting metadata from all video cards...")
        video_card_containers_xpath = "//*[starts-with(@id, 'column-item-video-container-')]"
        cards = self.driver.find_elements(By.XPATH, video_card_containers_xpath)
        for card in cards:
            video_url, username, title = None, "unknown_user", "Untitled Video"
            try:
                username_element = card.find_element(By.XPATH, ".//a[contains(@href, '/@')]")
                username = username_element.text.strip()
                if not username:
                    username = "unknown_user"
                    # Note: Don't log yet - video_url not extracted

                title_area = card.find_element(By.XPATH, ".//div[2]/div")
                try:
                    title_link_element = title_area.find_element(By.XPATH, ".//a")
                    video_url = title_link_element.get_attribute('href')
                    title = title_link_element.text
                except Exception:
                    print(f"⚠️ Could not extract title via primary method, using fallback")
                    main_link_element = card.find_element(By.XPATH, ".//div[1]/div/div[1]/div/a")
                    video_url = main_link_element.get_attribute('href')

                if video_url:
                    # Log metadata issues AFTER URL extracted
                    if username == "unknown_user":
                        print(f"⚠️ Username empty for video: {video_url}")
                    self.video_data.append({"url": video_url, "username": username, "title": title})
            except Exception as e:  # CHANGE C
                print(f"⚠️ Could not process a card: {e}")  # CHANGE C
        unique_videos = {v['url']: v for v in self.video_data}.values()
        self.video_data = list(unique_videos)
        print(f"Harvesting complete. Found {len(self.video_data)} unique videos.")

    def download_videos(self):
        """Loops through harvested data and downloads only new or missing videos."""
        print("Phase 2: Beginning sequential download of all videos...")
        total_videos = len(self.video_data)
        for i, data in enumerate(self.video_data, 1):
            print(f"\n--- Processing video {i}/{total_videos} ---")

            # --- HYBRID NAMING: Human-readable with video ID fallback ---
            safe_username = re.sub(r'[\\/*?:"<>|]', "", data['username'])
            safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title'])[:50].strip()

            # If we successfully extracted real metadata, use human-readable name
            if safe_username != "unknown_user" and safe_title and safe_title != "Untitled Video":
                filename = f"@{safe_username} - {safe_title}.mp4"
            else:
                # Fallback to video ID for failed extractions
                try:
                    video_id = data['url'].split('/video/')[-1].split('?')[0]
                    if not video_id or '/' in video_id:
                        raise ValueError("Invalid video ID")
                    filename = f"tiktok_{video_id}.mp4"
                except (IndexError, ValueError):
                    import hashlib
                    url_hash = hashlib.md5(data['url'].encode()).hexdigest()[:16]
                    filename = f"tiktok_unknown_{url_hash}.mp4"
                    print(f"⚠️ Using fallback filename due to missing metadata")

            filepath = self.download_path / filename
            if filepath.exists():
                print(f"SKIPPING: File already exists at {filepath}")
                continue

            try:  # Download logic exception handler
                del self.driver.requests
                self.driver.get(data['url'])
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/@')]"))
                )
                time.sleep(2)
                video_stream_url = None
                for request in self.driver.requests:
                    if request.response and request.response.headers and 'video/mp4' in request.response.headers.get(
                            'Content-Type', ''
                    ):
                        video_stream_url = request.url
                        break
                if video_stream_url:
                    print(f"Downloading to: {filepath}")
                    selenium_cookies = self.driver.get_cookies()
                    request_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                        'Referer': 'https://www.tiktok.com/'
                    }
                    response = requests.get(
                        video_stream_url, stream=True, timeout=30, cookies=request_cookies, headers=headers
                    )
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=1024 * 1024):
                                f.write(chunk)
                        # --- CHANGE B: File size validation ---
                        file_size = filepath.stat().st_size
                        file_size_mb = file_size / (1024 * 1024)
                        print(f"Download complete. ✅ Size: {file_size_mb:.2f} MB")
                        if file_size == 0:
                            print("⚠️ WARNING: File size is 0 bytes - download failed")
                            filepath.unlink()  # Delete empty file
                        # --- END CHANGE B ---
                    else:
                        print(f"Error downloading: Status code {response.status_code}")
                else:
                    print("FAILURE: Could not find video stream URL for this page.")
            except Exception as e:  # Matches try: on line 33
                print(f"An error occurred while processing {data['url']}: {e}")

    def run(self):
        """Executes the full mission plan."""
        if self.load_cookies_and_login():
            if self.navigate_to_collection():
                self.harvest_video_data()
                self.download_videos()
        print("\n--- Mission Complete ---")
        self.driver.quit()


if __name__ == "__main__":
    fetcher = TikTokFetcher()
    fetcher.run()
