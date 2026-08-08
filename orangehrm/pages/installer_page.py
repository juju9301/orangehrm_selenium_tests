import os
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Literal

from .base_page import BasePage


class InstallerPage(BasePage):
    PATH = "/installer/index.php"
    OPTIONS_CONTAINER = (By.CSS_SELECTOR, "div.oxd-select-dropdown")

    def open(self):
        return self.open_welcome()

    def open_welcome(self):
        self.go_to("/installer/index.php/welcome")
        return self

    def click_next(self):
        return self.click_button_by_text("Next")

    def accept_welcome(self):
        self.wait.until(EC.url_contains("/installer/index.php/welcome"))
        fresh_installation = self.find_checkbox_or_radio_by_label(
            "radio", "Fresh Installation"
        )
        assert fresh_installation.is_selected()
        return self.click_next()

    def accept_license(self):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/licence-acceptance")
        )
        terms_checkbox = self.find_checkbox_or_radio_by_label(
            "checkbox", "I accept the terms in the License Agreement"
        )
        self.click_checkbox_or_radio(terms_checkbox)
        return self

    def configure_database(
        self, host: str, port: str, database_name: str, username: str, password: str
    ):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/database-config")
        )

        new_database_radio = self.find_checkbox_or_radio_by_label(
            "radio", "New Database"
        )
        assert new_database_radio.is_selected()

        field_values = [
            ("Database Host Name", host),
            ("Database Name", database_name),
            ("Privileged Database Username", username),
            ("Privileged Database User Password", password),
        ]

        for label, value in field_values:
            target = self.find_field_by_label(label)
            target.clear()
            target.send_keys(value)

        same_user_checkbox = self.find_checkbox_or_radio_by_label(
            "checkbox", "Use the same Database User for OrangeHRM"
        )
        self.click_checkbox_or_radio(same_user_checkbox)
        return self

    def complete_instance_creation(self):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/instance-creation")
        )

        org_name = self.find_field_by_label("Organization Name")
        org_name.send_keys("My Org")

        self.select_dropdown_option("Country", "Germany")
        self.select_dropdown_option("Language", "English (United States)")
        self.select_dropdown_option("Timezone", "Europe/Berlin")
        return self

    def complete_admin_creation(self):
        self.wait.until(
            EC.url_contains("/installer/index.php/installer/admin-user-creation")
        )

        admin_username = os.getenv("ENABLED_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ENABLED_ADMIN_PASSWORD", "admin123")
        admin_full_name = os.getenv("ENABLED_ADMIN_FULL_NAME", "Admin User")
        admin_email = os.getenv("ENABLED_ADMIN_EMAIL", "admin.user@example.com")

        first_name = self.find_visible(
            By.CSS_SELECTOR, "input[placeholder='First Name']"
        )
        first_name.send_keys(admin_full_name.split()[0])

        last_name = self.find_visible(By.CSS_SELECTOR, "input[placeholder='Last Name']")
        last_name.send_keys(admin_full_name.split()[1])

        email = self.find_field_by_label("Email")
        email.clear()
        email.send_keys(admin_email)

        username = self.find_field_by_label("Admin Username")
        username.clear()
        username.send_keys(admin_username)

        password = self.find_field_by_label("Password")
        password.clear()
        password.send_keys(admin_password)

        confirm_password = self.find_field_by_label("Confirm Password")
        confirm_password.clear()
        confirm_password.send_keys(admin_password)
        return self

    def wait_for_installation_and_click_next(self, timeout: int = 600):
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
                pass
            time.sleep(1)
        else:
            raise TimeoutException("Installation did not reach 100% within timeout")

        return self.click_next()

    def click_button_by_text(self, button_text: str):
        text_lower = button_text.lower()

        xpath = (
            "("
            # Match <button> elements
            "//button[contains("
            "translate(normalize-space(string(.)), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), "
            f"'{text_lower}'"
            ")]"
            " | "
            # Match <input type='submit'>
            "//input[@type='submit' and contains("
            "translate(normalize-space(@value), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), "
            f"'{text_lower}'"
            ")]"
            ")"
        )

        self.find(By.XPATH, xpath).click()
        return self

    def find_dropdown_trigger_by_label(self, label_text: str):
        label_lower = label_text.lower()
        xpath = (
            "//label[contains("
            "translate(normalize-space(string(.)), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{label_lower}'"
            ")]"
            "/ancestor::div[contains(@class,'oxd-input-group')]"
            "//div[contains(@class,'oxd-select-text')]"
        )
        return self.find_visible(By.XPATH, xpath)

    def select_dropdown_option(self, label_text: str, option_text: str):
        # Click the dropdown trigger
        trigger = self.find_dropdown_trigger_by_label(label_text)
        trigger.click()

        # Wait for dropdown to appear
        options_container = self.find_visible(*self.OPTIONS_CONTAINER)

        # Click the desired option
        option = options_container.find_element(
            By.XPATH, f".//span[normalize-space()='{option_text}']"
        )
        option.click()

    def find_field_by_label(self, label_text: str):
        label_lower = label_text.lower()
        xpath = (
            "//label[contains("
            "translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{label_lower}')]/ancestor::div[contains(@class, 'oxd-input-group')]//input"
        )
        return self.find(By.XPATH, xpath)

    def find_checkbox_or_radio_by_label(
        self, element_type: Literal["checkbox", "radio"], label_text: str
    ):
        label_lower = label_text.lower()
        xpath = (
            "//label[contains("
            "translate(normalize-space(string(.)), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{label_lower}'"
            f")]//input[@type='" + element_type + "']"
        )
        return self.find(By.XPATH, xpath)

    def click_checkbox_or_radio(self, element):
        """The interactable checkbox and radio elements in the UI are being obfuscated,
        therefore we need to click the label of the input instead of the input itself.
        Later consider removing this method and modifying the @find_checkbox_or_radio_by_label instead
        to find the label and interact with it.
        """
        if not element.is_selected():
            label = element.find_element(By.XPATH, "./parent::label")
            label.click()
