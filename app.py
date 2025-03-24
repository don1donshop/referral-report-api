from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

ACCESS_TOKENS = {
    "LAVONS88": "token_lavons88_123",
    "LAVONS_WINNIE": "token_winnie_456",
    "LAVONS_XIAOSHAN": "token_xiaoshan_789"
}

EASYSTORE_API_URL = "https://www.don1donshop.com/api/3.0/orders.json"
EASYSTORE_API_KEY = "你的 easystore API 金鑰"  # <<< 要改成環境變數方式，下面會教

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

    params = {
        "limit": 100,
        "fields": "order_number,created_at,total_price,financial_status,fulfillment_status,is_cancelled,referral,remark",
        "created_at_min": created_at_min,
        "created_at_max": created_at_max
    }

    headers = {
        "EasyStore-Access-Token": os.environ.get("EASYSTORE_API_KEY")
    }

    response = requests.get(EASYSTORE_API_URL, params=params, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "無法取得訂單資料"}), 500

    orders = response.json().get("orders", [])
    result = []
    for order in orders:
        ref = order.get("referral")
        if ref and ref.get("code", "").lower() == referral_code.lower():
            result.append({
                "order_number": order.get("order_number"),
                "created_at": order.get("created_at"),
                "total_price": order.get("total_price"),
                "financial_status": order.get("financial_status"),
                "fulfillment_status": order.get("fulfillment_status"),
                "is_cancelled": order.get("is_cancelled", False),
                "remark": order.get("remark")
            })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
