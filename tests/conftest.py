import pytest
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

ROOT_DIR = Path(__file__).resolve().parents[1]

from orangehrm.pages.login_page import LoginPage
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.config import BASE_URL

load_dotenv()

@pytest.fixture(scope='session', autouse=True)
def check_orangehrm_is_up():
    # Check if Orangehrm Docker container is running
    url = "http://localhost:80"
    try:
        requests.get(url, timeout=2)
    except Exception:
        pytest.exit("OrangeHRM is not reachable. Docker containers are down", returncode=1)


def chrome_options() -> Options:
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    return options

@pytest.fixture
def browser():
    driver = webdriver.Chrome(service=Service(), options=chrome_options())
    driver.set_page_load_timeout(3)
    yield driver
    driver.quit()

@pytest.fixture
def login_page(browser):
    page = LoginPage(browser, BASE_URL)
    page.open()
    return page

@pytest.fixture
def dashboard_page(login_page):
    login_page.login(os.getenv('ORANGEHRM_USERNAME'), os.getenv('ORANGEHRM_PASSWORD'))
    return DashboardPage(login_page.driver, login_page.base_url)


  
