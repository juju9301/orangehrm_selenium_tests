from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class InstallerPage(BasePage):
    PATH = "/installer/index.php"

    NEXT_BUTTONS = [
        (By.XPATH, "//button[normalize-space()='Next']"),
        (
            By.XPATH,
            "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
        ),
        (
            By.XPATH,
            "//input[@type='submit' and contains(translate(normalize-space(@value), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
        ),
    ]

    def open_welcome(self):
        self.go_to("/installer/index.php/welcome")
        return self

    def click_next(self):
        for by, locator in self.NEXT_BUTTONS:
            try:
                self.wait_clickable(by, locator).click()
                return self
            except TimeoutException:
                continue

        if self._js_click_by_text("next"):
            return self

        raise TimeoutException("Could not find a clickable 'Next' button")

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

    def fill_database_fields(self, values: list[str]):
        text_inputs = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='text'], input[type='password']"
        )
        for element, value in zip(text_inputs, values):
            element.clear()
            element.send_keys(value)
        return self

    def fill_admin_fields(self, full_name: str, username: str, password: str):
        fields = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='text'], input[type='password']"
        )
        if len(fields) >= 4:
            fields[0].clear()
            fields[0].send_keys(full_name)
            fields[1].clear()
            fields[1].send_keys(username)
            fields[2].clear()
            fields[2].send_keys(password)
            fields[3].clear()
            fields[3].send_keys(password)
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
