from typing import Literal
from selenium.webdriver.common.by import By, ByType

from orangehrm.pages.base_page import BasePage

dropdown_option = Literal["about", "support", "change_password", "logout"]


class TopbarComponent(BasePage):
    # TOPBAR_BODY = (By.CSS_SELECTOR, '')
    PAGE_TITLE = (By.CLASS_NAME, "oxd-topbar-header-title")
    USER_NAME = (By.CSS_SELECTOR, "p.oxd-userdropdown-name")
    USER_IMG = (By.CSS_SELECTOR, "img.oxd-userdropdown-img")

    """Dropdown elements"""
    DROPDOWN_ICON = (By.CSS_SELECTOR, "i.oxd-userdropdown-icon")
    DROPDOWN_MENU = (By.CSS_SELECTOR, "ul.oxd-dropdown-menu")
    DROPDOWN_ITEMS = (By.CSS_SELECTOR, "ul.oxd-dropdown-menu li")
    ABOUT_LINK = (By.CSS_SELECTOR, "ul.oxd-dropdown-menu li:nth-child(1)")
    SUPPORT_LINK = (By.CSS_SELECTOR, "ul.oxd-dropdown-menu li:nth-child(2)")
    CHANGE_PASSWORD_LINK = (By.CSS_SELECTOR, "ul.oxd-dropdown-menu li:nth-child(3)")
    LOGOUT_LINK = (By.CSS_SELECTOR, "ul.oxd-dropdown-menu li:nth-child(4)")

    PAGE_TITLE_NAMES = {
        "Admin": "Admin / User Management",
        "PIM": "PIM",
        "Leave": "Leave / Configure",
        "Time": "Time",
        "Recruitment": "Recruitment",
        "My Info": "PIM",
        "Performance": "Performance / Manage Reviews",
        "Dashboard": "Dashboard",
        "Directory": "Directory",
        "Maintenance": "Maintenance / Purge Records",
        "Claim": "Claim",
        "Buzz": "Buzz",
    }

    OPTIONS = {
        "about": ABOUT_LINK,
        "support": SUPPORT_LINK,
        "change_password": CHANGE_PASSWORD_LINK,
        "logout": LOGOUT_LINK,
    }

    def open_dropdown(self):
        self.find_visible(*self.DROPDOWN_ICON).click()
        self.find_visible(*self.DROPDOWN_MENU)
        return self

    def get_dropdown_items(self):
        self.find_visible(*self.DROPDOWN_MENU)
        return [item for item in self.find_all(*self.DROPDOWN_ITEMS)]

    def get_dropdown_text(self):
        return [item.text for item in self.get_dropdown_items()]

    def get_dropdown_hrefs(self):
        return [
            item.find_element(By.TAG_NAME, "a").get_attribute("href")
            for item in self.get_dropdown_items()
        ]

    def click_option(self, option: dropdown_option):
        locator = self.OPTIONS[option]
        self.open_dropdown()
        self.click(*locator)
