from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    PATH = "/auth/login"
    USERNAME_FLD = (By.NAME, "username")
    PASSWORD_FLD = (By.NAME, "password")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")

    """Form error elements"""

    USERNAME_ERROR = (
        By.XPATH,
        "//input[@name='username']/ancestor::div[contains(@class, 'oxd-input-group')]//span",
    )
    PASSWORD_ERROR = (
        By.XPATH,
        "//input[@name='password']/ancestor::div[contains(@class, 'oxd-input-group')]//span",
    )
    ERRORS = (By.CSS_SELECTOR, "span.oxd-input-field-error-message")

    ALERT_SECTION = (By.CSS_SELECTOR, "div.orangehrm-login-error")
    ALERT_ICON = (By.CSS_SELECTOR, "i[@data-v-bddebfba='']")
    ALERT_MESSAGE = (By.CSS_SELECTOR, "p.oxd-alert-content-text")

    def open(self):
        return self.go_to(self.PATH)

    def login(self, username: str, password: str):
        self.fill(*self.USERNAME_FLD, text=username)
        self.fill(*self.PASSWORD_FLD, text=password)
        self.click(*self.SUBMIT_BTN)
        return self
