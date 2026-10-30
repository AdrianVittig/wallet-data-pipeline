from decimal import Decimal

import pandas as pd
import streamlit as st

from analytics import load_report
from pipeline.config import load_database_settings

st.set_page_config(page_title="Wallet analytics", layout="wide")
st.title("Wallet Analytics")

db_settings = load_database_settings()
monthly = load_report(db_settings, "monthly_wallet_summary.sql")
categories = load_report(db_settings, "spending_by_category.sql")

if monthly.empty:
    st.info("No transfer data is available yet.")
    st.stop()

wallets = monthly[["source", "wallet_iban"]].drop_duplicates()
source = st.selectbox("API source", wallets["source"].unique())

source_wallets = wallets.loc[
    wallets["source"] == source, "wallet_iban"
]
wallet_iban = st.selectbox("Wallet", source_wallets)

monthly_wallet = monthly.loc[
    (monthly["source"] == source)
    & (monthly["wallet_iban"] == wallet_iban)
].sort_values("month")

category_wallet = categories.loc[
    (categories["source"] == source)
    & (categories["wallet_iban"] == wallet_iban)
]

incoming = sum(monthly_wallet["incoming_amount"], Decimal("0.00"))
outgoing = sum(monthly_wallet["outgoing_amount"], Decimal("0.00"))
net = incoming - outgoing

col1, col2, col3 = st.columns(3)
col1.metric("Incoming", f"{incoming:,.2f}")
col2.metric("Outgoing", f"{outgoing:,.2f}")
col3.metric("Net flow", f"{net:,.2f}")

st.subheader("Monthly cash flow")
monthly_chart = monthly_wallet[
    ["month", "incoming_amount", "outgoing_amount"]
].copy()
monthly_chart["month"] = pd.to_datetime(monthly_chart["month"])
monthly_chart["incoming_amount"] = (
    monthly_chart["incoming_amount"].astype(float))
monthly_chart["outgoing_amount"] = (
    monthly_chart["outgoing_amount"].astype(float)
)

st.bar_chart(
    monthly_chart,
    x="month",
    y=["incoming_amount","outgoing_amount"],
    stack=False
)

st.subheader("Outgoing spending by category")
if category_wallet.empty:
    st.info("No outgoing transfers for this wallet.")
else:
    category_chart = category_wallet[["category", "spent_amount"]].copy()
    category_chart["spent_amount"] = (
        category_chart["spent_amount"].astype(float))
    st.bar_chart(category_chart, x="category", y="spent_amount")

st.subheader("Exact monthly values")
exact_monthly = monthly_wallet.copy()
for column in ("incoming_amount", "outgoing_amount", "net_amount"):
    exact_monthly[column] = exact_monthly[column].map(str)
st.dataframe(exact_monthly, hide_index=True)

st.subheader("Exact category values")
exact_categories = category_wallet.copy()
exact_categories["spent_amount"] = exact_categories["spent_amount"].map(str)
st.dataframe(exact_categories, hide_index=True)