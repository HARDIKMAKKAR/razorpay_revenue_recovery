import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix
)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("data/ml_dataset.csv")

# ============================================================
# FEATURES
# ============================================================

features = [
    "amount",
    "payment_method",
    "payment_gateway",
    "failure_reason",
    "is_recurring",
    "attempt_number",
    "customer_tenure_days",
    "total_transactions",
    "successful_transactions",
    "failed_transactions",
    "historical_success_rate",
    "avg_transaction_amount",
    "days_since_last_success",
    "customer_segment"
]

X = df[features]
y = df["recovered"]

# ============================================================
# CATEGORICAL / NUMERICAL
# ============================================================

categorical_features = [
    "payment_method",
    "payment_gateway",
    "failure_reason",
    "customer_segment"
]

numerical_features = [
    "amount",
    "is_recurring",
    "attempt_number",
    "customer_tenure_days",
    "total_transactions",
    "successful_transactions",
    "failed_transactions",
    "historical_success_rate",
    "avg_transaction_amount",
    "days_since_last_success"
]

# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "num",
            "passthrough",
            numerical_features
        )
    ]
)

# ============================================================
# MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=5,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# ============================================================
# TRAIN
# ============================================================

pipeline.fit(X_train, y_train)

# ============================================================
# PREDICTION
# ============================================================

y_pred = pipeline.predict(X_test)

y_probability = pipeline.predict_proba(X_test)[:, 1]

# ============================================================
# EVALUATION
# ============================================================

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test,
        y_pred
    )
)

print("\n========== CONFUSION MATRIX ==========")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)

print("\n========== ROC-AUC ==========")

print(
    roc_auc_score(
        y_test,
        y_probability
    )
)

# ============================================================
# SAVE MODEL
# ============================================================

import joblib

joblib.dump(
    pipeline,
    "recovery_model.pkl"
)

print("\nModel saved as: recovery_model.pkl")