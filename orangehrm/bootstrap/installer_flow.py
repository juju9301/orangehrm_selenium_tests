import logging
import os
from pathlib import Path

from orangehrm.pages.installer_page import InstallerPage

logger = logging.getLogger(__name__)


class InstallerFlow:
    def __init__(self, driver, base_url: str, screenshots_dir: Path):
        self.driver = driver
        self.base_url = base_url
        self.screenshots_dir = screenshots_dir
        self.installer_page = InstallerPage(driver, base_url=base_url)

    def run(self) -> None:
        self._prepare_installer()
        self._complete_welcome()
        self._complete_license()
        self._complete_database_config()
        self._complete_system_check()
        self._complete_instance_creation()
        self._complete_admin_creation()
        self._confirm_installation()
        self._complete_installation()
        self._launch_orangehrm()

    def _prepare_installer(self) -> None:
        self.installer_page.open()
        self.installer_page.accept_welcome()

    def _complete_welcome(self) -> None:
        self.installer_page.click_button_by_text("Next")

    def _complete_license(self) -> None:
        self.installer_page.accept_license()
        self.installer_page.click_button_by_text("Next")

    def _complete_database_config(self) -> None:
        self.installer_page.configure_database(
            host=os.getenv("ORANGEHRM_DB_HOST", "mysql"),
            port=os.getenv("ORANGEHRM_DB_PORT", "3306"),
            database_name=os.getenv("MYSQL_DATABASE", "orangehrm"),
            username=os.getenv("MYSQL_ROOT_USERNAME", "root"),
            password=os.getenv("MYSQL_ROOT_PASSWORD", "my-secret-pw"),
        )
        self.installer_page.click_button_by_text("Next")

    def _complete_system_check(self) -> None:
        self.installer_page.wait_for_url_contains(
            "/installer/index.php/installer/system-check"
        )
        self.installer_page.click_button_by_text("Next")

    def _complete_instance_creation(self) -> None:
        self.installer_page.complete_instance_creation()
        self.installer_page.click_button_by_text("Next")

    def _complete_admin_creation(self) -> None:
        self.installer_page.complete_admin_creation()
        self.installer_page.click_button_by_text("Next")

    def _confirm_installation(self) -> None:
        self.installer_page.wait_for_url_contains(
            "/installer/index.php/installer/confirmation"
        )
        self.installer_page.click_button_by_text("Install")

    def _complete_installation(self) -> None:
        self.installer_page.wait_for_installation_and_click_next()

    def _launch_orangehrm(self) -> None:
        self.installer_page.wait_for_url_contains(
            "/installer/index.php/installer/complete"
        )
        self.installer_page.click_button_by_text("Launch OrangeHRM")
