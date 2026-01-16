import requests
from django.conf import settings

PRODUCT_SERVICE_URL = f"{settings.PRODUCT_SERVICE_URL}/products/"

def get_product_details(product_id):
    """
    Fetches product details from Product Service.
    Returns dict with price, name, stock, etc.
    """
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}/")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None
