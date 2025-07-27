# 🧠 Ethereum Wallet Risk Scoring

This project analyzes Ethereum wallet transaction data and assigns each wallet a **risk score between 0 and 1000**. The score helps identify potentially suspicious wallets based on behavioral indicators such as transaction volume, failed attempts, and contract interaction.

---
## 🔍 Objective

To build a scoring model that evaluates the **risk level** of Ethereum wallets using on-chain transactional behavior.

---

## 🛠️ How It Works

### 1. **Data Collection**
- Source: [Etherscan.io](https://etherscan.io/)
- We used a sample CSV containing 6,422 Ethereum transactions including:
  - `from`, `to`, `value`, `gasUsed`, `functionName`, etc.

### 2. **Feature Extraction**
- Transactions were grouped by wallet.
- Extracted features include:
  - Total ETH received/sent
  - Number of unique `to` addresses
  - Contract interaction count
  - Failed transactions
  - Contract creation flag

### 3. **Risk Scoring Logic**
- Features were scaled using `MinMaxScaler`.
- A **weighted scoring system** was applied based on:
  - +2: Total Transactions
  - +3: ETH Received
  - −2: Failed Transactions
  - +1: Contract Interactions
  - +2: ETH Sent
  - +1: Unique Interactions
- Score range: **0 to 1000**

### 4. **Output**
- Risk scores are saved to `wallet_risk_scores.csv` with:
  - `wallet_id`
  - `risk_score`

---
