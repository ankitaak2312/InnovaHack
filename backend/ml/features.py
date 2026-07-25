"""
URL feature extraction shared by the training script (train_model.py) and,
later, the /analyze scoring endpoint (Step 5) so the live API extracts
features exactly the same way the model was trained on.
"""
import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "secure", "account", "banking",
    "confirm", "signin", "webscr", "password", "billing", "suspend",
    "urgent", "alert", "limited", "click", "ebayisapi", "paypal",
]

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "shorte.st", "rebrand.ly",
}

FEATURE_NAMES = [
    "url_length",
    "num_dots",
    "num_hyphens",
    "num_digits",
    "num_subdomains",
    "has_ip_address",
    "has_https",
    "has_at_symbol",
    "num_suspicious_keywords",
    "is_shortened",
    "path_length",
    "num_query_params",
]


def _has_ip_address(hostname: str) -> bool:
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    return bool(re.match(ipv4_pattern, hostname or ""))


def extract_features(url: str) -> list:
    """Return a fixed-length numeric feature vector for a given URL."""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    num_subdomains = max(hostname.count(".") - 1, 0) if hostname else 0
    lowered_url = url.lower()

    features = [
        len(url),
        url.count("."),
        url.count("-"),
        sum(c.isdigit() for c in url),
        num_subdomains,
        int(_has_ip_address(hostname)),
        int(parsed.scheme == "https"),
        int("@" in url),
        sum(kw in lowered_url for kw in SUSPICIOUS_KEYWORDS),
        int(hostname in SHORTENER_DOMAINS),
        len(path),
        query.count("&") + (1 if query else 0),
    ]
    return features


def extract_features_dict(url: str) -> dict:
    return dict(zip(FEATURE_NAMES, extract_features(url)))
