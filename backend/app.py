from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import joblib

load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔥 MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["ddos_db"]

blocked_collection = db["blocked_ips"]
logs_collection = db["logs"]
users_collection = db["users"]

model = joblib.load('../ml_model/model.pkl')

latest_data = {}

# 🔐 Default admin (run once)
if not users_collection.find_one({"username": "admin"}):
    users_collection.insert_one({
        "username": "admin",
        "password": "1234",
        "role": "admin"
    })

@app.route('/')
def home():
    return "Server Running ✅"

# 📡 Live data
@app.route('/get-data')
def get_data():
    return jsonify(latest_data)

# 🚨 Detection API (AUTO)
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

        if not blocked_collection.find_one({"ip": ip}):
            blocked_collection.insert_one({"ip": ip})

    else:
        result = "Normal Traffic"
        action = "No Action"

    # 📜 Save logs
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

# 🚫 Blocked IPs
@app.route('/blocked')
def blocked():
    ips = list(blocked_collection.find({}, {"_id": 0}))
    return jsonify({"blocked_ips": ips})

# 📜 Logs
@app.route('/logs')
def logs():
    logs = list(logs_collection.find({}, {"_id": 0}))
    return jsonify({"logs": logs})

# 🔐 Login system
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = users_collection.find_one({
        "username": data['username'],
        "password": data['password']
    })

    if user:
        return jsonify({"status": "success", "role": user['role']})
    else:
        return jsonify({"status": "fail"})

if __name__ == '__main__':
    app.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 5000))
)