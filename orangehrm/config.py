import os
from urllib.parse import urlparse, urlunparse


# def normalize_base_url(url: str) -> str:
#     parsed = urlparse(url if "://" in url else f"http://{url}")
#     scheme = parsed.scheme or "http"
#     hostname = parsed.hostname or "localhost"
#     port = parsed.port

#     if port is None:
#         if scheme == "http":
#             port = 80
#         elif scheme == "https":
#             port = 443

#     netloc = f"{hostname}:{port}"
#     path = parsed.path.rstrip("/")
#     return urlunparse((scheme, netloc, path, "", "", ""))


BASE_URL = os.getenv("ORANGEHRM_URL", "http://localhost:80").rstrip("/")
