from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

ACCESS_TOKENS = {
    "LAVONS88": "token_lavons88_123",
    "LAVONS_WINNIE": "token_winnie_456",
    "LAVONS_XIAOSHAN": "token_xiaoshan_789"
}

EASYSTORE_API_URL = "https://www.don1donshop.com/api/3.0/orders.json"
EASYSTORE_API_TOKEN = os.environ.get("EASYSTORE_API_KEY") or "bf227aac7aec54ea6abd5a78dd82a44a"

def parse_sku_string(raw_sku):
    result = {}
    if not raw_sku:
        return result
    entries = raw_sku.split(",")
    for entry in entries:
        if "*" in entry:
            sku, qty = entry.split("*")
            qty = int(qty)
        else:
            sku, qty = entry, 1
        result[sku] = result.get(sku, 0) + qty
    return result

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/orders", methods=["GET"])
def get_orders():
    referral_code = request.args.get("referral_code")
    access_token = request.args.get("access_token")

    if not referral_code or not access_token:
        return jsonify({"error": "請提供 referral_code 與 access_token"}), 400

    expected_token = ACCESS_TOKENS.get(referral_code.upper())
    if not expected_token or access_token != expected_token:
        return jsonify({"error": "授權失敗，token 不正確"}), 403

    created_at_min = request.args.get("created_at_min") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    created_at_max = request.args.get("created_at_max") or datetime.now().strftime("%Y-%m-%d 23:59:59")

    all_orders = []
    page = 1
    max_pages = 10

    while page <= max_pages:
        params = {
            "limit": 100,
            "page": page,
            "fields": ",".join([
                "id", "order_number", "created_at", "total_price",
                "financial_status", "fulfillment_status", "is_cancelled",
                "referral", "remark", "shipping_fees", "refunds", "line_items", "sku"
            ]),
            "created_at_min": created_at_min,
            "created_at_max": created_at_max
        }
        headers = {
            "EasyStore-Access-Token": EASYSTORE_API_TOKEN,
            "Accept": "application/json"
        }

        response = requests.get(EASYSTORE_API_URL, params=params, headers=headers)
        print(f"📄 Page {page} | 狀態碼: {response.status_code}")

        if response.status_code != 200:
            break

        orders = response.json().get("orders", [])
        all_orders.extend(orders)

        if len(orders) < 100:
            break
        page += 1

    # 🧮 統計單品 SKU 數量
    sku_stats = {}
    for order in all_orders:
        items = []

        if isinstance(order.get("line_items"), list):
            items = order["line_items"]
        elif (
            isinstance(order.get("shipping_fees"), list)
            and isinstance(order["shipping_fees"][0].get("calculation_params", {}).get("profile_items"), list)
        ):
            items = order["shipping_fees"][0]["calculation_params"]["profile_items"]
        elif order.get("sku"):
            items = [{"sku": order["sku"]}]

        for item in items:
            parsed = parse_sku_string(item.get("sku"))
            for sku, qty in parsed.items():
                sku_stats[sku] = sku_stats.get(sku, 0) + qty

    filtered = []
    seen_order_numbers = set()

    for order in all_orders:
        ref = order.get("referral")
        code = ref.get("code") if ref else None

        if code and code.lower() == referral_code.lower():
            order_number = order.get("order_number")
            if order_number in seen_order_numbers:
                continue
            seen_order_numbers.add(order_number)

            shipping_fee = 0.0
            if order.get("shipping_fees"):
                shipping_fee = sum(float(fee.get("price", 0)) for fee in order["shipping_fees"])

            is_refunded = order.get("financial_status") == "refunded"
            refund_amount = 0.0
            if order.get("refunds"):
                refund_amount = sum(float(refund.get("amount", 0)) for refund in order["refunds"])

            filtered.append({
                "order_number": order.get("order_number"),
                "created_at": order.get("created_at"),
                "total_price": order.get("total_price"),
                "financial_status": order.get("financial_status"),
                "fulfillment_status": order.get("fulfillment_status"),
                "is_cancelled": order.get("is_cancelled", False),
                "remark": order.get("remark"),
                "shipping_fee": shipping_fee,
                "is_refunded": is_refunded,
                "refund_amount": refund_amount
            })

    print(f"✅ 符合推薦碼 {referral_code} 的不重複訂單數：{len(filtered)}")
    if not filtered:
        return jsonify({"message": "查無符合的訂單"}), 200

    return jsonify({
        "orders": filtered,
        "sku_stats": sku_stats
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
