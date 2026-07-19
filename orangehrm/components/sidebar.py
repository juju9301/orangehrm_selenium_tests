from orangehrm.pages.base_page import BasePage

from selenium.webdriver.common.by import By


class SidebarComponent(BasePage):
    SIDEBAR_NAMES = [
        "Admin",
        "PIM",
        "Leave",
        "Time",
        "Recruitment",
        "My Info",
        "Performance",
        "Dashboard",
        "Directory",
        "Maintenance",
        "Claim",
        "Buzz",
    ]
    SEARCH_FLD = (By.CSS_SELECTOR, 'input[placeholder="Search"]')
    MENU_ITEMS = (By.CSS_SELECTOR, "ul.oxd-main-menu li")

    def get_sidebar_item(self, name: str):
        for item in self.find_all(*self.MENU_ITEMS):
            if item.text.strip() == name:
                return item
        raise ValueError(f"Sidebar item {name} cannot be found")

    def click_sidebar_item(self, name: str):
        item = self.get_sidebar_item(name)
        item.click()
        return item
