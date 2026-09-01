import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# ============================================================
# CONFIG
# ============================================================

NUM_CUSTOMERS = 20000
NUM_TRANSACTIONS = 100000

OUTPUT_DIR = "data"

# ============================================================
# HELPERS
# ============================================================

def random_date(start, end, n):
    start_ts = start.timestamp()
    end_ts = end.timestamp()

    return pd.to_datetime(
        np.random.uniform(start_ts, end_ts, n),
        unit="s"
    )


# ============================================================
# 1. CUSTOMERS
# ============================================================

customer_ids = [
    f"CUST{i:06d}"
    for i in range(1, NUM_CUSTOMERS + 1)
]

customer_tenure = np.random.randint(
    30, 1500, NUM_CUSTOMERS
)

total_transactions = np.random.poisson(
    15, NUM_CUSTOMERS
) + 1

historical_success_rate = np.clip(
    np.random.beta(8, 2, NUM_CUSTOMERS),
    0.40,
    0.99
)

successful_transactions = np.array([
    np.random.binomial(
        total_transactions[i],
        historical_success_rate[i]
    )
    for i in range(NUM_CUSTOMERS)
])

failed_transactions = (
    total_transactions - successful_transactions
)

avg_transaction_amount = np.round(
    np.random.lognormal(
        mean=7,
        sigma=0.8,
        size=NUM_CUSTOMERS
    ),
    2
)

days_since_last_success = np.random.randint(
    1, 90, NUM_CUSTOMERS
)

# Customer segment based partly on behavior/value

customer_segment = []

for i in range(NUM_CUSTOMERS):

    if avg_transaction_amount[i] > 10000:
        segment = "high_value"

    elif historical_success_rate[i] < 0.60:
        segment = "churn_risk"

    elif total_transactions[i] <= 5:
        segment = "new"

    else:
        segment = "regular"

    customer_segment.append(segment)


customers = pd.DataFrame({

    "customer_id": customer_ids,

    "customer_tenure_days": customer_tenure,

    "total_transactions": total_transactions,

    "successful_transactions": successful_transactions,

    "failed_transactions": failed_transactions,

    "historical_success_rate": np.round(
        historical_success_rate, 3
    ),

    "avg_transaction_amount": avg_transaction_amount,

    "days_since_last_success": days_since_last_success,

    "customer_segment": customer_segment
})


# ============================================================
# 2. TRANSACTIONS
# ============================================================

transaction_ids = [
    f"TXN{i:08d}"
    for i in range(1, NUM_TRANSACTIONS + 1)
]

transaction_customer_ids = np.random.choice(
    customer_ids,
    NUM_TRANSACTIONS
)

# Create lookup for customer attributes

customer_lookup = customers.set_index("customer_id")

transaction_amounts = []

for cid in transaction_customer_ids:

    avg = customer_lookup.loc[
        cid, "avg_transaction_amount"
    ]

    amount = np.random.lognormal(
        np.log(max(avg, 100)),
        0.45
    )

    transaction_amounts.append(
        round(amount, 2)
    )


payment_methods = np.random.choice(
    [
        "card",
        "upi",
        "netbanking",
        "wallet"
    ],
    NUM_TRANSACTIONS,
    p=[
        0.35,
        0.40,
        0.20,
        0.05
    ]
)


# Recurring payments are important for our use case

is_recurring = np.random.choice(
    [True, False],
    NUM_TRANSACTIONS,
    p=[0.70, 0.30]
)


# Attempt number

attempt_number = np.random.choice(
    [1, 2, 3],
    NUM_TRANSACTIONS,
    p=[0.80, 0.15, 0.05]
)


# Failure probability

failure_probability = np.zeros(NUM_TRANSACTIONS)


for i, cid in enumerate(transaction_customer_ids):

    success_rate = customer_lookup.loc[
        cid,
        "historical_success_rate"
    ]

    failure_probability[i] = (
        0.08
        + (1 - success_rate) * 0.25
        + (attempt_number[i] - 1) * 0.05
    )


failure_probability = np.clip(
    failure_probability,
    0.03,
    0.50
)


is_failed = (
    np.random.random(NUM_TRANSACTIONS)
    < failure_probability
)


# Failure reasons

failure_reasons = [
    "insufficient_funds",
    "bank_declined",
    "expired_card",
    "authentication_failed",
    "network_error",
    "limit_exceeded",
    "mandate_failed"
]

failure_reason_probability = [
    0.25,
    0.20,
    0.10,
    0.12,
    0.13,
    0.08,
    0.12
]


failure_reason = np.array(
    np.random.choice(
        failure_reasons,
        NUM_TRANSACTIONS,
        p=failure_reason_probability
    )
)

failure_reason[~is_failed] = "none"


# Failure codes

failure_code_map = {

    "insufficient_funds": "INSUFFICIENT_FUNDS",

    "bank_declined": "BANK_DECLINED",

    "expired_card": "CARD_EXPIRED",

    "authentication_failed": "AUTH_FAILED",

    "network_error": "NETWORK_ERROR",

    "limit_exceeded": "LIMIT_EXCEEDED",

    "mandate_failed": "MANDATE_FAILED",

    "none": "SUCCESS"
}


failure_code = [
    failure_code_map[x]
    for x in failure_reason
]


# Dates

start_date = datetime.now() - timedelta(days=365)

end_date = datetime.now()

transaction_dates = random_date(
    start_date,
    end_date,
    NUM_TRANSACTIONS
)


# Payment gateway

payment_gateways = np.random.choice(
    [
        "razorpay",
        "stripe",
        "payu"
    ],
    NUM_TRANSACTIONS,
    p=[
        0.75,
        0.15,
        0.10
    ]
)


subscription_ids = []

for i in range(NUM_TRANSACTIONS):

    if is_recurring[i]:

        subscription_ids.append(
            f"SUB{np.random.randint(1, 15000):06d}"
        )

    else:

        subscription_ids.append("none")


merchant_ids = np.random.choice(
    [
        "MERCHANT_001",
        "MERCHANT_002",
        "MERCHANT_003",
        "MERCHANT_004",
        "MERCHANT_005"
    ],
    NUM_TRANSACTIONS
)


transactions = pd.DataFrame({

    "transaction_id": transaction_ids,

    "customer_id": transaction_customer_ids,

    "merchant_id": merchant_ids,

    "subscription_id": subscription_ids,

    "amount": transaction_amounts,

    "currency": "INR",

    "payment_method": payment_methods,

    "payment_gateway": payment_gateways,

    "transaction_timestamp": transaction_dates,

    "failure_reason": failure_reason,

    "failure_code": failure_code,

    "is_recurring": is_recurring,

    "attempt_number": attempt_number
})


# ============================================================
# 3. RECOVERY EVENTS
# ============================================================

failed_transactions = transactions[
    transactions["failure_reason"] != "none"
].copy()


recovery_events = []

channels = [
    "sms",
    "email",
    "whatsapp",
    "push"
]


for _, txn in failed_transactions.iterrows():

    cid = txn["customer_id"]

    customer = customer_lookup.loc[cid]

    failure = txn["failure_reason"]

    success_rate = customer[
        "historical_success_rate"
    ]

    segment = customer[
        "customer_segment"
    ]

    # --------------------------------------------------------
    # Recovery probability
    # --------------------------------------------------------

    score = (
        1.5 * success_rate
        - 0.25 * (txn["attempt_number"] - 1)
        + 0.25 * (segment == "high_value")
        - 0.30 * (segment == "churn_risk")
    )

    # Failure-specific effect

    if failure == "network_error":
        score += 0.50

    elif failure == "insufficient_funds":
        score -= 0.30

    elif failure == "bank_declined":
        score -= 0.15

    elif failure == "authentication_failed":
        score -= 0.10

    elif failure == "mandate_failed":
        score -= 0.20


    recovery_probability = (
        1 / (1 + np.exp(-score))
    )

    recovery_probability = np.clip(
        recovery_probability,
        0.05,
        0.95
    )


    # --------------------------------------------------------
    # Action selection
    # --------------------------------------------------------

    if failure == "network_error":

        action = np.random.choice(
            ["retry", "payment_link"],
            p=[0.75, 0.25]
        )

    elif failure == "insufficient_funds":

        action = np.random.choice(
            ["reminder", "payment_link"],
            p=[0.65, 0.35]
        )

    elif failure == "authentication_failed":

        action = np.random.choice(
            ["payment_link", "reminder"],
            p=[0.70, 0.30]
        )

    elif failure == "bank_declined":

        action = np.random.choice(
            ["retry", "payment_link", "reminder"],
            p=[0.45, 0.30, 0.25]
        )

    elif failure == "expired_card":

        action = "payment_link"

    elif failure == "limit_exceeded":

        action = np.random.choice(
            ["payment_link", "reminder"],
            p=[0.60, 0.40]
        )

    else:

        action = np.random.choice(
            ["retry", "payment_link", "escalate"],
            p=[0.40, 0.40, 0.20]
        )


    # --------------------------------------------------------
    # Channel
    # --------------------------------------------------------

    if action == "retry":

        channel = "system"

    else:

        channel = np.random.choice(
            channels,
            p=[
                0.25,
                0.30,
                0.30,
                0.15
            ]
        )


    # --------------------------------------------------------
    # Retry delay
    # --------------------------------------------------------

    if action == "retry":

        if failure == "network_error":
            retry_delay = np.random.choice(
                [0.25, 1, 2]
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

        retry_delay = 0

    else:

        retry_delay = 48


    # --------------------------------------------------------
    # Actual recovery
    # --------------------------------------------------------

    recovered = np.random.random() < recovery_probability


    if recovered:

        recovery_time = round(
            np.random.exponential(
                max(retry_delay, 1)
            ),
            2
        )

        recovered_amount = txn["amount"]

    else:

        recovery_time = np.nan

        recovered_amount = 0


    recovery_events.append({

        "recovery_event_id":
            f"REC{len(recovery_events) + 1:08d}",

        "transaction_id":
            txn["transaction_id"],

        "customer_id":
            txn["customer_id"],

        "failure_reason":
            failure,

        "action_taken":
            action,

        "action_timestamp":
            txn["transaction_timestamp"]
            + timedelta(
                hours=float(
                    max(retry_delay, 0)
                )
            ),

        "channel":
            channel,

        "retry_delay_hours":
            retry_delay,

        "recovery_probability":
            round(
                recovery_probability,
                4
            ),

        "recovered":
            int(recovered),

        "recovery_time_hours":
            recovery_time,

        "recovered_amount":
            recovered_amount
    })


recovery_events = pd.DataFrame(
    recovery_events
)


# ============================================================
# SAVE
# ============================================================

import os

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

customers.to_csv(
    f"{OUTPUT_DIR}/customers.csv",
    index=False
)

transactions.to_csv(
    f"{OUTPUT_DIR}/transactions.csv",
    index=False
)

recovery_events.to_csv(
    f"{OUTPUT_DIR}/recovery_events.csv",
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n===================================")
print("DATASET GENERATION COMPLETE")
print("===================================")

print(
    f"Customers:       {len(customers):,}"
)

print(
    f"Transactions:    {len(transactions):,}"
)

print(
    f"Failed payments: "
    f"{len(failed_transactions):,}"
)

print(
    f"Recovery events: "
    f"{len(recovery_events):,}"
)

print("\nFailure distribution:")

print(
    transactions[
        transactions["failure_reason"] != "none"
    ]["failure_reason"].value_counts()
)

print("\nRecovery rate:")

print(
    recovery_events["recovered"].mean()
)

print("\nFiles created:")

print("data/customers.csv")
print("data/transactions.csv")
print("data/recovery_events.csv")