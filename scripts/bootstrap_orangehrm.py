import os
import sys
import time
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from orangehrm.pages.installer_page import InstallerPage

BASE_URL = os.getenv("ORANGEHRM_URL", "http://localhost:80").rstrip("/")


def chrome_options() -> Options:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    return options


class OrangeHRMBootstrapper:
    def __init__(self):
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options(),
        )
        self.driver.set_page_load_timeout(15)
        self.wait = WebDriverWait(self.driver, 6)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.driver.quit()

    def is_login_page(self) -> bool:
        return "/auth/login" in self.driver.current_url

    def load_page(self, url: str, timeout: int = 60) -> None:
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                self.driver.get(url)
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                return
            except TimeoutException as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(5)

        if last_error is not None:
            raise last_error

    def wait_for_login(self, timeout: int = 120) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_url = self.driver.current_url
            if "/auth/login" in current_url:
                return True
            if "installer" not in current_url:
                return True
            time.sleep(2)
        return False

    def dump_debug_state(self, context: str) -> None:
        try:
            title = self.driver.title or ""
            url = self.driver.current_url or ""
            body_text = self.driver.find_element("tag name", "body").text[:4000]
        except Exception:
            title, url, body_text = "", "", ""

        print(
            f"[bootstrap-debug] {context}\nURL: {url}\nTitle: {title}\nBody: {body_text}",
            file=sys.stderr,
        )

    def complete_database_config(self, installer: InstallerPage):

        db_config_labels = [
            "Database Host Name",
            # "Database Host Port",
            "Database Name",
            "Privileged Database Username",
            "Privileged Database User Password",
            # "OrangeHRM Database Username",  # not filled if same user
            # "OrangeHRM Database User Password",  # not filled if same user
        ]

        db_config_values = [
            os.getenv("ORANGEHRM_DB_HOST", "mysql"),
            # os.getenv("ORANGEHRM_DB_PORT", "3306"),
            os.getenv("MYSQL_DATABASE", "orangehrm"),
            os.getenv("MYSQL_ROOT_USERNAME", "root"),
            os.getenv("MYSQL_ROOT_PASSWORD", "my-secret-pw"),
            # os.getenv("MYSQL_USER", "orangehrm"),
            # os.getenv("MYSQL_PASSWORD", "orangehrm"),
        ]

        self.wait.until(
            EC.url_contains("/installer/index.php/installer/database-config")
        )

        new_database_radio = installer.find_checkbox_or_radio_by_label(
            "radio", "New Database"
        )
        assert new_database_radio.is_selected()

        for label, value in zip(db_config_labels, db_config_values):
            target = installer.find_field_by_label(label)
            target.clear()
            target.send_keys(value)

        same_user_checkbox = installer.find_checkbox_or_radio_by_label(
            "checkbox", "Use the same Database User for OrangeHRM"
        )
        installer.click_checkbox_or_radio(same_user_checkbox)

        installer.click_button_by_text("Next")

    def complete_instance_creation(self, installer: InstallerPage):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/instance-creation")
        )

        org_name = installer.find_field_by_label("Organization Name")
        org_name.send_keys("My Org")

        installer.select_dropdown_option("Country", "Germany")
        installer.select_dropdown_option("Language", "English (United States)")
        installer.select_dropdown_option("Timezone", "Europe/Berlin")
        installer.click_button_by_text("Next")

    def complete_admin_creation(self, installer: InstallerPage):

        self.wait.until(
            EC.url_contains("/installer/index.php/installer/admin-user-creation")
        )

        admin_username = os.getenv("ENABLED_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ENABLED_ADMIN_PASSWORD", "admin123")
        admin_full_name = os.getenv("ENABLED_ADMIN_FULL_NAME", "Admin User")
        admin_email = os.getenv("ENABLED_ADMIN_EMAIL", "admin.user@example.com")

        first_name = installer.find_visible(
            By.CSS_SELECTOR, "input[placeholder='First Name']"
        )
        first_name.send_keys(admin_full_name.split()[0])

        last_name = installer.find_visible(
            By.CSS_SELECTOR, "input[placeholder='Last Name']"
        )
        last_name.send_keys(admin_full_name.split()[1])

        email = installer.find_field_by_label("Email")
        email.clear()
        email.send_keys(admin_email)

        username = installer.find_field_by_label("Admin Username")
        username.clear()
        username.send_keys(admin_username)

        password = installer.find_field_by_label("Password")
        password.clear()

        password.send_keys(admin_password)

        confirm_password = installer.find_field_by_label("Confirm Password")
        confirm_password.clear()
        confirm_password.send_keys(admin_password)

        installer.click_button_by_text("Next")

    def wait_for_installation_and_click_next(
        self, installer: InstallerPage, timeout=600
    ):
        """
        Wait until installation progress reaches 100%,
        then click the [Next] button.
        timeout default = 600 seconds (10 minutes)
        """

        progress_xpath = "//h5[contains(@class,'--progress')]"

        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                progress_el = self.driver.find_element(By.XPATH, progress_xpath)
                text = progress_el.text.strip().replace("%", "")
                percent = int(text)

                if percent >= 100:
                    break

            except Exception:
                # If element temporarily disappears, keep waiting
                pass

            time.sleep(1)

        else:
            raise TimeoutException("Installation did not reach 100% within timeout")

        # Now wait for the Next button to appear
        installer.click_button_by_text("Next")

        return self

    def bootstrap(self):
        installer = InstallerPage(self.driver, base_url=BASE_URL)
        installer.open_welcome()

        # Verify that OrangeHRM wasn't initialized yet
        if self.wait_for_login(timeout=3):
            print("OrangeHRM already initialized; login page reachable.")
            return 0

        """
        Welcome page
        1. Verify "Fresh Installation" option is selected (by default). 
        2. Click [Next]
        """
        self.wait.until(EC.url_contains("/installer/index.php/welcome"))
        fresh_installation = installer.find_checkbox_or_radio_by_label(
            "radio", "Fresh Installation"
        )
        assert fresh_installation.is_selected()
        installer.click_button_by_text("Next")

        """
        Licence Acceptance page
        1. Check checkbox "I accept the terms in the License Agreement"
        2. Verify [Next] button is enabled 
        3. Click [Next]
        """
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/licence-acceptance")
        )
        terms_checkbox = installer.find_checkbox_or_radio_by_label(
            "checkbox", "I accept the terms in the License Agreement"
        )
        if not terms_checkbox.is_selected():
            label = terms_checkbox.find_element(By.XPATH, "./parent::label")
            label.click()
        # installer.click_checkbox("I accept the terms in the License Agreement")
        # assert next button
        installer.click_button_by_text("Next")

        """
        Database configuration
        """

        self.complete_database_config(installer)

        """System Check
        Click [Next]
        """

        self.wait.until(EC.url_contains("/installer/index.php/installer/system-check"))
        installer.click_button_by_text("Next")

        """Instance creation
        1. Fill org name
        2. Country select
        3. Language select
        4. Timezone select
        5. Click [Next]
        """

        self.complete_instance_creation(installer)

        """"""

        self.complete_admin_creation(installer)

        """
        Confirmation
        1. Click [Install]
        """

        self.wait.until(EC.url_contains("/installer/index.php/installer/confirmation"))
        installer.click_button_by_text("Install")

        """
        Installation
        1. Click [Install]
        2. Wait until the installation is complete (can take a considerable time!!! ~3-5 min)
        3. Wait until [Next] button is visible and enabled
        4. Click [Next]
        
        """

        # self.wait.until(EC.url_contains("/installer/index.php/installer/installation"))
        # installer.click_button_by_text("Install")

        self.wait.until(EC.url_contains("/installer/index.php/installer/process"))
        self.wait_for_installation_and_click_next(installer)

        self.wait.until(EC.url_contains("/installer/index.php/installer/complete"))
        installer.click_button_by_text("Launch OrangeHRM")

        if not self.wait_for_login(timeout=180):
            raise RuntimeError(
                "OrangeHRM installer did not reach the login page in time"
            )

        print("OrangeHRM bootstrap completed successfully.")
        return 0


def main() -> int:
    with OrangeHRMBootstrapper() as bootstrapper:
        try:
            return bootstrapper.bootstrap()
        except Exception:
            screenshot_path = ROOT_DIR / "screenshots" / "bootstrap_failure.png"
            try:
                bootstrapper.driver.save_screenshot(str(screenshot_path))
            except Exception:
                pass
            raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        print(f"OrangeHRM bootstrap failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
