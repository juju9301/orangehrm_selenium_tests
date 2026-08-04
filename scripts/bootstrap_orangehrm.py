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
from webdriver_manager.chrome import ChromeDriverManager

from orangehrm.pages.installer_page import InstallerPage

ROOT_DIR = Path(__file__).resolve().parents[1]
BASE_URL = os.getenv("ORANGEHRM_URL", "http://localhost:80").rstrip("/")


def chrome_options() -> Options:
    options = Options()
    # options.add_argument("--headless=new")
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
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/database-config")
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

        installer.fill_database_fields(values)
        installer.click_checkbox("Use the same Database User for OrangeHRM")
        installer.click_next()

    def complete_admin_creation(self, installer: InstallerPage):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/admin-user-creation")
        )

        admin_username = os.getenv("ENABLED_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ENABLED_ADMIN_PASSWORD", "admin123")
        admin_full_name = os.getenv("ENABLED_ADMIN_FULL_NAME", "Admin User")

        installer.fill_admin_fields(admin_full_name, admin_username, admin_password)
        installer.click_next()

    def bootstrap(self):
        installer = InstallerPage(self.driver, base_url=BASE_URL)
        installer.open_welcome()

        if self.wait_for_login(timeout=5):
            print("OrangeHRM already initialized; login page reachable.")
            return 0

        self.wait.until(EC.url_contains("/installer/index.php/welcome"))
        installer.click_next()

        self.wait.until(
            EC.url_contains("/installer/index.php/installer/licence-acceptance")
        )
        installer.click_checkbox("I accept the terms in the License Agreement")
        installer.click_next()

        self.complete_database_config(installer)

        self.wait.until(EC.url_contains("/installer/index.php/installer/system-check"))
        installer.click_next()

        self.wait.until(
            EC.url_contains("/installer/index.php/installer/instance-creation")
        )
        installer.click_next()

        self.complete_admin_creation(installer)

        self.wait.until(EC.url_contains("/installer/index.php/installer/confirmation"))
        installer.click_next()

        self.wait.until(EC.url_contains("/installer/index.php/installer/installation"))

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
