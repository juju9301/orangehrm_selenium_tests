from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    PATH = '/auth/login'
    USERNAME_FLD = (By.NAME, 'username')
    PASSWORD_FLD = (By.NAME, 'password')
    SUBMIT_BTN = (By.CSS_SELECTOR, 'button[type="submit"]')

    def open(self):
        return self.go_to(self.PATH)
    
    def login(self, username: str, password: str):
        self.fill(*self.USERNAME_FLD, text=username)
        self.fill(*self.PASSWORD_FLD, text=password)
        self.click(*self.SUBMIT_BTN)
        return self
    