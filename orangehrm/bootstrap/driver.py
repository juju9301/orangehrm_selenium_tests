import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


ROOT_DIR = Path(__file__).resolve().parents[2]


def chrome_options() -> Options:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1980,1080")
    if os.getenv("HEADLESS", "0").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    return options


def create_driver() -> webdriver.Chrome:
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options(),
    )
