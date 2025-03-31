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

# 單品 SKU 白名單（LAVONS 品項）
LAVONS_SKU_WHITELIST = {
    'LA02-4573', 'LA03-4610', 'LA02-2351', 'LA02-2368', 'LA02-4566',
    'LA03-4603', 'LA02-4580', 'LA03-4627', 'LA02-1514', 'LA02-2863',
    'LA02-0043', 'LA02-2832', 'LA02-0029', 'LA02-9510', 'LA02-9534',
    'LA02-4597', 'LA03-4634', 'LA02-3729', 'LA02-1538', 'LA02-1545',
    'LA02-0173', 'LA02-0418', 'LA02-2399', 'LA02-2405', 'LA02-0098',
    'LA02-3743', 'LA02-1521', 'LA02-0074', 'LA02-2801', 'LA02-0197',
    'LA02-0432', 'LA02-2375', 'LA02-2382'
}

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
                "referral", "remark", "shipping_fees", "refunds", "line_items"
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

    filtered = []
    seen_order_numbers = set()
    sku_stats = {}

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

            line_items = order.get("line_items", [])
            for item in line_items:
                raw_sku = item.get("sku", "")
                quantity = int(item.get("quantity", 0))

                # 拆解 SKU 字串，例如："LA02-4580,LA03-4627*5"
                sku_parts = [sku.strip() for sku in raw_sku.split(",") if sku.strip()]
                for part in sku_parts:
                    if "*" in part:
                        base_sku, qty = part.split("*")
                        base_sku = base_sku.strip()
                        qty = int(qty.strip())
                    else:
                        base_sku = part.strip()
                        qty = 1

                    if base_sku in LAVONS_SKU_WHITELIST:
                        sku_stats[base_sku] = sku_stats.get(base_sku, 0) + qty * quantity

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
    print(f"📦 單品統計：{sku_stats}")

    return jsonify({
        "orders": filtered,
        "sku_stats": sku_stats
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
