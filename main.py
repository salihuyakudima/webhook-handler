import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Shopify API details
ADMIN_API_ACCESS_TOKEN = os.getenv('SHOPIFY_ADMIN_API_ACCESS_TOKEN')

SHOP_NAME = os.getenv('SHOP_NAME', 'shophurdle')
API_VERSION = os.getenv('SHOPIFY_API_VERSION', '2023-04')  # Replace with the correct API version

# Fez Delivery API details
FEZ_API_SECRET_KEY = os.getenv('FEZ_API_SECRET_KEY', 'tO49mg8EFlKG6ddTXCXVT-cyx9l6fWM2I9JXLhRE6pvz9_DqKgO8DK55jcHzC569')

def get_shopify_orders():
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json"
    headers = {
        "X-Shopify-Access-Token": ADMIN_API_ACCESS_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        app.logger.error(f"Failed to fetch Shopify orders: {response.text}")
        return None

def send_order_to_fez(order):
    url = "https://api.fezdelivery.co/v1/orders"
    headers = {
        "Authorization": f"Bearer {FEZ_API_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=order, headers=headers)
    if response.status_code != 201:
        app.logger.error(f"Failed to send order to Fez: {response.text}")
    return response.status_code, response.text

@app.route('/fetch-and-send-orders', methods=['GET'])
def fetch_and_send_orders():
    orders = get_shopify_orders()
    if orders:
        for order in orders.get('orders', []):
            status_code, response_text = send_order_to_fez(order)
            if status_code != 201:
                return jsonify({"error": response_text}), status_code
        return jsonify({"message": "Orders sent to Fez successfully!"})
    else:
        return jsonify({"error": "Failed to fetch orders from Shopify"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
 