
# EconoCausal
### Dynamic Pricing Using Double Machine Learning and Causal AI

## 1. Project Introduction

EconoCausal is a data-driven dynamic pricing and discount
optimization system that uses Causal Machine Learning to
identify the impact of discounts on customer purchasing
behaviour.

The system estimates individual treatment effects and
recommends suitable discounts to improve business outcomes.

## 2. Problem Statement

Traditional discount strategies provide similar discounts
to different customers without understanding their
individual purchasing behaviour.

This can result in unnecessary discount expenses and
inefficient marketing campaigns.

EconoCausal solves this problem using causal inference
and personalized discount recommendations.

## 3. Objectives

- Analyze customer campaign data.
- Estimate individual treatment effects.
- Compare different discount strategies.
- Optimize customer-level discount allocation.
- Detect changes in incoming customer data.

## 4. Technology Stack

- Python
- Pandas and NumPy
- EconML
- DoWhy
- FastAPI
- React.js
- JavaScript
- HTML and CSS
- Matplotlib
- Git and GitHub

## 5. Project Modules

1. Customer Data Upload and Validation
2. Exploratory Data Analysis
3. Causal Graph and Confounder Identification
4. Double Machine Learning
5. Customer Treatment Effect Estimation
6. Discount Optimization
7. Data Drift Detection using PSI
8. React Dashboard and FastAPI Integration

## 6. How to Run

### Backend

Activate virtual environment:

.venv\Scripts\activate

Start backend:

uvicorn backend.main:app --reload

### Frontend

Open another terminal:

cd frontend
npm install
npm run dev

### API Documentation

http://127.0.0.1:8000/docs

## 7. Expected Outputs

- Customer-level treatment effects
- Optimized discount recommendations
- Discount allocation summary
- Data drift warnings
- Interactive dashboard

## 8. Future Scope

- Real-time customer data integration
- Advanced causal models
- Automated model retraining
- Cloud deployment
- Continuous data monitoring

## 9. Conclusion

EconoCausal demonstrates how causal machine learning
can support personalized pricing decisions and
improve customer campaign efficiency.
