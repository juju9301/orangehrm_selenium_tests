from dotenv import load_dotenv
import os
import pytest

from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.components.topbar import TopbarComponent

load_dotenv()

def test_title(login_page):
    title = login_page.title
    assert title == 'OrangeHRM'
    assert 'ange' in title
    assert title.endswith('HRM')

def test_successful_login(login_page):
    login_page.login(
        username=os.getenv('ORANGEHRM_USERNAME'), 
        password=os.getenv('ORANGEHRM_PASSWORD')
        )
    assert login_page.current_url.endswith('/dashboard/index')

@pytest.mark.parametrize('username, password', [
    ('random_user123', os.getenv('ORANGEHRM_PASSWORD')),
    (os.getenv('ORANGEHRM_USERNAME'), 'random123%')
])
def test_credentials_are_incorrect(login_page, username, password):
    login_page.login(
        username=username, 
        password=password
        )
    assert login_page.current_url == login_page.url
    assert login_page.find_visible(*login_page.ALERT_SECTION)
    assert login_page.find_visible(*login_page.ALERT_ICON)
    assert login_page.get_text(*login_page.ALERT_MESSAGE) == 'Invalid credentials'

def test_redirect_after_logout(login_page):
    login_page.login(
        username=os.getenv('ORANGEHRM_USERNAME'), 
        password=os.getenv('ORANGEHRM_PASSWORD')
    )
    dashboard = DashboardPage(login_page.driver)
    topbar = TopbarComponent(dashboard.driver)
    topbar.click_option('logout')
    new_url = dashboard.wait_for_url_change(dashboard.url)
    assert new_url.endswith(login_page.PATH)
