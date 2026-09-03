# 🚀 Intelligent Revenue Recovery System

> AI-powered payment failure recovery for subscription businesses.

## 🏆 Built for the Razorpay Hackathon — Track 3: AI Revenue Recovery

This project was built as a hackathon prototype for Razorpay's AI Revenue Recovery track.

The goal is to build an intelligent layer that helps merchants make better recovery decisions after a recurring payment fails.

Instead of treating every failed payment the same way, the system analyzes the payment failure, customer history, transaction context, and proposed recovery action to estimate the probability of successful recovery and recommend the most suitable action.

---

# 📌 Overview

A failed recurring payment does not necessarily mean lost revenue.

Different failures require different recovery strategies.

For example:

- A temporary network error may be suitable for a retry.
- Insufficient funds may require a reminder or payment link.
- An expired card may require an alternative payment method.
- A repeated or complex mandate failure may require escalation.

The **Intelligent Revenue Recovery System** combines:

1. Machine Learning
2. Failure-aware business rules
3. Expected revenue optimization
4. Node.js backend APIs
5. Flask ML service
6. Angular merchant dashboard

to determine:

> **"What is the best next action to recover this revenue?"**

---

# 🎯 Hackathon Objective

The objective of this project is to move beyond a simple fixed retry strategy.

Instead of asking:

> "Should we retry this payment?"

the system asks:

> **"Given this payment failure and customer context, what recovery action is most likely to recover the revenue while minimizing unnecessary cost and customer friction?"**

---

# 🔴 Problem

Failed payments are a major source of potential revenue leakage for subscription-based businesses.

A failed payment does **not necessarily mean that the customer has churned**.

The cause of the failure matters.

| Failure Reason | Suitable Recovery Strategy |
|---|---|
| Network Error | Retry |
| Insufficient Funds | Reminder / Payment Link |
| Authentication Failure | Payment Link |
| Expired Card | Payment Link |
| Bank Declined | Reminder / Payment Link / Retry |
| Limit Exceeded | Reminder / Payment Link |
| Mandate Failure | Retry / Payment Link / Reminder / Escalation |

A simple fixed-retry strategy can look like:

```text
Payment Failed
      ↓
Wait Fixed Time
      ↓
Retry
      ↓
Retry Again
      ↓
Generic Reminder
```

The problem with this approach is that it does not sufficiently account for the reason behind the failure or the customer's historical behavior.

This can lead to:

- Unnecessary payment retries
- Poor customer experience
- Excessive notifications
- Delayed revenue recovery
- Additional processing costs
- Revenue remaining unrecovered

---

# 💡 Solution

Our solution introduces an **AI-powered revenue recovery decision layer**.

For every failed payment, the system evaluates:

### Transaction Context

- Payment amount
- Payment method
- Payment gateway
- Failure reason
- Attempt number
- Recurring payment status

### Customer Context

- Customer tenure
- Total transactions
- Successful transactions
- Failed transactions
- Historical success rate
- Average transaction amount
- Days since last successful payment
- Customer segment

The ML model then estimates:

```text
P(payment will be recovered | context + action)
```

The decision engine then evaluates the valid recovery actions and selects the action with the highest expected revenue.

---

# 🧠 Key Idea

The system separates two different questions.

## 1. ML Model

> **"How likely is this payment to be recovered if we take this action?"**

The model predicts a recovery probability for each candidate action.

Example:

```text
Failure: Insufficient Funds

Payment Link
Recovery Probability = 79.82%

Reminder
Recovery Probability = 73.29%
```

## 2. Decision Engine

> **"What should we do next?"**

The decision engine:

1. Identifies the failure reason.
2. Filters actions that are not appropriate for that failure.
3. Gets the ML recovery probability for each valid action.
4. Calculates expected revenue.
5. Selects the highest-value action.

This separation allows machine learning predictions to work together with business rules and economic considerations.

---

# 💰 Expected Revenue Optimization

The decision engine calculates expected revenue as:

```text
Expected Revenue =
    Recovery Probability × Payment Amount
    − Action Cost
    − Customer Friction
```

For example:

```text
Payment Amount = ₹5,000

Recovery Probability = 79.82%

Action Cost = ₹3

Customer Friction = 8%

Expected Revenue ≈ ₹3,587.93
```

The action with the highest expected revenue is selected.

This means the system is not simply optimizing for prediction accuracy.

It is using the prediction to optimize for a **business outcome: expected recovered revenue**.

---

# ⚙️ How It Works

The current hackathon MVP follows this flow:

```text
                  Failed Payment
                        │
                        ▼
               Angular Dashboard
                        │
                        ▼
                Node.js Backend
                        │
                        ▼
              Flask ML Service
                        │
                        ▼
              Random Forest Model
                        │
                        ▼
             Recovery Probabilities
                        │
                        ▼
              Decision Engine
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            RETRY    REMINDER   PAYMENT LINK
                        │
                        ▼
                 Best Recommendation
                        │
                        ▼
               Angular Dashboard
```

The current prototype demonstrates the complete prediction and recommendation pipeline using synthetic payment data.

---

# 🏗️ System Architecture

```text
┌───────────────────────────┐
│     Angular Dashboard     │
│       Merchant UI         │
└─────────────┬─────────────┘
              │
              │ HTTP
              ▼
┌───────────────────────────┐
│    Node.js / Express      │
│      Backend API          │
└─────────────┬─────────────┘
              │
              │ Prediction Request
              ▼
┌───────────────────────────┐
│     Python / Flask        │
│       ML Service          │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   Random Forest Model     │
│   Recovery Probability    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    Recovery Decision      │
│         Engine            │
└─────────────┬─────────────┘
              │
              ▼
      Recommended Action

---

# 🤖 Machine Learning

## Objective

The ML model predicts:

```text
P(payment will be recovered | payment + customer + action)
```

This is formulated as a **binary classification problem**.

### Target

```text
recovered

1 → Payment recovered
0 → Payment not recovered
```

## Model Features

### Transaction Features

```text
amount
payment_method
payment_gateway
is_recurring
attempt_number
failure_reason
```

### Customer Features

```text
customer_tenure_days
total_transactions
successful_transactions
failed_transactions
historical_success_rate
avg_transaction_amount
days_since_last_success
customer_segment
```

### Recovery Action

```text
action
```

The action is included as a feature because the model estimates recovery probability conditional on the proposed intervention.

## Data Leakage Prevention

The model excludes post-outcome fields such as:

```text
recovery_probability
recovered_amount
recovery_time_hours
action_cost
customer_friction
```

Model evaluation uses a **transaction-level group split** so different candidate actions from the same transaction cannot appear in both training and testing sets.

## Initial Model

```text
Random Forest Classifier
```

Current held-out evaluation:

```text
Accuracy  ≈ 70.5%
ROC-AUC    ≈ 0.724
```

The model is used primarily as a recovery probability engine inside the larger decision system.

---

# 🧠 Recovery Decision Engine

The ML model does not directly determine the final action.

The decision engine applies failure-aware rules.

### Valid Actions

```text
retry
reminder
payment_link
escalate
```

Example:

```text
Network Error
      ↓
Valid Actions:
Retry
Reminder
Payment Link
      ↓
ML Probabilities
      ↓
Expected Revenue
      ↓
RETRY
```

For insufficient funds:

```text
Insufficient Funds
      ↓
Valid Actions:
Reminder
Payment Link
      ↓
ML Probabilities
      ↓
Expected Revenue
      ↓
PAYMENT LINK / REMINDER
```

---

# 🖥️ Merchant Dashboard

The Angular frontend provides a merchant-facing recovery dashboard.

The dashboard displays:

- Failed payments
- Customer information
- Payment amount
- Failure reason
- Attempt number
- AI recovery recommendation
- Recovery probability
- Expected revenue
- Alternative actions

Example:

```text
Customer: Rahul Sharma
Amount: ₹5,000
Failure: Insufficient Funds

Recommended Action:
PAYMENT LINK

Recovery Probability:
79.82%

Expected Revenue:
₹3,587.93
```

---

# 📦 Dataset

The current hackathon prototype uses **synthetic data**.

No real customer or payment information is used.

The main training dataset is:

```text
data/raw/recovery_action_dataset.csv
```

It represents candidate recovery actions for failed transactions and their recovery outcomes.

Supporting synthetic datasets include:

```text
customers.csv
transactions.csv
recovery_events.csv
```

The action-conditioned dataset allows the model to learn:

```text
Payment Context
+
Customer Context
+
Recovery Action
        ↓
Recovery Outcome
```

---

# 📁 Project Structure

```text
razorpay_revenue_recovery/
│
├── frontend/
│   └── Angular merchant dashboard
│
├── backend/
│   ├── routes/
│   │   └── recovery.js
│   ├── server.js
│   ├── package.json
│   └── .env
│
├── ml_service/
│   ├── data/
│   │   ├── raw/
│   │   │   ├── customers.csv
│   │   │   ├── transactions.csv
│   │   │   ├── recovery_events.csv
│   │   │   └── recovery_action_dataset.csv
│   │   └── processed/
│   │
│   ├── models/
│   │   └── recovery_model.joblib
│   │
│   ├── src/
│   │   ├── data/
│   │   │   └── generate_data.py
│   │   ├── models/
│   │   │   └── train_model.py
│   │   ├── decision_engine.py
│   │   ├── test_decision.py
│   │   └── app.py
│   │
│   ├── requirements.txt
│   └── .venv/
│
├── infrastructure/
├── docs/
├── README.md
└── .gitignore
```

---

# 🛠️ Technology Stack

### Frontend
- Angular
- TypeScript
- HTML
- CSS

### Backend
- Node.js
- Express.js
- Axios
- REST APIs

### ML Service
- Python
- Flask
- Pandas
- NumPy
- Scikit-learn
- Joblib

### ML
- Random Forest Classifier
- One-Hot Encoding
- Transaction-level group splitting

---

# 🔌 API Architecture

```text
Angular
   │
   │ POST
   ▼
Node.js / Express
   │
   │ POST
   ▼
Flask ML Service
   │
   ▼
Decision Engine
   │
   ▼
Recovery Recommendation
```

## Current Recommendation API

```text
POST /api/recovery/recommend
```

Example request:

```json
{
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
```

Example response:

```json
{
  "failure_reason": "insufficient_funds",
  "amount": 5000,
  "recommended_action": "payment_link",
  "recovery_probability": 0.7982,
  "expected_revenue": 3587.93,
  "reason": "A payment link gives the customer an alternative way to complete the payment."
}
```

## ML Health API

```text
GET /health
```

---

# 💻 Running the Project

## 1. Clone

```bash
git clone <repository-url>
cd razorpay_revenue_recovery
```

## 2. ML Service

```bash
cd ml_service
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate synthetic data:

```bash
python src/data/generate_data.py
```

Train model:

```bash
python src/models/train_model.py
```

Start ML service:

```bash
python src/app.py
```

ML service:

```text
http://localhost:5001
```

## 3. Backend

Open another terminal:

```bash
cd backend
npm install
node server.js
```

Backend:

```text
http://localhost:5000
```

## 4. Frontend

Open another terminal:

```bash
cd frontend
npm install
ng serve
```

Frontend:

```text
http://localhost:4200
```

---

# 🔄 End-to-End Flow

```text
1. Merchant selects a failed payment
                ↓
2. Angular sends payment context
                ↓
3. Node.js backend receives request
                ↓
4. Node.js calls Flask ML service
                ↓
5. ML model evaluates candidate actions
                ↓
6. Decision engine filters invalid actions
                ↓
7. Expected revenue is calculated
                ↓
8. Best recovery action is selected
                ↓
9. Recommendation is returned
                ↓
10. Angular dashboard displays result
```

---

# 🎥 Hackathon Demonstration

The prototype demonstrates multiple failure scenarios.

### Scenario 1 — Insufficient Funds

```text
Payment Amount: ₹5,000
Failure: Insufficient Funds

             ↓

Payment Link
Recovery Probability: 79.82%

Expected Revenue: ₹3,587.93
```

### Scenario 2 — Network Error

```text
Payment Failure:
Network Error

             ↓

Retry
```

The key demonstration is that **changing the failure context can change the recommended recovery action**.

---

# 🚧 Current MVP Scope

## Implemented

- Synthetic customer data
- Synthetic transaction data
- Action-conditioned recovery dataset
- ML training pipeline
- Random Forest recovery model
- Recovery probability prediction
- Failure-aware action filtering
- Expected revenue calculation
- Recovery decision engine
- Flask ML API
- Node.js backend
- Angular merchant dashboard
- End-to-end frontend → backend → ML integration

## Future/Productization Work

- Live Razorpay webhook integration
- Real payment execution
- Production database
- Authentication and authorization
- Live customer/payment data
- Automated notification delivery
- Production deployment
- Continuous model retraining
- Dynamic retry scheduling
- Full analytics pipeline

---

# 🚀 Future Improvements

## 1. Razorpay Webhook Integration

A production version can consume payment failure events through Razorpay webhooks:

```text
Payment Failed
      ↓
Razorpay Webhook
      ↓
Backend
      ↓
ML + Decision Engine
      ↓
Recovery Action
```

## 2. Dynamic Retry Scheduling

Instead of fixed retry intervals, the system could learn the optimal retry timing for each customer and failure type.

## 3. Contextual Action Optimization

Future versions could learn the best recovery action directly from historical outcomes using approaches such as:

- Contextual Bandits
- Reinforcement Learning
- Causal Inference

## 4. Customer-Specific Recovery

Different customers may respond differently to recovery strategies.

```text
Customer A
High historical success
        ↓
Retry

Customer B
Frequent insufficient-funds failures
        ↓
Reminder

Customer C
Expired card
        ↓
Payment Link
```

## 5. Continuous Learning

Future versions can incorporate recovery outcomes into model retraining:

```text
Prediction
    ↓
Action
    ↓
Outcome
    ↓
Feedback
    ↓
Future Model
```

---

# 📈 Success Metrics

## ML Metrics

- Accuracy
- ROC-AUC
- Precision
- Recall
- F1 Score
- Confusion Matrix

## Business Metrics

- Recovery Rate
- Revenue Recovered
- Revenue At Risk
- Recovery Lift
- Average Recovery Time
- Unnecessary Retry Reduction

The key future business metric is:

> **Additional revenue recovered compared with a basic fixed-retry strategy.**

---

# 🔐 Security Considerations

A production deployment should include:

- Webhook signature verification
- Authentication and authorization
- Encrypted credentials
- Secure environment variables
- API rate limiting
- Input validation
- Logging and monitoring
- No storage of sensitive payment credentials

The hackathon prototype uses synthetic payment information.

---

# 🧪 Testing

The current prototype includes testing of:

- Dataset generation
- Model training and evaluation
- Decision engine recommendations
- ML API
- Backend → ML integration
- Frontend → backend integration

The core end-to-end path is:

```text
Failed Payment
      ↓
Angular
      ↓
Backend
      ↓
ML Service
      ↓
Decision Engine
      ↓
Recommendation
      ↓
Dashboard
```

---

# 🏆 Hackathon Demo

The hackathon demo focuses on showing how the system reacts differently to different payment failures.

Example:

```text
Insufficient Funds
        ↓
Payment Link

Network Error
        ↓
Retry
```

This demonstrates the core idea:

> **Different failures can require different recovery actions.**

---

# ⚠️ Disclaimer

This project is a **hackathon prototype**.

The current development environment uses synthetic customer and payment data.

No real customer information, payment credentials, or financial data are used.

Live Razorpay payment events are not currently connected to the MVP; payment scenarios are simulated during development.

Any production deployment would require appropriate security, compliance, payment-provider integration, and operational controls.

---

# 🎯 Final Objective

The goal is not simply to predict whether a payment will succeed.

The goal is to answer:

> **"A payment just failed. What should we do next to maximize the probability of recovering this revenue while minimizing unnecessary retries and customer friction?"**

The core intelligence loop is:

```text
FAILED PAYMENT
      ↓
UNDERSTAND WHY
      ↓
ANALYZE CUSTOMER
      ↓
PREDICT RECOVERY
      ↓
CHOOSE BEST ACTION
      ↓
RECOVER REVENUE
```

---

# 👥 Team

Built for the **Razorpay Hackathon — Track 3: AI Revenue Recovery**.

---

## ⭐ Project Status

**Hackathon MVP — Core ML + Decision Engine + Backend + Frontend completed.**

The prototype demonstrates the core revenue-recovery decision workflow using synthetic data.
