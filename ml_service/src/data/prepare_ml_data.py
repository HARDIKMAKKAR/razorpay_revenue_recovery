import pandas as pd

transactions = pd.read_csv("data/transactions.csv")
customers = pd.read_csv("data/customers.csv")
recovery = pd.read_csv("data/recovery_events.csv")

# Only failed transactions
failed = transactions[
    transactions["failure_reason"] != "none"
].copy()

# Join customer information
df = failed.merge(
    customers,
    on="customer_id",
    how="left"
)

# Join recovery outcome
df = df.merge(
    recovery[
        [
            "transaction_id",
            "action_taken",
            "channel",
            "retry_delay_hours",
            "recovered"
        ]
    ],
    on="transaction_id",
    how="left"
)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nTarget distribution:")
print(df["recovered"].value_counts())

print("\nTarget percentage:")
print(df["recovered"].value_counts(normalize=True))

# Save
df.to_csv(
    "data/ml_dataset.csv",
    index=False
)

print("\nSaved: data/ml_dataset.csv")