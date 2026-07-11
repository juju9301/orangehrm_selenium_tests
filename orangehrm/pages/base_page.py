from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


class BasePage:
    BODY = (By.TAG_NAME, "body")

    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)
    
    """Navigation methods"""
    def go_to(self, path: str = '') -> "BasePage":
        if self.base_url:
            self.driver.get(self.base_url + path)
        else:
            self.driver.get(path)
        return self
    
    """Element finders"""

    def find(self, by: ByType, locator: str):
        """Find element, no wait"""
        return self.driver.find_element(by, locator)
    
    def find_all(self, by: ByType, locator: str):
        """Find multiple elements, no wait"""
        return self.driver.find_elements(by, locator)

    def find_visible(self, by: ByType, locator: str):
        """Wait until element is visible"""
        return self.wait.until(EC.visibility_of_element_located((by, locator)))
    
    def find_all_present(self, by: ByType, locator: str):
        """Wait until all elements are visible"""
        return self.wait.until(EC.presence_of_all_elements_located((by, locator)))
    
    def find_all_visible(self, by: ByType, locator: str):
        return self.wait.until(EC.visibility_of_all_elements_located((by, locator)))

    """Boolean checks"""

    def is_visible(self, by: ByType, locator: str):
        """Returns True if element is visible within timeout"""
        try:
            self.wait.until(EC.visibility_of_element_located((by, locator)))
            return True
        except TimeoutException:
            return False
        
    def is_present(self, by: ByType, locator: str):
        """Returns True if element is present in DOM within timeout"""
        try:
            self.wait.until(EC.presence_of_element_located((by, locator)))
            return True
        except TimeoutException:
            return False
        
    """Wait helpers"""

    def wait_clickable(self, by: ByType, locator: str):
        return self.wait.until(EC.element_to_be_clickable((by, locator)))

    def wait_invisible(self, by: ByType, locator: str):
        return self.wait.until(EC.invisibility_of_element_located((by, locator)))
    
    """Actions"""

    def click(self, by: ByType, locator: str):
        element = self.wait_clickable(by, locator)
        element.click()
        return element #return element for access to it, otherwise it's lost after the action 
    
    def click_elsewhere(self):
        self.find(*self.BODY).click()
    
    def fill(self, by: ByType, locator: str, text: str):
        element = self.find_visible(by, locator)
        element.clear()
        element.send_keys(text)
        return element #return element for access to it, otherwise it's lost after the action 
    
    """Text helpers"""
    def get_text(self, by: ByType, locator: str):
        element = self.find_visible(by, locator)
        return element.text.strip()
    
    """Browser navigation"""

    def refresh(self):
        self.driver.refresh()
        return self
    
    def forward(self):
        self.driver.forward()
        return self
    
    def back(self):
        self.driver.back()
        return self
    
    """Screenshot"""

    def save_screenshot(self, path: str):
        self.driver.save_screenshot(filename=path)
        return path
    
    """Properties"""

    @property
    def current_url(self):
        return self.driver.current_url
    
    @property
    def title(self):
        return self.driver.title

    @property
    def cookies(self):
        return self.driver.get_cookies()




