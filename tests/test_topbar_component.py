import pytest

def test_topbar_visible(dashboard_page):
    topbar = dashboard_page.topbar
    assert dashboard_page.find(*topbar.USER_NAME).text == 'Ivan Kovresov'

# @pytest.mark.parametrize('element,num,text,link_text', [
#     (),
#     (),
#     (),
#     ()
# ])
def test_dropdown_elements(dashboard_page):
    topbar = dashboard_page.topbar
    topbar.find(*topbar.DROPDOWN_ICON).click()
    assert topbar.find(*topbar.SUPPORT_LINK).is_displayed()