import requests
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

ETHERSCAN_API_KEY = 'DSUHRJ5E5G1WTBRH2WRWZ1R61UKVIQ1BXD'
df = pd.read_csv('Wallet id.csv')
wallet_list = df['wallet_id'].tolist()

def fetch_transactions(wallet_address):
    url=(
        f"https://api.etherscan.io/api"
        f"?module=account"
        f"&action=txlist"
        f"&address={wallet_address}"
        f"&startblock=0"
        f"&endblock=99999999"
        f"&sort=asc"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    
    if data["status"] != "1":
        raise Exception(f"Error fetching for {wallet_address}: {data['message']}")
        return []
    
    return data["result"]

# To store all transactions
all_transactions = []

# Iterate through each wallet address and fetch transactions
for i, wallet in enumerate(wallet_list):
    print(f"Fetching for wallet {i+1}/{len(wallet_list)}: {wallet}")
    txns = fetch_transactions(wallet)
    
    for tx in txns:
        tx["wallet_id"] = wallet
        
    all_transactions.extend(txns)
    
    #sleep to avoid API rate limits
    time.sleep(0.3)
    
# Convert to DataFrame
tx_df = pd.DataFrame(all_transactions)

# Save to CSV
tx_df.to_csv('wallet_transactions.csv', index=False)
print("Saved all transactions to 'wallet_transactions.csv' ")


#FEATURE EXTRACTION
df1 = pd.read_csv('wallet_transactions.csv')
print(df1.info())

#Conversion of 'value' to float
df1["value"] = df1["value"].astype(float) / 10 ** 16
# Convert 'timestamp' to datetime
df1["timestamp"] = pd.to_datetime(df1["timeStamp"], unit='s')
#Add helper columns to simplify direction
df1['is_sender'] = df1['from'] == df1['wallet_id']
df1['is_receiver'] = df1['to'] == df1['wallet_id']

#Group by wallet
features = []

for wallet, group in df1.groupby("wallet_id"):
    total_tx = len(group)
    sent_tx = group[group["is_sender"]]
    received_tx = group[group["is_receiver"]]
    
    total_sent = sent_tx["value"].sum()
    total_received = received_tx["value"].sum()
    
    avg_sent = sent_tx["value"].mean() if not sent_tx.empty else 0
    avg_received = received_tx["value"].mean() if not received_tx.empty else 0
    
    unique_to = sent_tx["to"].nunique()
    unique_from = received_tx["from"].nunique()
    
    failed_tx = group[group["isError"] == 1]
    failed_ratio = len(failed_tx) / total_tx if total_tx > 0 else 0
    
    contract_calls = group["contractAddress"].notnull().sum()
    
    features.append({
        "wallet_id": wallet,
        "total_transactions": total_tx,
        "total_sent": total_sent,
        "total_received": total_received,
        "avg_sent": avg_sent,
        "avg_received": avg_received,
        "unique_to": unique_to,
        "unique_from": unique_from,
        "failed_tx_count": len(failed_tx),
        "failed_tx_ratio": failed_ratio,
        "contract_interactions": contract_calls
    })
    
features_df = pd.DataFrame(features)
print(features_df.head())

#Feature Scaling
wallet_ids = features_df['wallet_id']
x = features_df.drop(columns=['wallet_id'], axis=1)

scaler = MinMaxScaler()
x_scaled  = scaler.fit_transform(x)

scaled_df = pd.DataFrame(x_scaled, columns = x.columns)
scaled_df['wallet_id'] = wallet_ids

print(scaled_df.head())

#Score Calculation

#weight assignment
feature_weights = {
    "total_sent":0.1,
    "total_received":-0.1,
    "total_transactions":0.05,
    "avg_sent":0.15,
    "failed_tx_ratio":0.25,
    "unique_to":0.05,
    "unique_from":0.05,
    "contract_interactions":0.1,
    "failed_tx_count":0.2
}

#Rule based scoring Model

# Use only features that are in our weight dictionary
used_features = list(feature_weights.keys())
X = scaled_df[used_features]

# Convert weights into numpy array
weights = np.array([feature_weights[feat] for feat in used_features])

# Compute weighted sum
risk_scores = X.values.dot(weights)

# Normalize to 0–1000 range
min_score = risk_scores.min()
max_score = risk_scores.max()
normalized_scores = 1000 * (risk_scores - min_score) / (max_score - min_score)

# Final DataFrame
scaled_df['risk_score'] = normalized_scores.round(2)

# Sort by highest risk
risk_ranked = scaled_df.sort_values(by='risk_score', ascending=False)

# Show top 5 risky wallets
print(risk_ranked[['wallet_id', 'risk_score']].head())
# Save the risk scores to a CSV file
risk_ranked[['wallet_id', 'risk_score']].to_csv("wallet_risk_scores.csv", index=False)

print("wallet_risk_scores.csv saved successfully.")

