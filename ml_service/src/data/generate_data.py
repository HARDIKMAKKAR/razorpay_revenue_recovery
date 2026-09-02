import os
import numpy as np
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

SEED = 42

N_CUSTOMERS = 20_000
N_TRANSACTIONS = 100_000

np.random.seed(SEED)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

os.makedirs(RAW_DIR, exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# ============================================================
# 1. CUSTOMERS
# ============================================================

print("Generating customers...")

customer_ids = np.array([
    f"CUST_{i:06d}"
    for i in range(1, N_CUSTOMERS + 1)
])

customer_tenure_days = np.random.randint(
    1, 2000, N_CUSTOMERS
)

total_transactions = np.random.randint(
    3, 100, N_CUSTOMERS
)

historical_success_rate = np.clip(
    np.random.beta(8, 2, N_CUSTOMERS),
    0.40,
    0.99
)

successful_transactions = (
    total_transactions * historical_success_rate
).astype(int)

failed_transactions = (
    total_transactions - successful_transactions
)

avg_transaction_amount = np.round(
    np.random.lognormal(
        mean=np.log(1500),
        sigma=0.8,
        size=N_CUSTOMERS
    ),
    2
)

days_since_last_success = np.random.randint(
    0, 90, N_CUSTOMERS
)

customer_segment = np.random.choice(
    [
        "regular",
        "new",
        "high_value",
        "churn_risk"
    ],
    size=N_CUSTOMERS,
    p=[
        0.50,
        0.20,
        0.15,
        0.15
    ]
)


# Make segment behavior meaningful
high_value_mask = customer_segment == "high_value"
new_mask = customer_segment == "new"
churn_mask = customer_segment == "churn_risk"

avg_transaction_amount[high_value_mask] *= np.random.uniform(
    2.5, 5.0, high_value_mask.sum()
)

historical_success_rate[churn_mask] = np.clip(
    historical_success_rate[churn_mask] - np.random.uniform(
        0.15, 0.30, churn_mask.sum()
    ),
    0.40,
    0.85
)

historical_success_rate[new_mask] = np.clip(
    historical_success_rate[new_mask] - np.random.uniform(
        0.02, 0.08, new_mask.sum()
    ),
    0.40,
    0.95
)


customers = pd.DataFrame({
    "customer_id": customer_ids,
    "customer_tenure_days": customer_tenure_days,
    "total_transactions": total_transactions,
    "successful_transactions": successful_transactions,
    "failed_transactions": failed_transactions,
    "historical_success_rate": historical_success_rate,
    "avg_transaction_amount": avg_transaction_amount,
    "days_since_last_success": days_since_last_success,
    "customer_segment": customer_segment
})

customers_path = os.path.join(
    RAW_DIR,
    "customers.csv"
)

customers.to_csv(
    customers_path,
    index=False
)

print(f"Customers generated: {len(customers):,}")


# ============================================================
# CUSTOMER LOOKUPS
# ============================================================

customer_success_map = dict(
    zip(
        customer_ids,
        historical_success_rate
    )
)

customer_avg_amount_map = dict(
    zip(
        customer_ids,
        avg_transaction_amount
    )
)

# ============================================================
# 2. TRANSACTIONS
# ============================================================

print("Generating transactions...")

transaction_ids = np.array([
    f"TXN_{i:07d}"
    for i in range(1, N_TRANSACTIONS + 1)
])

transaction_customer_ids = np.random.choice(
    customer_ids,
    N_TRANSACTIONS
)

transaction_success_rates = np.array([
    customer_success_map[cid]
    for cid in transaction_customer_ids
])

transaction_avg_amounts = np.array([
    customer_avg_amount_map[cid]
    for cid in transaction_customer_ids
])


# ============================================================
# AMOUNT
# ============================================================

amounts = np.random.lognormal(
    mean=np.log(
        np.maximum(
            transaction_avg_amounts,
            100
        )
    ),
    sigma=0.30
)

amounts = np.round(amounts, 2)


# ============================================================
# PAYMENT METHOD
# ============================================================

payment_methods = np.random.choice(
    [
        "card",
        "UPI",
        "netbanking",
        "wallet"
    ],
    N_TRANSACTIONS,
    p=[
        0.35,
        0.40,
        0.20,
        0.05
    ]
)


# ============================================================
# PAYMENT GATEWAY
# ============================================================

payment_gateways = np.random.choice(
    [
        "Razorpay",
        "Stripe",
        "PayU"
    ],
    N_TRANSACTIONS,
    p=[
        0.75,
        0.15,
        0.10
    ]
)


# ============================================================
# RECURRING
# ============================================================

is_recurring = np.random.choice(
    [0, 1],
    N_TRANSACTIONS,
    p=[0.30, 0.70]
)


# ============================================================
# ATTEMPT NUMBER
# ============================================================

attempt_number = np.random.choice(
    [1, 2, 3],
    N_TRANSACTIONS,
    p=[0.80, 0.15, 0.05]
)


# ============================================================
# MERCHANT
# ============================================================

merchant_ids = np.random.choice(
    [
        "MERCHANT_001",
        "MERCHANT_002",
        "MERCHANT_003",
        "MERCHANT_004",
        "MERCHANT_005"
    ],
    N_TRANSACTIONS
)


# ============================================================
# FAILURE
# ============================================================

failure_reasons = [
    "insufficient_funds",
    "bank_declined",
    "expired_card",
    "authentication_failed",
    "network_error",
    "limit_exceeded",
    "mandate_failed"
]

failure_probabilities = [
    0.25,
    0.20,
    0.10,
    0.12,
    0.13,
    0.08,
    0.12
]


failure_probability = (
    0.08
    + (1 - transaction_success_rates) * 0.25
    + (attempt_number - 1) * 0.05
)

failure_probability = np.clip(
    failure_probability,
    0.03,
    0.50
)

failed_mask = (
    np.random.random(N_TRANSACTIONS)
    < failure_probability
)

failure_reason_list = np.full(
    N_TRANSACTIONS,
    "none",
    dtype=object
)

failure_reason_list[failed_mask] = np.random.choice(
    failure_reasons,
    size=failed_mask.sum(),
    p=failure_probabilities
)


# ============================================================
# FAILURE CODES
# ============================================================

failure_code_map = {
    "insufficient_funds": "INSUFFICIENT_FUNDS",
    "bank_declined": "BANK_DECLINED",
    "expired_card": "EXPIRED_CARD",
    "authentication_failed": "AUTH_FAILED",
    "network_error": "NETWORK_ERROR",
    "limit_exceeded": "LIMIT_EXCEEDED",
    "mandate_failed": "MANDATE_FAILED",
    "none": None
}

failure_codes = np.array([
    failure_code_map[x]
    for x in failure_reason_list
], dtype=object)


# ============================================================
# TIMESTAMPS
# ============================================================

timestamps = pd.date_range(
    end=pd.Timestamp.now(),
    periods=N_TRANSACTIONS,
    freq="min"
)

timestamps = np.random.choice(
    timestamps,
    N_TRANSACTIONS,
    replace=False
)


# ============================================================
# SUBSCRIPTIONS
# ============================================================

subscription_ids = np.array(
    [
        f"SUB_{np.random.randint(1, 30000):06d}"
        if recurring == 1
        else None
        for recurring in is_recurring
    ],
    dtype=object
)


# ============================================================
# TRANSACTION DATAFRAME
# ============================================================

transactions = pd.DataFrame({

    "transaction_id":
        transaction_ids,

    "customer_id":
        transaction_customer_ids,

    "merchant_id":
        merchant_ids,

    "subscription_id":
        subscription_ids,

    "amount":
        amounts,

    "currency":
        "INR",

    "payment_method":
        payment_methods,

    "payment_gateway":
        payment_gateways,

    "transaction_timestamp":
        timestamps,

    "failure_reason":
        failure_reason_list,

    "failure_code":
        failure_codes,

    "is_recurring":
        is_recurring,

    "attempt_number":
        attempt_number
})


transactions_path = os.path.join(
    RAW_DIR,
    "transactions.csv"
)

transactions.to_csv(
    transactions_path,
    index=False
)

print(
    f"Transactions generated: "
    f"{len(transactions):,}"
)


# ============================================================
# 3. FAILED TRANSACTIONS
# ============================================================

print(
    "\nGenerating action-level recovery dataset..."
)

failed_transactions = transactions[
    transactions["failure_reason"] != "none"
].copy()

failed_transactions = failed_transactions.merge(
    customers,
    on="customer_id",
    how="left"
)

print(
    f"Failed transactions: "
    f"{len(failed_transactions):,}"
)


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
# FAILURE × ACTION EFFECT
#
# Stronger relationships than previous version.
# ============================================================

ACTION_EFFECT = {

    "insufficient_funds": {

        "retry": -1.00,

        "reminder": 0.80,

        "payment_link": 0.50,

        "escalate": -0.70
    },

    "bank_declined": {

        "retry": -0.45,

        "reminder": 0.30,

        "payment_link": 0.60,

        "escalate": 0.10
    },

    "expired_card": {

        "retry": -1.20,

        "reminder": 0.10,

        "payment_link": 1.00,

        "escalate": -0.10
    },

    "authentication_failed": {

        "retry": -0.90,

        "reminder": 0.30,

        "payment_link": 0.90,

        "escalate": 0.00
    },

    "network_error": {

        "retry": 1.20,

        "reminder": -0.20,

        "payment_link": -0.30,

        "escalate": -0.80
    },

    "limit_exceeded": {

        "retry": -0.80,

        "reminder": 0.40,

        "payment_link": 0.90,

        "escalate": -0.10
    },

    "mandate_failed": {

        "retry": 0.60,

        "reminder": 0.20,

        "payment_link": 0.80,

        "escalate": 0.40
    }
}


# ============================================================
# BASE FAILURE EFFECT
# ============================================================

FAILURE_BASE_EFFECT = {

    "insufficient_funds": -0.25,

    "bank_declined": -0.15,

    "expired_card": -0.20,

    "authentication_failed": -0.20,

    "network_error": 0.45,

    "limit_exceeded": 0.00,

    "mandate_failed": -0.15
}


# ============================================================
# 4. GENERATE ACTION DATA
# ============================================================

records = []


for _, row in failed_transactions.iterrows():

    # --------------------------------------------------------
    # CUSTOMER BASE SCORE
    # --------------------------------------------------------

    base_score = (
        -0.80
        + 3.0 * row["historical_success_rate"]
    )


    # --------------------------------------------------------
    # TENURE
    # --------------------------------------------------------

    if row["customer_tenure_days"] > 365:

        base_score += 0.25

    elif row["customer_tenure_days"] < 30:

        base_score -= 0.15


    # --------------------------------------------------------
    # CUSTOMER SEGMENT
    # --------------------------------------------------------

    if row["customer_segment"] == "high_value":

        base_score += 0.25

    elif row["customer_segment"] == "new":

        base_score -= 0.10

    elif row["customer_segment"] == "churn_risk":

        base_score -= 0.45


    # --------------------------------------------------------
    # FAILURE TYPE
    # --------------------------------------------------------

    base_score += FAILURE_BASE_EFFECT[
        row["failure_reason"]
    ]


    # --------------------------------------------------------
    # ATTEMPTS
    # --------------------------------------------------------

    base_score -= (
        0.30 *
        (row["attempt_number"] - 1)
    )


    # ========================================================
    # EVERY POSSIBLE ACTION
    # ========================================================

    for action in ACTIONS:

        score = (
            base_score
            + ACTION_EFFECT[
                row["failure_reason"]
            ][action]
        )


        # ----------------------------------------------------
        # PAYMENT METHOD × ACTION INTERACTION
        # ----------------------------------------------------

        if (
            row["payment_method"] == "UPI"
            and action == "retry"
        ):
            score += 0.25

        if (
            row["payment_method"] == "card"
            and action == "payment_link"
        ):
            score += 0.20

        if (
            row["payment_method"] == "netbanking"
            and action == "payment_link"
        ):
            score += 0.15


        # ----------------------------------------------------
        # RECURRING PAYMENT
        # ----------------------------------------------------

        if row["is_recurring"] == 1:

            score += 0.15


        # ----------------------------------------------------
        # HIGH VALUE CUSTOMER
        # ----------------------------------------------------

        if (
            row["customer_segment"] == "high_value"
            and action in [
                "payment_link",
                "reminder"
            ]
        ):

            score += 0.15


        # ----------------------------------------------------
        # VERY LARGE TRANSACTION
        # ----------------------------------------------------

        if row["amount"] > 10000:

            if action == "reminder":

                score += 0.20

            elif action == "escalate":

                score += 0.15


        # ----------------------------------------------------
        # DAYS SINCE SUCCESS
        # ----------------------------------------------------

        if row["days_since_last_success"] > 45:

            score -= 0.15


        # ----------------------------------------------------
        # ACTION-SPECIFIC TIMING
        # ----------------------------------------------------

        if action == "retry":

            if row["failure_reason"] == "network_error":

                retry_delay = np.random.choice(
                    [0.1, 0.5, 1, 2]
                )

            else:

                retry_delay = np.random.choice(
                    [2, 6, 12, 24]
                )

        elif action == "reminder":

            retry_delay = np.random.choice(
                [6, 12, 24]
            )

        elif action == "payment_link":

            retry_delay = np.random.choice(
                [1, 6, 12]
            )

        else:

            retry_delay = np.random.choice(
                [12, 24, 48]
            )


        # ----------------------------------------------------
        # TIMING EFFECT
        # ----------------------------------------------------

        if (
            action == "retry"
            and row["failure_reason"] == "network_error"
            and retry_delay <= 1
        ):

            score += 0.20


        # ----------------------------------------------------
        # PROBABILITY
        # ----------------------------------------------------

        probability = sigmoid(score)

        probability = np.clip(
            probability,
            0.05,
            0.95
        )


        # ----------------------------------------------------
        # REALISTIC RANDOMNESS
        # ----------------------------------------------------

        probability += np.random.normal(
            0,
            0.015
        )

        probability = np.clip(
            probability,
            0.03,
            0.97
        )


        # ----------------------------------------------------
        # OUTCOME
        # ----------------------------------------------------

        recovered = np.random.binomial(
            1,
            probability
        )


        # ----------------------------------------------------
        # CHANNEL
        # ----------------------------------------------------

        if action == "retry":

            channel = "system"

        else:

            channel = np.random.choice(
                [
                    "email",
                    "sms",
                    "whatsapp",
                    "push"
                ]
            )


        # ----------------------------------------------------
        # RECOVERY TIME
        # ----------------------------------------------------

        if recovered:

            recovery_time = round(
                np.random.exponential(
                    scale=max(
                        retry_delay,
                        1
                    )
                ),
                2
            )

            recovered_amount = row["amount"]

        else:

            recovery_time = None

            recovered_amount = 0


        # ----------------------------------------------------
        # STORE RECORD
        # ----------------------------------------------------

        records.append({

            "transaction_id":
                row["transaction_id"],

            "customer_id":
                row["customer_id"],

            "merchant_id":
                row["merchant_id"],

            "subscription_id":
                row["subscription_id"],

            "amount":
                row["amount"],

            "currency":
                row["currency"],

            "payment_method":
                row["payment_method"],

            "payment_gateway":
                row["payment_gateway"],

            "transaction_timestamp":
                row["transaction_timestamp"],

            "failure_reason":
                row["failure_reason"],

            "failure_code":
                row["failure_code"],

            "is_recurring":
                row["is_recurring"],

            "attempt_number":
                row["attempt_number"],

            "customer_tenure_days":
                row["customer_tenure_days"],

            "total_transactions":
                row["total_transactions"],

            "successful_transactions":
                row["successful_transactions"],

            "failed_transactions":
                row["failed_transactions"],

            "historical_success_rate":
                row["historical_success_rate"],

            "avg_transaction_amount":
                row["avg_transaction_amount"],

            "days_since_last_success":
                row["days_since_last_success"],

            "customer_segment":
                row["customer_segment"],

            "action":
                action,

            "channel":
                channel,

            "retry_delay_hours":
                retry_delay,

            "recovery_probability":
                probability,

            "recovered":
                recovered,

            "recovery_time_hours":
                recovery_time,

            "recovered_amount":
                recovered_amount,

            "action_cost":
                ACTION_COST[action],

            "customer_friction":
                ACTION_FRICTION[action]
        })


# ============================================================
# 5. CREATE DATAFRAME
# ============================================================

recovery_dataset = pd.DataFrame(
    records
)


# ============================================================
# 6. SAVE
# ============================================================

recovery_dataset_path = os.path.join(
    RAW_DIR,
    "recovery_action_dataset.csv"
)

recovery_dataset.to_csv(
    recovery_dataset_path,
    index=False
)


# ============================================================
# 7. REPORT
# ============================================================

print("\n")
print("==============================================")
print("DATA GENERATION COMPLETE")
print("==============================================")


print(
    f"Customers: "
    f"{len(customers):,}"
)

print(
    f"Transactions: "
    f"{len(transactions):,}"
)

print(
    f"Failed transactions: "
    f"{len(failed_transactions):,}"
)

print(
    f"Action training rows: "
    f"{len(recovery_dataset):,}"
)


print("\nCustomer segments:")

print(
    customers[
        "customer_segment"
    ].value_counts()
)


print("\nFailure distribution:")

print(
    transactions[
        "failure_reason"
    ].value_counts()
)


print("\nRecovery rate by action:")

print(
    recovery_dataset
    .groupby("action")["recovered"]
    .mean()
    .sort_values(
        ascending=False
    )
    .round(3)
)


print("\nRecovery rate by failure + action:")

print(
    recovery_dataset
    .groupby(
        [
            "failure_reason",
            "action"
        ]
    )["recovered"]
    .mean()
    .round(3)
)


print("\nFiles written:")

print(customers_path)
print(transactions_path)
print(recovery_dataset_path)

print("\nDone.")