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


TRUSTED_BRANDS = [
    "paypal", "amazon", "google", "microsoft", "apple", "netflix",
    "facebook", "instagram", "linkedin", "github", "dropbox", "adobe",
    "bankofamerica", "chase", "wellsfargo", "hdfcbank", "icicibank", "sbi",
]


TWO_PART_SUFFIXES = {"co.uk", "com.au", "co.in", "com.br", "co.jp", "co.nz"}

TYPOSQUAT_MAX_DISTANCE = 2


KNOWN_SAFE_DOMAINS = {
    "gitlab", "airbnb", "telegram", "reddit", "notion", "figma",
    "spotify", "stripe", "slack", "discord", "medium", "twitch",
    "pinterest", "wordpress",
}

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

def levenshtein_distance(a, b):
    """Standard edit-distance DP: minimum single-character insertions,
    deletions, or substitutions to turn `a` into `b`."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev_row = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        curr_row = [i] + [0] * len(b)
        for j, char_b in enumerate(b, start=1):
            cost = 0 if char_a == char_b else 1
            curr_row[j] = min(
                prev_row[j] + 1,        
                curr_row[j - 1] + 1,   
                prev_row[j - 1] + cost  
            )
        prev_row = curr_row
    return prev_row[-1]

def get_domain_label(url):
    """Extract the registrable-domain label (no TLD, no subdomains) from a URL.
    e.g. 'https://www.paypa1-secure.tk/x' -> 'paypa1-secure' """
    hostname = urlparse(url).hostname
    if not hostname:
        return ""
    parts = hostname.lower().split(".")
    if len(parts) < 2:
        return hostname.lower()

    last_two = ".".join(parts[-2:])
    if last_two in TWO_PART_SUFFIXES and len(parts) >= 3:
        return parts[-3]
    return parts[-2]

def check_typosquatting(url):
    """Flag domains that are a small edit distance away from a known trusted
    brand's domain but are NOT an exact or substring match — catching
    character-substitution tricks (e.g. 'paypa1', 'arnazon', 'gogle') that
    plain keyword matching misses because the brand name isn't literally
    present. Checks each hyphen/underscore-separated token individually so
    compound domains like 'paypa1-secure.tk' or 'microsft-support.click'
    are still caught, not just single-word lookalikes."""
    label = get_domain_label(url)
    if not label:
        return None

    tokens = [t for t in re.split(r"[-_0-9]+", label) if t] or [label]
    tokens += [t for t in re.split(r"[-_]+", label) if t]

    for token in tokens:
        if token in KNOWN_SAFE_DOMAINS:
            continue
        for brand in TRUSTED_BRANDS:
            if token == brand or brand in token:
                continue  
            if abs(len(token) - len(brand)) > TYPOSQUAT_MAX_DISTANCE:
                continue  
            distance = levenshtein_distance(token, brand)
            if 0 < distance <= TYPOSQUAT_MAX_DISTANCE:
                return brand
    return None

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

    impersonated_brand = check_typosquatting(url)
    if impersonated_brand:
        flags.append(
            f"Domain closely resembles the trusted brand '{impersonated_brand}' "
            f"(possible typosquatting)"
        )

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
        "http://update-your-account.banking-confirm.xyz",
        "http://paypa1-secure.tk/confirm",
        "http://www.arnazon.com/deals",
        "https://gogle.com",
        "http://microsft-support.click",
    ]

    for test_url in test_urls:
        result = run_heuristics(test_url)
        print(f"\nURL: {test_url}")
        print(f"Flags: {result['flags']}")
        print(f"Heuristic Score: {result['heuristic_score']}")