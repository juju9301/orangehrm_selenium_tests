from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.support.ui import WebDriverWait
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

    def click_checkbox(self, text: str):
        normalized_text = text.lower()
        locators = [
            (
                By.XPATH,
                f"//input[@type='checkbox' and ancestor::*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{normalized_text}')]]",
            ),
            (
                By.XPATH,
                f"//*[self::label or self::span or self::div or self::p][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{normalized_text}')]//input[@type='checkbox']",
            ),
            (
                By.XPATH,
                f"//input[@type='checkbox'][following::node()[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{normalized_text}')]]",
            ),
        ]

        for by, locator in locators:
            try:
                checkboxes = WebDriverWait(self.driver, 4).until(
                    lambda driver: [
                        checkbox
                        for checkbox in driver.find_elements(by, locator)
                        if checkbox.is_displayed() and checkbox.is_enabled()
                    ]
                )
            except TimeoutException:
                continue

            if not checkboxes:
                continue

            for checkbox in checkboxes:
                if checkbox.is_displayed() and checkbox.is_enabled():
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    return self

        if self._js_click_by_text(normalized_text):
            return self

        raise TimeoutException(f"Could not find a clickable checkbox for: {text}")

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
        xpath = f"//label[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]/ancestor::div[contains(@class, 'oxd-input-group')]//input"
        return self.find_visible(By.XPATH, xpath)

    # def find_checkbox_or_radio_by_label(
    #     self, element_type: Literal["checkbox", "radio"], label_text: str
    # ):
    #     label_lower = label_text.lower()
    #     # xpath = f"//label[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_lower}')]//input[@type='{element_type}']"
    #     xpath = f"//label[contains(translate(normalize-space(string(.)),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{label_lower}')]//input[@type='{element_type}']"
    #     return self.find_visible(By.XPATH, xpath)

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
        if not element.is_selected():
            label = element.find_element(By.XPATH, "./parent::label")
            label.click()

    def fill_database_fields(self, values: list[str]):
        text_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='text'], input[type='password']"
        )
        for element, value in zip(text_inputs, values):
            element.clear()
            element.send_keys(value)
        return self

    def _js_click_by_text(self, text: str) -> bool:
        script = """
        const target = arguments[0].toLowerCase();
        const candidates = Array.from(document.querySelectorAll('button, input[type=\"submit\"], input[type=\"button\"], input[type=\"checkbox\"], [role=\"checkbox\"], a'));
        for (const element of candidates) {
            const label = (element.innerText || element.value || '').trim().toLowerCase();
            const context = (element.outerHTML + ' ' + (element.parentElement?.innerText || '') + ' ' + (element.closest('label, div, span, p')?.innerText || '')).toLowerCase();
            if (!target || label.includes(target) || context.includes(target)) {
                try {
                    element.click();
                    return true;
                } catch (error) {
                    // Try next candidate.
                }
            }
        }
        return false;
        """
        return bool(self.driver.execute_script(script, text))
