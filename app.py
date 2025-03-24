from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# 🛡️ Access Token 安全驗證機制
ACCESS_TOKENS = {
    "LAVONS88": "token_lavons88_123",
    "LAVONS_WINNIE": "token_winnie_456",
    "LAVONS_XIAOSHAN": "token_xiaoshan_789"
}

# 🛒 EasyStore 訂單 API
EASYSTORE_API_URL = "https://www.don1donshop.com/api/3.0/orders.json"
EASYSTORE_API_TOKEN = os.environ.get("EASYSTORE_API_KEY") or "bf227aac7aec54ea6abd5a78dd82a44a"

# 🔧 API 分頁最大限制
MAX_PAGES = 10  # 最多抓 10 頁，每頁 100 筆，最多 1000 筆
PER_PAGE_LIMIT = 100


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
    for page in range(1, MAX_PAGES + 1):
        params = {
            "limit": PER_PAGE_LIMIT,
            "page": page,
            "fields": "id,order_number,created_at,total_price,financial_status,fulfillment_status,is_cancelled,referral,remark",
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

        if len(orders) < PER_PAGE_LIMIT:
            break  # 已抓完所有資料

    print("🧾 開始列出每筆訂單的 Referral Code：")

    unique_orders = {}  # ✅ 使用 dict 去除重複
    for order in all_orders:
        ref = order.get("referral")
        code = ref.get("code") if ref else "❌ 無推薦碼"
        print(f"📦 訂單：{order.get('order_number', '-')}, Referral Code: {code}")

        if ref and code.lower() == referral_code.lower():
            order_no = order.get("order_number")
            unique_orders[order_no] = {
                "order_number": order_no,
                "created_at": order.get("created_at"),
                "total_price": order.get("total_price"),
                "financial_status": order.get("financial_status"),
                "fulfillment_status": order.get("fulfillment_status"),
                "is_cancelled": order.get("is_cancelled", False),
                "remark": order.get("remark")
            }

    filtered = list(unique_orders.values())

    print(f"✅ 總共符合 {referral_code} 的訂單數：{len(filtered)}")
    print("🟢 Render 版本：已更新 ✅ 分頁 + 去重複")

    if not filtered:
        return jsonify({"message": "查無符合的訂單"}), 200

    return jsonify(filtered)


@app.route("/orders/debug", methods=["GET"])
def debug_referrals():
    created_at_min = request.args.get("created_at_min") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    created_at_max = request.args.get("created_at_max") or datetime.now().strftime("%Y-%m-%d 23:59:59")

    lines = []
    total_orders = 0

    for page in range(1, MAX_PAGES + 1):
        params = {
            "limit": PER_PAGE_LIMIT,
            "page": page,
            "fields": "id,order_number,created_at,referral",
            "created_at_min": created_at_min,
            "created_at_max": created_at_max
        }
        headers = {
            "EasyStore-Access-Token": EASYSTORE_API_TOKEN,
            "Accept": "application/json"
        }

        response = requests.get(EASYSTORE_API_URL, params=params, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": f"API 錯誤 {response.status_code}"}), 500

        orders = response.json().get("orders", [])
        if not orders:
            break

        for order in orders:
            order_no = order.get("order_number", "-")
            referral = order.get("referral")
            code = referral.get("code") if referral else "❌ 無推薦碼"
            lines.append(f"📦 訂單：{order_no}, Referral Code: {code}")
            total_orders += 1

        if len(orders) < PER_PAGE_LIMIT:
            break

    lines.insert(0, f"🔍 共 {total_orders} 筆訂單")
    return Response("\n".join(lines), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
