import os


BASE_URL = os.getenv("ORANGEHRM_URL", "http://localhost:80").rstrip("/")
