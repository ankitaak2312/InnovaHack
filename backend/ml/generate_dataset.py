"""
Generates a synthetic dataset of safe and phishing URLs.

There's no real crawled data here — this fabricates structurally
plausible examples so the classifier has *some* signal to learn from
(short/clean/https domains vs long/ip-based/keyword-stuffed ones).
Swap this out for a real labeled dataset (e.g. PhishTank + Tranco) later
without touching train_model.py, since it only depends on the
safe_urls / phishing_urls lists returned here.
"""
import random

random.seed(42)

LEGIT_BRANDS = [
    "google", "github", "amazon", "wikipedia", "microsoft", "apple",
    "netflix", "spotify", "reddit", "stackoverflow", "linkedin", "nytimes",
    "bbc", "cnn", "dropbox", "adobe", "salesforce", "shopify", "notion",
    "figma",
]
LEGIT_TLDS = ["com", "org", "net", "io", "edu", "co.uk", "in"]
LEGIT_PATHS = [
    "", "/", "/about", "/docs", "/login", "/products", "/blog/2024/update",
    "/user/settings", "/search?q=fastapi", "/api/v1/status",
]

PHISHING_BRANDS = [
    "paypal", "amazon", "netflix", "apple", "microsoft", "bankofamerica",
    "chase", "wellsfargo", "facebook", "instagram", "google", "hdfcbank",
    "icicibank", "sbi",
]
PHISHING_KEYWORDS = [
    "login", "verify", "secure", "update", "account", "confirm",
    "signin", "billing", "suspend", "urgent", "reset-password",
]
PHISHING_TLDS = ["tk", "ml", "ga", "cf", "xyz", "top", "info", "click"]
SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd"]


def _random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def generate_safe_urls(n: int) -> list:
    urls = []
    for _ in range(n):
        brand = random.choice(LEGIT_BRANDS)
        tld = random.choice(LEGIT_TLDS)
        path = random.choice(LEGIT_PATHS)
        subdomain = random.choice(["", "www.", "docs.", "app."])
        urls.append(f"https://{subdomain}{brand}.{tld}{path}")
    return urls


def generate_phishing_urls(n: int) -> list:
    urls = []
    for _ in range(n):
        style = random.choice(["ip", "lookalike", "keyword_subdomain", "shortener", "at_symbol"])
        brand = random.choice(PHISHING_BRANDS)
        keyword = random.choice(PHISHING_KEYWORDS)

        if style == "ip":
            urls.append(f"http://{_random_ip()}/{keyword}-{brand}/index.php")
        elif style == "lookalike":
            tld = random.choice(PHISHING_TLDS)
            noise = random.choice(["-secure", "-verify", "-support", "1", "-online"])
            urls.append(f"http://{brand}{noise}.{tld}/{keyword}")
        elif style == "keyword_subdomain":
            tld = random.choice(PHISHING_TLDS)
            urls.append(f"http://{keyword}.{brand}-{keyword}.{tld}/{keyword}.html")
        elif style == "shortener":
            shortener = random.choice(SHORTENERS)
            token = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=7))
            urls.append(f"http://{shortener}/{token}")
        else:  # at_symbol
            tld = random.choice(PHISHING_TLDS)
            urls.append(f"http://{brand}.com@{keyword}-{brand}.{tld}/{keyword}")
        urls.append  # no-op to keep style consistent
    return urls


def build_dataset(n_per_class: int = 600):
    safe = generate_safe_urls(n_per_class)
    phishing = generate_phishing_urls(n_per_class)
    urls = safe + phishing
    labels = [0] * len(safe) + [1] * len(phishing)  # 0 = safe, 1 = phishing
    return urls, labels


if __name__ == "__main__":
    urls, labels = build_dataset(5)
    for u, l in zip(urls, labels):
        print(l, u)
