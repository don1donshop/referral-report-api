from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# === 初始化 Flask App 與 CORS ===
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# === Logging 設定 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# === 安全 Token ===
ACCESS_TOKENS = {
    # 舊有可保留註解
    # "LAVONS88": "token_lavons88_123",
    # "LAVONS_WINNIE": "token_winnie_456",
    # "LAVONS_XIAOSHAN": "token_xiaoshan_789",
    "LAVONS_XIAOKE": "token_xiaoke_999"  # ✅ 小可的推薦碼
}

# === EasyStore API 設定 ===
EASYSTORE_API_URL = "https://www.don1donshop.com/api/3.0/orders.json"
EASYSTORE_API_TOKEN = os.environ.get("EASYSTORE_API_KEY") or "bf227aac7aec54ea6abd5a78dd82a44a"

# === SKU 對照表 ===
SKU_NAME_MAP = {
    "LA02-4566": "除菌去漬洗衣精（蔚藍海岸）",
    "LA02-4580": "除菌去漬洗衣精（氣泡香檳）",
    "LA02-4573": "除菌去漬洗衣精（法式馬卡龍）",
    "LA02-4597": "除菌去漬洗衣精（無香料）",
    "LA03-4603": "除菌去漬洗衣精補充包（蔚藍海岸）",
    "LA03-4627": "除菌去漬洗衣精補充包（氣泡香檳）",
    "LA03-4610": "除菌去漬洗衣精補充包（法式馬卡龍）",
    "LA03-4634": "除菌去漬洗衣精補充包（無香料）",
    "LA02-0029": "香氛柔軟精（蔚藍海岸）",
    "LA02-0074": "香氛柔軟精補充包（蔚藍海岸）",
    "LA02-1514": "香氛柔軟精（氣泡香檳）",
    "LA02-1521": "香氛柔軟精補充包（氣泡香檳）",
    "LA02-0043": "香氛柔軟精（法式馬卡龍）",
    "LA02-0098": "香氛柔軟精補充包（法式馬卡龍）",
    "LA02-2801": "精緻衣物洗衣精（蔚藍海岸）",
    "LA02-2863": "精緻衣物洗衣精（氣泡香檳）",
    "LA02-2832": "精緻衣物洗衣精（法式馬卡龍）",
    "LA02-0173": "柔氛噴霧（蔚藍海岸）",
    "LA02-1538": "柔氛噴霧（氣泡香檳）",
    "LA02-0197": "柔氛噴霧（法式馬卡龍）",
    "LA02-0418": "柔氛噴霧補充包（蔚藍海岸）",
    "LA02-1545": "柔氛噴霧補充包（氣泡香檳）",
    "LA02-0432": "柔氛噴霧補充包（法式馬卡龍）",
    "LA02-2351": "室內擴香（蔚藍海岸）",
    "LA02-2368": "室內擴香補充包（蔚藍海岸）",
    "LA02-2399": "室內擴香（氣泡香檳）",
    "LA02-2405": "室內擴香補充包（氣泡香檳）",
    "LA02-2375": "室內擴香（法式馬卡龍）",
    "LA02-2382": "室內擴香補充包（法式馬卡龍）",
    "LA02-3729": "To the Moon衣物柔軟精（清鈴恬木）",
    "LA02-9510": "To the Moon衣物柔軟精（澄柑暖木）",
    "LA02-3743": "To the Moon織品噴霧（清鈴恬木）",
    "LA02-9534": "To the Moon織品噴霧（澄柑暖木）",
}

# === 首頁 ===
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# === 統計 SKU 數量 ===
@app.route("/sku_stats", methods=["GET"])
def sku_stats():
    orders_response = get_orders()
    if isinstance(orders_response, tuple):
        return orders_response

    all_data = orders_response.get_json()
    if "message" in all_data:
        return jsonify({"message": "無有效訂單資料"}), 200

    sku_counter = defaultdict(int)

    for order in all_data:
        if order["financial_status"] != "paid" or order["is_cancelled"] or order["is_refunded"]:
            continue

        for item in order.get("line_items", []):
            sku_str = item.get("sku", "")
            if not sku_str:
                continue

            for part in sku_str.split(","):
                if "*" in part:
                    sku, qty = part.split("*")
                    qty = int(qty)
                else:
                    sku = part
                    qty = 1

                if sku in SKU_NAME_MAP:
                    key = f"{SKU_NAME_MAP[sku]} ({sku})"
                    sku_counter[key] += qty
                else:
                    logging.warning(f"❓ 未知 SKU：{sku}")

    return jsonify(dict(sorted(sku_counter.items())))

# === 查詢訂單 ===
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
        logging.info(f"📄 Page {page} | Status Code: {response.status_code}")

        if response.status_code != 200:
            break

        orders = response.json().get("orders", [])
        all_orders.extend(orders)

        if len(orders) < 100:
            break
        page += 1

    filtered = []
    seen_order_numbers = set()

    for order in all_orders:
        ref = order.get("referral")
        code = ref.get("code") if ref else None

        if not code or code.lower() != referral_code.lower():
            continue

        order_number = order.get("order_number")
        if order_number in seen_order_numbers:
            continue
        seen_order_numbers.add(order_number)

        shipping_fee = sum(float(fee.get("price", 0)) for fee in order.get("shipping_fees", []))
        is_refunded = order.get("financial_status") == "refunded"
        refund_amount = sum(float(r.get("amount", 0)) for r in order.get("refunds", []))

        filtered.append({
            "order_number": order_number,
            "created_at": order.get("created_at"),
            "total_price": order.get("total_price"),
            "financial_status": order.get("financial_status"),
            "fulfillment_status": order.get("fulfillment_status"),
            "is_cancelled": order.get("is_cancelled", False),
            "remark": order.get("remark"),
            "shipping_fee": shipping_fee,
            "is_refunded": is_refunded,
            "refund_amount": refund_amount,
            "line_items": [
                {
                    "sku": item.get("sku"),
                    "quantity": item.get("quantity", 1)
                }
                for item in order.get("line_items", [])
            ]

        })

    if not filtered:
        return jsonify({"message": "查無符合的訂單"}), 200
    
    return jsonify(filtered)

# === 啟動應用程式 ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
