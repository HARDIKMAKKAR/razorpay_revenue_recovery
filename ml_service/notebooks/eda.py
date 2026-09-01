import pandas as pd

customers = pd.read_csv("data/customers.csv")
transactions = pd.read_csv("data/transactions.csv")
recovery = pd.read_csv("data/recovery_events.csv")

print("\n========== SHAPES ==========")
print("Customers:", customers.shape)
print("Transactions:", transactions.shape)
print("Recovery:", recovery.shape)

print("\n========== TRANSACTIONS ==========")
print(transactions.head())
print("\nMissing values:")
print(transactions.isnull().sum())

print("\nFailure distribution:")
print(transactions["failure_reason"].value_counts())

print("\nPayment methods:")
print(transactions["payment_method"].value_counts())

print("\n========== CUSTOMERS ==========")
print(customers.head())

print("\nCustomer segments:")
print(customers["customer_segment"].value_counts())

print("\n========== RECOVERY ==========")
print(recovery.head())

print("\nActions:")
print(recovery["action_taken"].value_counts())

print("\nChannels:")
print(recovery["channel"].value_counts())

print("\nRecovery rate:")
print(recovery["recovered"].mean())

print("\nRecovery by action:")
print(
    recovery.groupby("action_taken")["recovered"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
)

print("\nRecovery by failure:")
print(
    recovery.groupby("failure_reason")["recovered"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
)