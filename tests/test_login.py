from dotenv import load_dotenv
import os

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


