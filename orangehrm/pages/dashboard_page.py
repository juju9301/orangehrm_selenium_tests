from .base_page import BasePage
from ..components.topbar import TopbarComponent


class DashboardPage(BasePage):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.topbar = TopbarComponent(self.driver, self.base_url)
