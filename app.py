from flask import Flask, jsonify, request
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

    headers = {
        "EasyStore-Access-Token": EASYSTORE_API_TOKEN,
        "Accept": "application/json"
    }

    # 🌀 自動翻頁抓所有訂單
    page = 1
    all_orders = []

    while True:
        params = {
            "limit": 100,
            "page": page,
            "fields": "id,order_number,created_at,total_price,financial_status,fulfillment_status,is_cancelled,referral,remark",
            "created_at_min": created_at_min,
            "created_at_max": created_at_max
        }

        response = requests.get(EASYSTORE_API_URL, params=params, headers=headers)

        print(f"🔎 Page {page} - 狀態碼: {response.status_code}")
        if response.status_code != 200:
            print("❌ 回應錯誤：", response.text)
            break

        orders = response.json().get("orders", [])
        if not orders:
            break

        all_orders.extend(orders)
        page += 1

    # 🎯 篩選指定推薦碼
    filtered = []
    print("🧾 開始列出每筆訂單的 Referral Code：")
    for order in all_orders:
        ref = order.get("referral")
        code = ref.get("code") if ref else "❌ 無推薦碼"
        print(f"📦 訂單：{order.get('order_number', '-')}, Referral Code: {code}")

        if ref and code.lower() == referral_code.lower():
            filtered.append({
                "order_number": order.get("order_number"),
                "created_at": order.get("created_at"),
                "total_price": order.get("total_price"),
                "financial_status": order.get("financial_status"),
                "fulfillment_status": order.get("fulfillment_status"),
                "is_cancelled": order.get("is_cancelled", False),
                "remark": order.get("remark")
            })

    print(f"✅ 總共符合 {referral_code} 的訂單數：{len(filtered)}")

    if not filtered:
        return jsonify({"message": "查無符合的訂單"}), 200

    return jsonify(filtered)

@app.route("/orders/debug", methods=["GET"])
def debug_referrals():
    from flask import Response

    # 🗓️ 時間區段（跟主 API 一樣）
    created_at_min = request.args.get("created_at_min") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    created_at_max = request.args.get("created_at_max") or datetime.now().strftime("%Y-%m-%d 23:59:59")

    params = {
        "limit": 100,
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
    lines = [f"🔍 共 {len(orders)} 筆訂單"]
    for order in orders:
        order_no = order.get("order_number", "-")
        referral = order.get("referral")
        code = referral.get("code") if referral else "❌ 無推薦碼"
        lines.append(f"📦 訂單：{order_no}, Referral Code: {code}")

    return Response("\n".join(lines), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
