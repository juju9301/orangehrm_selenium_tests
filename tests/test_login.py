import os

import pytest

from orangehrm.components.sidebar import SidebarComponent
from orangehrm.components.topbar import TopbarComponent
from orangehrm.pages.dashboard_page import DashboardPage
from orangehrm.pages.login_page import LoginPage


def test_title(login_page):
    assert login_page.title == "OrangeHRM"


def test_successful_login(login_page, valid_credentials):
    username, password = valid_credentials
    login_page.login(username=username, password=password)

    assert login_page.current_url.endswith("/dashboard/index")


@pytest.mark.parametrize(
    ("username", "password", "expected_visible", "expected_hidden"),
    [
        pytest.param(
            "",
            "",
            [LoginPage.USERNAME_ERROR, LoginPage.PASSWORD_ERROR],
            [],
            id="both missing",
        ),
        pytest.param(
            os.getenv("ORANGEHRM_USERNAME", ""),
            "",
            [LoginPage.PASSWORD_ERROR],
            [LoginPage.USERNAME_ERROR],
            id="password_missing",
        ),
        pytest.param(
            "",
            os.getenv("ORANGEHRM_PASSWORD", ""),
            [LoginPage.USERNAME_ERROR],
            [LoginPage.PASSWORD_ERROR],
            id="username_missing",
        ),
    ],
)
def test_credentials_are_empty(
    login_page, username, password, expected_visible, expected_hidden
):
    login_page.login(username=username, password=password)

    assert login_page.current_url == login_page.url

    for locator in expected_visible:
        assert login_page.is_visible(*locator)

    for locator in expected_hidden:
        assert not login_page.is_visible(*locator)


@pytest.mark.parametrize(
    ("username", "password"),
    [
        pytest.param(
            "random_user123", os.getenv("ORANGEHRM_PASSWORD"), id="wrong_username"
        ),
        pytest.param(
            os.getenv("ORANGEHRM_USERNAME"), "random123%", id="wrong_password"
        ),
    ],
)
def test_credentials_are_incorrect(login_page, username, password):
    login_page.login(username=username, password=password)

    assert login_page.current_url == login_page.url
    assert login_page.find_visible(*login_page.ALERT_SECTION)
    assert login_page.find_visible(*login_page.ALERT_ICON)
    assert login_page.get_text(*login_page.ALERT_MESSAGE) == "Invalid credentials"


def test_redirect_after_logout(login_page, valid_credentials):
    username, password = valid_credentials
    login_page.login(username=username, password=password)
    dashboard = DashboardPage(login_page.driver)
    topbar = TopbarComponent(dashboard.driver)

    topbar.click_option("logout")
    new_url = dashboard.wait_for_url_change(dashboard.url)

    assert new_url.endswith(login_page.PATH)


def test_no_interaction_after_logout(login_page, valid_credentials):
    username, password = valid_credentials
    login_page.login(username=username, password=password)
    dashboard = DashboardPage(login_page.driver)
    topbar = TopbarComponent(dashboard.driver)

    cookie_after_login = login_page.get_cookie("_orangehrm")
    assert cookie_after_login is not None

    topbar.click_option("logout")
    new_url = dashboard.wait_for_url_change(dashboard.url)
    cookie_after_logout = login_page.get_cookie("_orangehrm")

    assert cookie_after_login != cookie_after_logout
    assert new_url == login_page.url

    login_page.back()
    assert login_page.current_url == dashboard.url

    topbar.click_option("support")
    new_url1 = dashboard.wait_for_url_change(dashboard.url)

    assert new_url1 == login_page.url


@pytest.mark.xfail(
    reason="Currently the page clicked in logout state gets saved as next",
    strict=True,
)
def test_redirect_to_dashboard_after_logout_click(login_page, valid_credentials):
    username, password = valid_credentials
    login_page.login(username=username, password=password)
    dashboard = DashboardPage(login_page.driver)
    topbar = TopbarComponent(dashboard.driver)
    sidebar = SidebarComponent(dashboard.driver)

    topbar.click_option("logout")
    new_url = dashboard.wait_for_url_change(dashboard.url)

    assert new_url == login_page.url
    login_page.back()
    assert dashboard.current_url == dashboard.url

    sidebar.click_sidebar_item("Admin")
    new_url = dashboard.wait_for_url_change(dashboard.url)
    assert new_url == login_page.url

    login_page.login(username=username, password=password)

    assert dashboard.current_url == dashboard.url
