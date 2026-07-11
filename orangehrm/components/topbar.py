from selenium.webdriver.common.by import By, ByType

from ..pages.base_page import BasePage


class TopbarComponent(BasePage):
    TOPBAR_BODY = (By.CSS_SELECTOR, '')
    # PAGE_TITLE = (By.CSS_SELECTOR, "h6[data-v-7b563373='']")
    PAGE_TITLE = (By.CLASS_NAME, 'oxd-topbar-header-title')
    USER_NAME = (By.CSS_SELECTOR, 'p.oxd-userdropdown-name')
    USER_IMG = (By.CSS_SELECTOR, 'img.oxd-userdropdown-img')
    DROPDOWN_ICON = (By.CSS_SELECTOR, 'i.oxd-userdropdown-icon')
    DROPDOWN_MENU = (By.CSS_SELECTOR, 'ul.oxd-dropdown-menu')
    ABOUT_LINK = (By.CSS_SELECTOR, 'ul.oxd-dropdown-menu li:nth-child(1)')
    # ABOUT_LINK = (By.LINK_TEXT, '#', 'About')
    SUPPORT_LINK = (By.CSS_SELECTOR, 'ul.oxd-dropdown-menu li:nth-child(2)')
    # SUPPORT_LINK = (By.LINK_TEXT, 'href="/web/index.php/help/support"', 'Support')
    CHANGE_PASSWORD = (By.CSS_SELECTOR, 'ul.oxd-dropdown-menu li:nth-child(3)')
    # CHANGE_PASSWORD = (By.LINK_TEXT, '/web/index.php/pim/updatePassword', 'Change Password')
    LOGOUT = (By.CSS_SELECTOR, 'ul.oxd-dropdown-menu li:nth-child(4)')
    # 'Logout', 'href="/web/index.php/auth/logout"'

    def open_dropdown(self):
        self.find


    