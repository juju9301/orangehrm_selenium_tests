from orangehrm.pages.base_page import BasePage

from selenium.webdriver.common.by import By


class SidebarComponent(BasePage):
    SIDEBAR_NAMES = ['Admin', 'PIM', 'Leave', 'Time', 'Recruitment', 'My Info',
                     'Performance', 'Dashboard', 'Directory', 'Maintenance', 
                     'Claim', 'Buzz']
    SEARCH_FLD = (By.CSS_SELECTOR, 'input[placeholder="Search"]')
    MENU_ITEMS = (By.CSS_SELECTOR, 'ul.oxd-main-menu li')
    SIDEBAR_ITEMS = [(By.CSS_SELECTOR, f'ul.oxd-main-menu li:nth-chaild({n+1})') for n in range(len(SIDEBAR_NAMES))]

    def get_sidebar_item(self, name: str):
        name_index = self.SIDEBAR_NAMES.index(name)
        return self.SIDEBAR_ITEMS[name_index + 1]
