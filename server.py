from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print(f"\n✅ Received Data for {data.get('Ticker')} ({data.get('Sentiment')})")

    # Example trading logic
    if data.get("Sentiment") in ["Bullish", "Strong Bullish"]:
        print("📈 Placing BUY order...")
    elif data.get("Sentiment") in ["Bearish", "Strong Bearish"]:
        print("📉 Placing SELL order...")
    else:
        print("⏸ Neutral sentiment — no trade triggered.")

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
