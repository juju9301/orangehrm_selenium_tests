from selenium.webdriver.common.by import By

from typing import Literal

from .base_page import BasePage


class InstallerPage(BasePage):
    PATH = "/installer/index.php"
    OPTIONS_CONTAINER = (By.CSS_SELECTOR, "div.oxd-select-dropdown")

    def open_welcome(self):
        self.go_to("/installer/index.php/welcome")
        return self

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
        return self.find_visible(By.XPATH, xpath)

    def find_checkbox_or_radio_by_label(
        self, element_type: Literal["checkbox", "radio"], label_text: str
    ):
        label_lower = label_text.lower()
        xpath = (
            "//label[contains("
            "translate(normalize-space(string(.)), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{label_lower}'"
            ")]//input[@type='" + element_type + "']"
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
