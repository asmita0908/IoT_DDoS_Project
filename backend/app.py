from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# 🔥 MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["ddos_db"]

blocked_collection = db["blocked_ips"]
logs_collection = db["logs"]

model = joblib.load('../ml_model/model.pkl')

latest_data = {}

@app.route('/')
def home():
    return "Server Running ✅"

# 📡 GET latest data
@app.route('/get-data')
def get_data():
    return jsonify(latest_data)

# 🚨 Detect API
@app.route('/detect', methods=['POST'])
def detect():
    global latest_data

    data = request.json
    ip = request.remote_addr

    requests_list = [d['requests'] for d in data]
    avg_requests = sum(requests_list) / len(requests_list)

    prediction = model.predict([[avg_requests]])

    if prediction[0] == 1:
        result = "DDoS Attack"
        action = "BLOCK IP"

        # 🔥 Save blocked IP (avoid duplicate)
        if not blocked_collection.find_one({"ip": ip}):
            blocked_collection.insert_one({"ip": ip})

    else:
        result = "Normal Traffic"
        action = "No Action"

    # 🔥 Save logs
    logs_collection.insert_one({
        "ip": ip,
        "status": result,
        "requests": avg_requests,
        "devices": data
    })

    latest_data = {
        "status": result,
        "requests": avg_requests,
        "action": action,
        "devices": data
    }

    return jsonify(latest_data)

# 🚫 Get blocked IPs
@app.route('/blocked')
def blocked():
    ips = list(blocked_collection.find({}, {"_id": 0}))
    return jsonify({"blocked_ips": ips})

# 📜 Get logs (Admin panel)
@app.route('/logs')
def logs():
    logs = list(logs_collection.find({}, {"_id": 0}))
    return jsonify({"logs": logs})

if __name__ == '__main__':
    app.run(debug=True)