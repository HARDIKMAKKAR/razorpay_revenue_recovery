from decision_engine import recommend_action


payment = {
    "amount": 5000,
    "payment_method": "UPI",
    "payment_gateway": "Razorpay",
    "is_recurring": 1,
    "attempt_number": 1,
    "failure_reason": "insufficient_funds",
    "customer_tenure_days": 500,
    "total_transactions": 30,
    "successful_transactions": 27,
    "failed_transactions": 3,
    "historical_success_rate": 0.90,
    "avg_transaction_amount": 1500,
    "days_since_last_success": 5,
    "customer_segment": "regular"
}


result = recommend_action(payment)


print("\n======================================")
print("       REVENUE RECOVERY DECISION")
print("======================================")

print(f"Failure: {result['failure_reason']}")
print(f"Amount: ₹{result['amount']:.2f}")

print(
    f"\nRecommended Action: "
    f"{result['recommended_action'].upper()}"
)

print(
    f"Recovery Probability: "
    f"{result['recovery_probability']:.2%}"
)

print(
    f"Expected Revenue: "
    f"₹{result['expected_revenue']:.2f}"
)

print(f"\nReason: {result['reason']}")

print("\nAll Valid Actions:")

for action in result["alternatives"]:

    print(
        f"{action['action']:15s}"
        f" P={action['recovery_probability']:.2%}"
        f" Expected=₹{action['expected_revenue']:.2f}"
    )