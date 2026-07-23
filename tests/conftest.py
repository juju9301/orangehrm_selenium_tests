import pytest
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from orangehrm.pages.login_page import LoginPage
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.config import BASE_URL

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def check_orangehrm_is_up():
    # Check if Orangehrm Docker container is running
    url = "http://localhost:80"
    try:
        requests.get(url, timeout=2)
    except Exception:
        pytest.exit(
            "OrangeHRM is not reachable. Docker containers are down", returncode=1
        )


def chrome_options() -> Options:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    return options


@pytest.fixture
def driver():
    # Get browser name from env variables, default to chrome
    browser_name = os.getenv("BROWSER", "chrome").lower().strip()

    if browser_name == "chrome":
        service = ChromeService(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=service, options=chrome_options())

    elif browser_name == "edge":
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver_instance = webdriver.Edge(service=service)

    elif browser_name == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        driver_instance = webdriver.Firefox(service=service)

    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    driver_instance.maximize_window()
    driver_instance.set_page_load_timeout(5)

    yield driver_instance
    driver_instance.quit()


@pytest.fixture
def login_page(driver):
    page = LoginPage(driver, BASE_URL)
    page.open()
    return page


@pytest.fixture
def dashboard_page(login_page):
    login_page.login(
        os.getenv("ENABLED_ADMIN_USERNAME", ""),
        os.getenv("ENABLED_ADMIN_PASSWORD", ""),
    )
    return DashboardPage(login_page.driver, login_page.base_url)


@pytest.fixture
def valid_credentials():
    username = os.getenv("ENABLED_ADMIN_USERNAME")
    password = os.getenv("ENABLED_ADMIN_PASSWORD")

    assert username, "ENABLED_ADMIN_USERNAME is not set"
    assert password, "ENABLED_ADMIN_PASSWORD is not set"

    return username, password
