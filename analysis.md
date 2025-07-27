# Ethereum Wallet Risk Scoring - Analysis

## 📊 1. Data Collection Method

The dataset used was obtained from Etherscan’s Ethereum transaction history export. Each transaction record contains detailed metadata such as:

- Block and transaction hashes
- Sender (`from`) and receiver (`to`) addresses
- Value of the transaction (in Wei)
- Gas used and gas price
- Transaction status and method invoked
- The wallet ID associated with each transaction

This dataset contains 6,422 transactions involving various Ethereum wallets.

---

## 🧠 2. Feature Selection Rationale

To assess wallet risk, we aggregated transaction-level data into wallet-level features. The features selected were:

| Feature                 | Description                                                    | Rationale                                          |
| ----------------------- | -------------------------------------------------------------- | -------------------------------------------------- |
| `total_transactions`    | Total number of transactions a wallet has participated in      | Active wallets are often more reliable             |
| `total_eth_received`    | Total ETH (in Ether) received by the wallet                    | Receiving large amounts can imply trust            |
| `total_eth_sent`        | Total ETH sent                                                 | Helps in identifying inflow/outflow balance        |
| `unique_to_addresses`   | Number of unique addresses interacted with                     | More unique addresses = more engagement            |
| `contract_interactions` | Count of transactions with contracts (non-null function names) | Identifies DeFi or DApp usage                      |
| `failed_transactions`   | Number of failed transactions                                  | High failure rates may signal risk or bot behavior |
| `contract_creation`     | Whether the wallet has created contracts                       | May imply developer use or complexity              |

All nulls were handled appropriately and features were aggregated by the `wallet_id`.

---

## 🧮 3. Scoring Method

We used a **rule-based scoring model** that assigns each wallet a score between 0 and 1000. The steps include:

1. **Normalization**: Each feature was scaled using MinMaxScaler to bring values to a 0–1 range.
2. **Weighted Sum**: Weights were applied to features to emphasize importance. Example weights:

   - +2 for total transactions
   - +3 for ETH received
   - −2 for failed transactions
   - +1 for contract interactions
   - +2 for ETH sent
   - +1 for number of unique addresses

3. **Score Calculation**:  
   `score = weighted_sum_of_scaled_features × 1000 / total_weight`

   Final scores were clipped to remain between 0–1000.

This method ensures a linear, interpretable scoring system based on transaction behavior.

---

## 📌 4. Justification of Risk Indicators

- **High transaction volume** → Suggests legitimate usage.
- **More ETH received** → Indicates trust and usage in economic activity.
- **Frequent failed transactions** → Potentially signals bots, attackers, or poorly coded contracts.
- **Contract interaction** → Suggests sophistication; could be a positive or a risky signal depending on context.
- **Contract creation** → Indicates complexity; often not used by regular users.

These features are commonly used in wallet reputation, fraud detection, and on-chain analytics by Web3 security tools.

---

## ✅ Output

Each wallet received a final risk score (0–1000) and a CSV file named `wallet_risk_scores.csv` was generated with the following columns:

- `wallet_id`
- `risk_score`

This can be used for visualizations, dashboarding, or integration into a larger blockchain analytics system.

---
