from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/orders')
def get_orders():
    referral_code = request.args.get('referral_code')
    access_token = request.args.get('access_token')
    created_at_min = request.args.get('created_at_min')
    created_at_max = request.args.get('created_at_max')

    if not referral_code or not access_token:
        return jsonify({'message': '缺少推薦碼或 access token'}), 400

    url = f"https://api.easystore.co/v1/orders"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    all_orders = []
    page = 1

    while True:
        params = {
            "page": page,
            "limit": 50,
            "referral_code": referral_code,
            "created_at_min": created_at_min,
            "created_at_max": created_at_max
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        print(f"📄 Page {page} | 狀態碼: {response.status_code}")

        if response.status_code != 200 or not data:
            break

        all_orders.extend(data)
        if len(data) < 50:
            break
        page += 1

    return jsonify({"orders": all_orders})
