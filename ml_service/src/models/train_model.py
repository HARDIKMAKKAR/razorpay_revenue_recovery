import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score
)


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

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "recovery_action_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "recovery_model.joblib"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(
    f"Dataset shape: {df.shape}"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [

    # -------------------------
    # Payment
    # -------------------------

    "amount",
    "payment_method",
    "payment_gateway",
    "is_recurring",
    "attempt_number",

    # -------------------------
    # Failure
    # -------------------------

    "failure_reason",

    # -------------------------
    # Customer
    # -------------------------

    "customer_tenure_days",
    "total_transactions",
    "successful_transactions",
    "failed_transactions",
    "historical_success_rate",
    "avg_transaction_amount",
    "days_since_last_success",
    "customer_segment",

    # -------------------------
    # Candidate action
    # -------------------------

    "action"
]


TARGET = "recovered"


X = df[FEATURES]

y = df[TARGET]


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

categorical_features = [

    "payment_method",
    "payment_gateway",
    "failure_reason",
    "customer_segment",
    "action"
]


# ============================================================
# NUMERICAL FEATURES
# ============================================================

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
            "categorical",

            OneHotEncoder(
                handle_unknown="ignore"
            ),

            categorical_features
        ),

        (
            "numerical",

            "passthrough",

            numerical_features
        )
    ]
)


# ============================================================
# RANDOM FOREST
# ============================================================

model = RandomForestClassifier(

    n_estimators=300,

    max_depth=14,

    min_samples_leaf=5,

    class_weight="balanced",

    random_state=42,

    n_jobs=-1
)


# ============================================================
# PIPELINE
# ============================================================

pipeline = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )
    ]
)


# ============================================================
# GROUP TRAIN / TEST SPLIT
# ============================================================

print("\nCreating transaction-level train/test split...")

splitter = GroupShuffleSplit(

    n_splits=1,

    test_size=0.20,

    random_state=42
)


train_idx, test_idx = next(
    splitter.split(
        X,
        y,
        groups=df["transaction_id"]
    )
)


X_train = X.iloc[train_idx]

X_test = X.iloc[test_idx]

y_train = y.iloc[train_idx]

y_test = y.iloc[test_idx]


print(
    f"Training rows: {len(X_train):,}"
)

print(
    f"Testing rows: {len(X_test):,}"
)

print(
    f"Training transactions: "
    f"{df.iloc[train_idx]['transaction_id'].nunique():,}"
)

print(
    f"Testing transactions: "
    f"{df.iloc[test_idx]['transaction_id'].nunique():,}"
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training complete.")


# ============================================================
# EVALUATION
# ============================================================

print("\nEvaluating model...")

predictions = pipeline.predict(
    X_test
)

probabilities = pipeline.predict_proba(
    X_test
)[:, 1]


accuracy = accuracy_score(
    y_test,
    predictions
)

auc = roc_auc_score(
    y_test,
    probabilities
)


print(
    f"\nAccuracy: {accuracy:.4f}"
)

print(
    f"ROC-AUC: {auc:.4f}"
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)


# ============================================================
# PREDICTED PROBABILITY BY ACTION
# ============================================================

print(
    "\nPredicted recovery probability by action:"
)

test_results = X_test.copy()

test_results["transaction_id"] = df.iloc[
    test_idx
]["transaction_id"].values

test_results["actual_recovered"] = y_test.values

test_results["predicted_probability"] = probabilities


action_probability = (

    test_results
    .groupby("action")
    ["predicted_probability"]
    .mean()
    .sort_values(
        ascending=False
    )
)


print(
    action_probability.round(3)
)


# ============================================================
# ACTUAL RECOVERY RATE BY ACTION
# ============================================================

print(
    "\nActual recovery rate by action:"
)

actual_action_rate = (

    test_results
    .groupby("action")
    ["actual_recovered"]
    .mean()
    .sort_values(
        ascending=False
    )
)


print(
    actual_action_rate.round(3)
)


# ============================================================
# EXPECTED REVENUE
# ============================================================

print(
    "\nCalculating expected revenue..."
)


# Cost of executing each action

ACTION_COST = {

    "retry": 2.0,

    "reminder": 1.0,

    "payment_link": 3.0,

    "escalate": 8.0
}


# Customer friction penalty

ACTION_FRICTION = {

    "retry": 0.02,

    "reminder": 0.05,

    "payment_link": 0.08,

    "escalate": 0.15
}


test_results["action_cost"] = (
    test_results["action"]
    .map(ACTION_COST)
)


test_results["customer_friction"] = (
    test_results["action"]
    .map(ACTION_FRICTION)
)


# ============================================================
# EXPECTED REVENUE FORMULA
# ============================================================

test_results["expected_revenue"] = (

    test_results["predicted_probability"]
    * test_results["amount"]

    - test_results["action_cost"]

    - (
        test_results["amount"]
        * test_results["customer_friction"]
    )
)


# ============================================================
# BEST ACTION PER TRANSACTION
# ============================================================

print(
    "\nFinding best action for each transaction..."
)


best_action_indices = (

    test_results
    .groupby("transaction_id")
    ["expected_revenue"]
    .idxmax()
)


best_actions = test_results.loc[
    best_action_indices
].copy()


# ============================================================
# ACTION DISTRIBUTION
# ============================================================

print(
    "\nRecommended action distribution:"
)

print(
    best_actions[
        "action"
    ].value_counts()
)


# ============================================================
# EXPECTED REVENUE BY ACTION
# ============================================================

print(
    "\nAverage expected revenue by recommended action:"
)

print(

    best_actions
    .groupby("action")
    ["expected_revenue"]
    .mean()
    .sort_values(
        ascending=False
    )
    .round(2)
)


# ============================================================
# ACTION SELECTION EXAMPLES
# ============================================================

print(
    "\nSample decision examples:"
)


sample_transactions = (
    best_actions[
        "transaction_id"
    ]
    .sample(
        min(
            5,
            len(best_actions)
        ),
        random_state=42
    )
)


for transaction_id in sample_transactions:

    rows = test_results[
        test_results[
            "transaction_id"
        ] == transaction_id
    ].copy()

    rows = rows.sort_values(
        "expected_revenue",
        ascending=False
    )


    best = rows.iloc[0]


    print("\n----------------------------------------")

    print(
        f"Transaction: "
        f"{transaction_id}"
    )

    print(
        f"Amount: "
        f"₹{best['amount']:.2f}"
    )

    print(
        f"Failure: "
        f"{best['failure_reason']}"
    )

    print("\nActions:")

    for _, row in rows.iterrows():

        print(

            f"{row['action']:15s}"
            f" P={row['predicted_probability']:.3f}"
            f"  Expected=₹{row['expected_revenue']:.2f}"
        )

    print(
        f"\nBEST ACTION → "
        f"{best['action'].upper()}"
    )


# ============================================================
# SAVE MODEL
# ============================================================

print(
    "\nSaving model..."
)

joblib.dump(
    pipeline,
    MODEL_PATH
)


print(
    f"Model saved to:"
)

print(
    MODEL_PATH
)


print("\nDone.")