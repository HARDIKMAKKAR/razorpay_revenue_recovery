# 🚀 Intelligent Revenue Recovery System

> AI-powered payment failure recovery for subscription businesses.

An AI-powered full-stack system that helps merchants **recover revenue lost due to failed recurring payments**.

Instead of blindly retrying every failed payment, the system analyzes the **payment failure, customer history, transaction context, and previous behavior** to predict the probability of recovery and recommend the most suitable recovery action.

---

## 📑 Table of Contents

- [Problem](#-problem)
- [Solution](#-solution)
- [Key Idea](#-key-idea)
- [How It Works](#-how-it-works)
- [Example](#-example)
- [System Architecture](#-system-architecture)
- [Machine Learning](#-machine-learning)
- [Recovery Decision Engine](#-recovery-decision-engine)
- [Merchant Dashboard](#-merchant-dashboard)
- [Dataset](#-dataset)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [End-to-End Flow](#-end-to-end-flow)
- [API Architecture](#-api-architecture)
- [Running the Project](#-running-the-project)
- [Development Roadmap](#-development-roadmap)
- [Future Improvements](#-future-improvements)
- [Disclaimer](#-disclaimer)

---

# 🔴 Problem

Failed payments are a major source of revenue leakage for subscription-based businesses.

A failed payment does **not necessarily mean that the customer has churned**.

Different payment failures have different causes and therefore require different recovery strategies.

For example:

| Failure Reason | Possible Recovery Strategy |
|---|---|
| Network Error | Retry quickly |
| Insufficient Funds | Remind customer later |
| Authentication Failure | Send payment link |
| Expired Card | Request payment method update |
| Bank Decline | Retry later |
| Mandate Failure | Payment link / alternate method |
| Repeated Failures | Escalate or stop retries |

A traditional recovery system often looks like:

```text
Payment Failed
      ↓
Wait fixed time
      ↓
Retry
      ↓
Retry again
      ↓
Send generic reminder
```

The problem is that this strategy treats every customer and every failure in the same way.

This can result in:

Unnecessary payment retries
Poor customer experience
Excessive notifications
Delayed revenue recovery
Increased payment processing costs
Revenue being permanently lost
💡 Solution

We are building an AI-powered Revenue Recovery System that makes recovery decisions based on the context of each failed payment.

The system analyzes:

Transaction Context
Payment amount
Payment method
Payment gateway
Failure reason
Failure code
Attempt number
Recurring payment status
Customer Context
Customer tenure
Total transactions
Successful transactions
Failed transactions
Historical success rate
Average transaction value
Days since last successful payment
Customer segment

The ML model predicts:

Probability that the failed payment can be recovered

For example:

Recovery Probability = 87%

The decision engine then determines the most appropriate action:

RETRY
REMINDER
PAYMENT LINK
ESCALATE
STOP

The result is tracked and displayed to the merchant.

🎯 Key Idea

The system separates two different questions:

ML Model

"How likely is this payment to be recovered?"

Example:

Recovery Probability = 87%
Decision Engine

"What should we do next?"

Example:

Failure Reason = Network Error
Recovery Probability = 87%
Attempt Number = 1

        ↓

Recommended Action = RETRY

This separation allows the system to combine machine learning with business logic.

⚙️ How It Works

The complete system follows this pipeline:

                    PAYMENT ATTEMPT
                           │
                           ▼
                    Payment Failed
                           │
                           ▼
                  Razorpay Webhook
                           │
                           ▼
                    Node.js Backend
                           │
                           ▼
              ┌────────────────────────┐
              │ Customer + Transaction │
              │ Context                │
              └────────────┬───────────┘
                           │
                           ▼
                     ML Service
                           │
                           ▼
                Recovery Probability
                           │
                           ▼
                  Decision Engine
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
        RETRY           REMINDER       PAYMENT LINK
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                        Customer
                           │
                           ▼
                    Payment Outcome
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
               Recovered          Failed
                  │                 │
                  └────────┬────────┘
                           ▼
                       Analytics
                           │
                           ▼
                    Merchant Dashboard
🧪 Example

Consider a failed recurring payment:

Customer ID: CUST00123
Amount: ₹8,500
Payment Method: Card
Failure Reason: Network Error
Attempt Number: 1
Recurring: Yes

Historical Success Rate: 91%
Customer Tenure: 420 days

The ML model receives these features and predicts:

Recovery Probability = 87%

The decision engine evaluates:

Failure = Network Error
Probability = 87%
Attempt = 1

and recommends:

Action = RETRY
Retry Delay = 1 hour

If the payment succeeds:

Recovered Amount = ₹8,500

The dashboard updates:

Revenue Recovered
₹8,500

The recovery event is also stored as feedback for future analysis.

🏗️ System Architecture

The entire application is maintained as a single monorepo.

                         ┌─────────────────┐
                         │    Razorpay     │
                         │   Webhook/API   │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │        Backend          │
                    │     Node.js/Express     │
                    └────────────┬────────────┘
                                 │
                         Prediction Request
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       ML Service        │
                    │       Python/Flask      │
                    └────────────┬────────────┘
                                 │
                        Recovery Probability
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Recovery Decision    │
                    │        Engine           │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
           RETRY              REMINDER         PAYMENT LINK
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 ▼
                             Customer
                                 │
                                 ▼
                          Payment Outcome
                                 │
                                 ▼
                             Analytics
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Angular Dashboard    │
                    │        Merchant         │
                    └─────────────────────────┘
🤖 Machine Learning
Objective

The first ML model predicts:

P(payment will be recovered)

This is a binary classification problem.

Target Variable
recovered

Where:

1 → Payment recovered
0 → Payment not recovered
Input Features

The model uses information available before the recovery action is taken.

Transaction Features
amount
payment_method
payment_gateway
failure_reason
is_recurring
attempt_number
Customer Features
customer_tenure_days
total_transactions
successful_transactions
failed_transactions
historical_success_rate
avg_transaction_amount
days_since_last_success
customer_segment
Data Leakage Prevention

The model must not use information that becomes available after the recovery decision.

Therefore the following fields are excluded from the initial prediction model:

action_taken
channel
retry_delay_hours
recovery_time_hours
recovered_amount

These describe the recovery action or outcome and therefore cannot be used as prediction inputs.

Initial Model

The initial model uses:

Random Forest Classifier

Reasons:

Handles nonlinear relationships
Works well with mixed features
Requires limited preprocessing
Provides feature importance
Fast enough for the hackathon prototype

Potential future models:

Logistic Regression
XGBoost
LightGBM
🧠 Recovery Decision Engine

The ML model predicts the probability of recovery.

The decision engine converts this prediction into an actionable recovery strategy.

Example:

Failure Reason = Network Error
Recovery Probability = 86%
Attempt Number = 1

              ↓

            RETRY

Another example:

Failure Reason = Insufficient Funds
Recovery Probability = 48%

              ↓

          REMINDER

Another:

Failure Reason = Expired Card

              ↓

        PAYMENT LINK

The decision engine considers:

ML Probability
+
Failure Reason
+
Attempt Number
+
Customer Context
+
Business Rules
📊 Merchant Dashboard

The Angular frontend provides merchants with a real-time view of payment recovery.

Key Metrics

Example:

┌────────────────────────────────────────────┐
│                                            │
│  Revenue At Risk        ₹12.4 L            │
│  Revenue Recovered       ₹8.7 L            │
│  Recovery Rate            70.2%            │
│  Failed Payments          1,428            │
│                                            │
└────────────────────────────────────────────┘
Failed Payment Table
Transaction   Amount    Failure       Probability   Action
------------------------------------------------------------
TXN00123      ₹8,500    Network       87%            Retry
TXN00124      ₹3,200    Funds         46%            Reminder
TXN00125      ₹6,700    Expired Card  31%            Payment Link

The merchant can see:

Which payments failed
Why they failed
Recovery probability
Recommended action
Recovery status
Recovered revenue
📦 Dataset

The current system uses synthetic data for development.

This allows the complete ML pipeline to be developed without using real customer or payment information.

The dataset consists of three primary files.

customers.csv

One row represents one customer.

Contains:

customer_id
customer_tenure_days
total_transactions
successful_transactions
failed_transactions
historical_success_rate
avg_transaction_amount
days_since_last_success
customer_segment
transactions.csv

One row represents one payment attempt.

Contains:

transaction_id
customer_id
merchant_id
subscription_id
amount
currency
payment_method
payment_gateway
transaction_timestamp
failure_reason
failure_code
is_recurring
attempt_number
recovery_events.csv

One row represents one recovery attempt.

Contains:

recovery_event_id
transaction_id
customer_id
failure_reason
action_taken
action_timestamp
channel
retry_delay_hours
recovery_probability
recovered
recovery_time_hours
recovered_amount
🔄 ML Dataset

The customer and transaction information is combined with recovery outcomes to create:

ml_dataset.csv

This dataset is used for model training and evaluation.

The ML pipeline is:

customers.csv
       +
transactions.csv
       +
recovery_events.csv
       │
       ▼
prepare_ml_data.py
       │
       ▼
ml_dataset.csv
       │
       ▼
Feature Processing
       │
       ▼
Model Training
📁 Project Structure

The entire application is contained inside one repository.

razorpay-revenue-recovery/
│
├── frontend/
│   │
│   └── Angular merchant dashboard
│
├── backend/
│   │
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   ├── middleware/
│   │   └── utils/
│   │
│   └── package.json
│
├── ml_service/
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   ├── customers.csv
│   │   │   ├── transactions.csv
│   │   │   └── recovery_events.csv
│   │   │
│   │   └── processed/
│   │       └── ml_dataset.csv
│   │
│   ├── src/
│   │   ├── data/
│   │   │   ├── generate_data.py
│   │   │   └── prepare_ml_data.py
│   │   │
│   │   ├── models/
│   │   │   ├── train_model.py
│   │   │   └── evaluate.py
│   │   │
│   │   └── prediction/
│   │       └── predictor.py
│   │
│   ├── notebooks/
│   │   └── 01_eda.ipynb
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── infrastructure/
│   │
│   └── AWS / Docker configuration
│
├── docs/
│   ├── architecture.md
│   └── api.md
│
├── README.md
├── .gitignore
└── docker-compose.yml
🛠️ Technology Stack
Frontend
Angular
TypeScript
HTML
CSS
Backend
Node.js
Express.js
REST APIs
ML Service
Python
Flask
Pandas
NumPy
Scikit-learn
Joblib
Infrastructure
Docker
AWS
Payment Integration
Razorpay APIs
Razorpay Webhooks
🔌 API Architecture

The backend acts as the main application layer.

The ML service operates as an independent service.

Angular
   │
   ▼
Node.js Backend
   │
   ├───────────────► Database
   │
   │
   └───────────────► ML Service
                          │
                          ▼
                  Recovery Probability
📡 Payment Failure API

When a payment fails, Razorpay sends a webhook.

Example endpoint:

POST /api/webhooks/payment-failed

The backend:

Receive webhook
      ↓
Validate event
      ↓
Extract payment information
      ↓
Fetch customer information
      ↓
Create ML features
      ↓
Call ML service
      ↓
Receive probability
      ↓
Run decision engine
      ↓
Store recovery event
      ↓
Return recommended action
🤖 ML Prediction API

Example endpoint:

POST /predict

Example request:

{
  "amount": 8500,
  "payment_method": "card",
  "payment_gateway": "razorpay",
  "failure_reason": "network_error",
  "is_recurring": true,
  "attempt_number": 1,
  "customer_tenure_days": 420,
  "total_transactions": 35,
  "successful_transactions": 32,
  "failed_transactions": 3,
  "historical_success_rate": 0.91,
  "avg_transaction_amount": 7200,
  "days_since_last_success": 5,
  "customer_segment": "regular"
}

Example response:

{
  "recovery_probability": 0.87
}
🔄 End-to-End Example
1. Customer's subscription payment fails
                  ↓
2. Razorpay sends webhook
                  ↓
3. Backend receives failure
                  ↓
4. Backend gets customer history
                  ↓
5. Features are sent to ML service
                  ↓
6. ML predicts recovery probability
                  ↓
7. Decision engine selects action
                  ↓
8. Recovery action is triggered
                  ↓
9. Payment outcome is recorded
                  ↓
10. Dashboard updates
💻 Running the Project
1. Clone Repository
git clone <repository-url>

cd razorpay-revenue-recovery
🐍 ML Service Setup

Navigate to:

cd ml_service

Create virtual environment:

python -m venv .venv
Windows
.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
Generate Synthetic Data
python src/data/generate_data.py

This generates:

data/raw/customers.csv
data/raw/transactions.csv
data/raw/recovery_events.csv
Prepare ML Dataset
python src/data/prepare_ml_data.py

This generates:

data/processed/ml_dataset.csv
Train Model
python src/models/train_model.py

The trained model will be saved locally.

Start ML Service
python app.py

The Flask service exposes the prediction API.

🟢 Backend Setup

Navigate to:

cd backend

Install dependencies:

npm install

Start development server:

npm run dev
🖥️ Frontend Setup

Navigate to:

cd frontend

Install dependencies:

npm install

Start Angular:

ng serve
🐳 Docker

The final version will support running the complete system using:

docker-compose up

This will allow:

Frontend
Backend
ML Service

to run together.

🚧 Development Roadmap
Phase 1 — Repository & Data
 Monorepo structure
 Synthetic customer dataset
 Synthetic transaction dataset
 Synthetic recovery dataset
 ML dataset preparation
Phase 2 — Machine Learning
 Exploratory Data Analysis
 Feature engineering
 Train/test split
 Baseline model
 Random Forest model
 Model evaluation
 Feature importance
 Prediction API
Phase 3 — Backend
 Express application
 Payment failure API
 ML service integration
 Recovery decision engine
 Recovery event storage
 Analytics APIs
Phase 4 — Frontend
 Angular dashboard
 Revenue at risk
 Revenue recovered
 Recovery rate
 Failed payment table
 Recovery probability
 Recommended action
 Recovery analytics
Phase 5 — Integration
 Razorpay webhook simulation
 Backend → ML integration
 Frontend → Backend integration
 End-to-end payment flow
 Docker setup
 Demo testing
🚀 Future Improvements

The initial system combines supervised machine learning with a rule-based decision engine.

Future versions can make the decision process more intelligent.

Dynamic Retry Scheduling

Instead of using fixed retry intervals:

Retry after 1 hour
Retry after 6 hours
Retry after 24 hours

the system can learn:

When is the optimal time to retry for this customer?
Action Optimization

Instead of manually defining:

Failure → Action

the system could learn:

Customer Context
       +
Failure Context
       +
Historical Outcomes
       ↓
Best Recovery Action

Potential approaches:

Contextual Bandits
Reinforcement Learning
Causal Inference
Customer-Specific Recovery

Different customers can receive different recovery strategies.

Example:

Customer A
High historical success
        ↓
Immediate Retry
Customer B
Frequent insufficient-funds failures
        ↓
Reminder
Customer C
Expired card
        ↓
Payment Link
Continuous Learning

Every recovery attempt generates an outcome.

Prediction
    ↓
Action
    ↓
Outcome
    ↓
Feedback
    ↓
Future Model

This creates a continuous learning loop.

📈 Success Metrics

The system will be evaluated using both ML and business metrics.

ML Metrics
ROC-AUC
Precision
Recall
F1 Score
Confusion Matrix
Business Metrics
Recovery Rate
Revenue Recovered
Revenue At Risk
Recovery Lift
Average Recovery Time
Unnecessary Retry Reduction

The most important business metric is:

Additional revenue recovered compared with a basic fixed-retry strategy.

🔐 Security Considerations

The production version should include:

Webhook signature verification
Authentication and authorization
Encrypted credentials
Secure environment variables
API rate limiting
Input validation
Logging and monitoring
No storage of sensitive payment credentials

The hackathon prototype will use simulated/synthetic payment information where appropriate.

🧪 Testing Strategy

The system will be tested at multiple levels.

ML
Dataset validation
Feature validation
Model evaluation
Prediction testing
Backend
API tests
Webhook tests
Decision engine tests
ML integration tests
Frontend
Component tests
API integration
Dashboard validation
End-to-End
Failed Payment
      ↓
Webhook
      ↓
Backend
      ↓
ML
      ↓
Decision
      ↓
Recovery
      ↓
Dashboard
🏆 Hackathon Demo

The final demonstration will simulate a failed subscription payment.

Scenario
Payment Failed
       ↓
Network Error
       ↓
Customer history retrieved
       ↓
ML prediction
       ↓
Recovery Probability = 87%
       ↓
Recommended Action = RETRY
       ↓
Payment recovered
       ↓
Revenue Recovered = ₹8,500

The merchant dashboard will show the complete recovery journey.

⚠️ Disclaimer

This project is a hackathon prototype.

The current development environment uses synthetic customer and payment data.

No real customer information, payment credentials, or financial data are used.

Razorpay payment events may be simulated during development.

Any production deployment would require appropriate security, compliance, payment-provider integration, and operational controls.

🎯 Final Objective

The goal is not simply to predict whether a payment will succeed.

The goal is to answer:

"A payment just failed. What should we do next to maximize the probability of recovering this revenue while minimizing unnecessary retries and customer friction?"

The complete intelligence loop is:

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
              ↓
       RECORD OUTCOME
              ↓
          LEARN
              │
              └──────────────► Future Decisions
👥 Team

Built for the Razorpay Hackathon.

⭐ Project Status

Current Status: 🚧 In Development

The project is being developed incrementally, with the ML pipeline, backend, frontend, and integration being built as separate components within a single monorepo.
