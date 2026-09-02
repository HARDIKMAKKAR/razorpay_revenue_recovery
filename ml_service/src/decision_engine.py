import os
import joblib
import pandas as pd


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "recovery_model.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# ACTIONS
# ============================================================

ACTIONS = [
    "retry",
    "reminder",
    "payment_link",
    "escalate"
]


# ============================================================
# ACTION COST
# ============================================================

ACTION_COST = {
    "retry": 2.0,
    "reminder": 1.0,
    "payment_link": 3.0,
    "escalate": 8.0
}


# ============================================================
# CUSTOMER FRICTION
# ============================================================

ACTION_FRICTION = {
    "retry": 0.02,
    "reminder": 0.05,
    "payment_link": 0.08,
    "escalate": 0.15
}


# ============================================================
# FAILURE-AWARE VALID ACTIONS
# ============================================================

VALID_ACTIONS = {

    "network_error": [
        "retry",
        "reminder",
        "payment_link"
    ],

    "insufficient_funds": [
        "reminder",
        "payment_link"
    ],

    "expired_card": [
        "payment_link",
        "reminder"
    ],

    "authentication_failed": [
        "payment_link",
        "reminder"
    ],

    "limit_exceeded": [
        "reminder",
        "payment_link"
    ],

    "bank_declined": [
        "reminder",
        "payment_link",
        "retry"
    ],

    "mandate_failed": [
        "retry",
        "payment_link",
        "reminder",
        "escalate"
    ]
}


# ============================================================
# REASONS
# ============================================================

ACTION_REASONS = {

    "retry":
        "Failure appears potentially transient, so retrying the payment is appropriate.",

    "reminder":
        "The customer may need to take action before another payment attempt.",

    "payment_link":
        "A payment link gives the customer an alternative way to complete the payment.",

    "escalate":
        "Repeated or complex mandate failures may require manual intervention."
}


# ============================================================
# DECISION FUNCTION
# ============================================================

def recommend_action(payment_data):

    failure_reason = payment_data["failure_reason"]

    amount = float(
        payment_data["amount"]
    )


    # --------------------------------------------------------
    # Determine valid actions
    # --------------------------------------------------------

    valid_actions = VALID_ACTIONS.get(
        failure_reason,
        ACTIONS
    )


    results = []


    # --------------------------------------------------------
    # Score every valid action
    # --------------------------------------------------------

    for action in valid_actions:

        row = payment_data.copy()

        row["action"] = action


        # Convert to DataFrame

        input_df = pd.DataFrame(
            [row]
        )


        # ----------------------------------------------------
        # ML prediction
        # ----------------------------------------------------

        probability = model.predict_proba(
            input_df
        )[0][1]


        # ----------------------------------------------------
        # Economics
        # ----------------------------------------------------

        action_cost = ACTION_COST[action]

        friction = ACTION_FRICTION[action]


        expected_revenue = (
            probability * amount
            - action_cost
            - (
                amount * friction
            )
        )


        results.append({

            "action": action,

            "recovery_probability": round(
                float(probability),
                4
            ),

            "action_cost": action_cost,

            "customer_friction": friction,

            "expected_revenue": round(
                float(expected_revenue),
                2
            )
        })


    # --------------------------------------------------------
    # Select highest expected revenue
    # --------------------------------------------------------

    results.sort(
        key=lambda x: x["expected_revenue"],
        reverse=True
    )


    best = results[0]


    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "failure_reason":
            failure_reason,

        "amount":
            amount,

        "recommended_action":
            best["action"],

        "recovery_probability":
            best["recovery_probability"],

        "expected_revenue":
            best["expected_revenue"],

        "reason":
            ACTION_REASONS[
                best["action"]
            ],

        "alternatives":
            results
    }