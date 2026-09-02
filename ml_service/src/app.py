from flask import Flask, request, jsonify
from flask_cors import CORS

from decision_engine import recommend_action


app = Flask(__name__)

CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "revenue-recovery-ml"
    })


@app.route("/recommend", methods=["POST"])
def recommend():

    try:

        payment_data = request.get_json()

        if not payment_data:
            return jsonify({
                "error": "Request body is required"
            }), 400

        result = recommend_action(payment_data)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )