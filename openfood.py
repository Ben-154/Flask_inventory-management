import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BARCODE_URL = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def fetch_by_barcode(barcode):
    """Look up one product by barcode."""
    url = BARCODE_URL.format(barcode=barcode)
    response = requests.get(url, timeout=10, verify=False)
    response.raise_for_status()

    data = response.json()
    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    return {
        "product_name": product.get("product_name", ""),
        "barcode": product.get("code", barcode),
        "brands": product.get("brands", ""),
    }


def search_by_name(name):
    """Search products by name; return a short list."""
    params = {
        "search_terms": name,
        "json": 1,
        "page_size": 5,
    }
    response = requests.get(SEARCH_URL, params=params, timeout=10, verify=False)
    response.raise_for_status()

    data = response.json()
    products = data.get("products", [])

    results = []
    for product in products:
        results.append({
            "product_name": product.get("product_name", ""),
            "barcode": product.get("code", ""),
            "brands": product.get("brands", ""),
        })
    return results