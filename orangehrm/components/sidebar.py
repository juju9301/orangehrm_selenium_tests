from orangehrm.pages.base_page import BasePage
from typing import Literal

from selenium.webdriver.common.by import By


class SidebarComponent(BasePage):
    ADMIN_MENU_ITEMS = (
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
    )

    ESS_MENU_ITEMS = (
        "Leave",
        "Time",
        "My Info",
        "Performance",
        "Dashboard",
        "Directory",
        "Claim",
        "Buzz",
    )
    SEARCH_INPUT_LOCATOR = (By.CSS_SELECTOR, "input[placeholder='Search']")
    MENU_ITEM_LOCATOR = (By.CSS_SELECTOR, "ul.oxd-main-menu li")

    SIDEBAR_TOGGLE_BUTTON_COLLAPSED_LOCATOR = (
        By.XPATH,
        "//button[.//i[contains(@class, 'bi-chevron-right')]]",
    )
    SIDEBAR_TOGGLE_BUTTON_EXPANDED_LOCATOR = (
        By.XPATH,
        "//button[.//i[contains(@class, 'bi-chevron-left')]]",
    )

    def get_menu_item(self, item_name: str):
        for item in self.find_all(*self.MENU_ITEM_LOCATOR):
            if item.text.strip() == item_name:
                return item
        raise ValueError(f"Menu item {item_name} cannot be found")

    def click_menu_item(self, item_name: str):
        item = self.get_menu_item(item_name)
        item.click()
        return item

    def get_menu_items_matching_query(self, query: str, menu: Literal["admin", "ess"]):
        menu_items = self.ADMIN_MENU_ITEMS if menu == "admin" else self.ESS_MENU_ITEMS
        query_text = query.lower()
        matching_names = [name for name in menu_items if query_text in name.lower()]
        return matching_names

    def get_visible_menu_item_names(self):
        return [item.text.strip() for item in self.find_all(*self.MENU_ITEM_LOCATOR)]
