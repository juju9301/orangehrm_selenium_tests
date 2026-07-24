import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

ROOT_DIR = Path(__file__).resolve().parents[1]
BASE_URL = os.getenv("ORANGEHRM_URL", "http://localhost:80").rstrip("/")


def chrome_options() -> Options:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return options


class OrangeHRMBootstrapper:
    def __init__(self):
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options(),
        )
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, 20)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.driver.quit()

    def is_login_page(self) -> bool:
        return "/auth/login" in self.driver.current_url

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

    def click_next(self):
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Next']"))
        ).click()

    def click_checkbox(self, text: str):
        checkbox = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//input[@type='checkbox'][ancestor::*[contains(., '{text}')]]",
                )
            )
        )
        self.driver.execute_script("arguments[0].click();", checkbox)

    def fill_field(self, label: str, value: str):
        xpath = (
            f"//*[self::label or self::div or self::span][contains(normalize-space(.), '{label}')]/"
            f"following::input[1]"
        )
        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        element.clear()
        element.send_keys(value)

    def complete_database_config(self):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/database-config")
        )

        text_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='text'], input[type='password']"
        )

        values = [
            os.getenv("ORANGEHRM_DB_HOST", "mysql"),
            os.getenv("ORANGEHRM_DB_PORT", "3306"),
            os.getenv("MYSQL_DATABASE", "orangehrm"),
            os.getenv("MYSQL_ROOT_USERNAME", "root"),
            os.getenv("MYSQL_ROOT_PASSWORD", "my-secret-pw"),
            os.getenv("MYSQL_USER", "orangehrm"),
            os.getenv("MYSQL_PASSWORD", "orangehrm"),
        ]

        for element, value in zip(text_inputs, values):
            element.clear()
            element.send_keys(value)

        same_user_checkbox = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@type='checkbox'][ancestor::*[contains(., 'Use the same Database User for OrangeHRM')]]",
                )
            )
        )
        if not same_user_checkbox.is_selected():
            self.driver.execute_script("arguments[0].click();", same_user_checkbox)

        self.click_next()

    def complete_admin_creation(self):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/admin-user-creation")
        )

        fields = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='text'], input[type='password']"
        )

        admin_username = os.getenv("ENABLED_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ENABLED_ADMIN_PASSWORD", "admin123")
        admin_full_name = os.getenv("ENABLED_ADMIN_FULL_NAME", "Admin User")

        if len(fields) >= 4:
            fields[0].clear()
            fields[0].send_keys(admin_full_name)
            fields[1].clear()
            fields[1].send_keys(admin_username)
            fields[2].clear()
            fields[2].send_keys(admin_password)
            fields[3].clear()
            fields[3].send_keys(admin_password)

        self.click_next()

    def bootstrap(self):
        self.driver.get(f"{BASE_URL}/installer/index.php/welcome")

        if self.wait_for_login(timeout=5):
            print("OrangeHRM already initialized; login page reachable.")
            return 0

        self.wait.until(EC.url_contains("/installer/index.php/welcome"))
        self.click_next()

        self.wait.until(
            EC.url_contains("/installer/index.php/installer/licence-acceptance")
        )
        self.click_checkbox("I accept the terms in the License Agreement")
        self.click_next()

        self.complete_database_config()

        self.wait.until(EC.url_contains("/installer/index.php/installer/system-check"))
        self.click_next()

        self.wait.until(
            EC.url_contains("/installer/index.php/installer/instance-creation")
        )
        self.click_next()

        self.complete_admin_creation()

        self.wait.until(EC.url_contains("/installer/index.php/installer/confirmation"))
        self.click_next()

        self.wait.until(EC.url_contains("/installer/index.php/installer/installation"))

        if not self.wait_for_login(timeout=180):
            raise RuntimeError(
                "OrangeHRM installer did not reach the login page in time"
            )

        print("OrangeHRM bootstrap completed successfully.")
        return 0


def main() -> int:
    with OrangeHRMBootstrapper() as bootstrapper:
        return bootstrapper.bootstrap()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"OrangeHRM bootstrap failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
