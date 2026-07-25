import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "confirm",
    "banking", "password", "signin", "webscr", "ebayisapi",
    "paypal", "urgent", "suspended", "unlock"
]

IP_PATTERN = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$"
)

def has_ip_address(url):
    hostname = urlparse(url).hostname
    if hostname is None:
        return False
    return bool(IP_PATTERN.match(hostname))

def is_missing_https(url):
    return urlparse(url).scheme != "https"

def has_excessive_subdomains(url, threshold=3):
    hostname = urlparse(url).hostname
    if hostname is None:
        return False
    parts = hostname.split(".")
    return len(parts) > threshold

def has_suspicious_keywords(url):
    lowered = url.lower()
    found = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lowered]
    return found

def run_heuristics(url):
    flags = []

    if has_ip_address(url):
        flags.append("URL uses an IP address instead of a domain name")

    if is_missing_https(url):
        flags.append("URL does not use HTTPS")

    if has_excessive_subdomains(url):
        flags.append("URL has an excessive number of subdomains")

    keywords_found = has_suspicious_keywords(url)
    if keywords_found:
        flags.append(f"URL contains suspicious keywords: {', '.join(keywords_found)}")

    score = len(flags) * 25
    score = min(score, 100)

    return {
        "flags": flags,
        "heuristic_score": score
    }


if __name__ == "__main__":
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login",
        "https://secure-login.paypal-verify-account.com.suspicious.tk",
        "http://update-your-account.banking-confirm.xyz"
    ]

    for test_url in test_urls:
        result = run_heuristics(test_url)
        print(f"\nURL: {test_url}")
        print(f"Flags: {result['flags']}")
        print(f"Heuristic Score: {result['heuristic_score']}")