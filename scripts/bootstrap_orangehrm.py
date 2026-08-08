import sys
import traceback
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from orangehrm.bootstrap.driver import create_driver
from orangehrm.bootstrap.installer_flow import InstallerFlow
from orangehrm.config import BASE_URL


class OrangeHRMBootstrapper:
    def __init__(self):
        self.driver = create_driver()
        self.driver.set_page_load_timeout(15)
        self.wait = WebDriverWait(self.driver, 6)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.driver.quit()

    def is_login_page(self) -> bool:
        return "/auth/login" in self.driver.current_url

    def wait_for_login(self, timeout: int = 120) -> bool:
        import time

        deadline = time.time() + timeout
        while time.time() < deadline:
            current_url = self.driver.current_url
            if "/auth/login" in current_url:
                return True
            if "installer" not in current_url:
                return True
            time.sleep(2)
        return False

    def bootstrap(self):
        installer_flow = InstallerFlow(
            self.driver, base_url=BASE_URL, screenshots_dir=ROOT_DIR / "screenshots"
        )
        installer_flow.installer_page.open_welcome()

        if self.wait_for_login(timeout=3):
            print("OrangeHRM already initialized; login page reachable.")
            return 0

        installer_flow.run()

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
