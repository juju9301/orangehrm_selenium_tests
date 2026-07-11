import pytest
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By


load_dotenv()

expected_items = [
    (0, "About", "#"),
    (1, "Support", "/web/index.php/help/support"),
    (2, "Change Password", "/web/index.php/pim/updatePassword"),
    (3, "Logout", "/web/index.php/auth/logout"),
]

def test_topbar_visible(dashboard_page):
    topbar = dashboard_page.topbar
    topbar.open_dropdown()
    assert dashboard_page.find(*topbar.USER_NAME).text == os.getenv("ORANGEHRM_FULL_NAME")

@pytest.mark.parametrize('index, expected_text, expected_href', expected_items)
def test_dropdown_elements(dashboard_page, index, expected_text, expected_href):
    topbar = dashboard_page.topbar
    topbar.open_dropdown()
    items = topbar.get_dropdown_items()

    assert len(items) > index

    item = items[index]
    assert item.is_displayed()
    assert item.text.strip() == expected_text

    # Check link href
    link = item.find_element(By.TAG_NAME, "a")
    assert link.get_attribute("href").endswith(expected_href)
