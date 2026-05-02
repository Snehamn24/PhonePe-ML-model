import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="PhonePe Insights Dashboard", layout="wide")

st.title("📊 PhonePe Transaction Insights Dashboard")

# -------------------------------
# DB CONNECTION
# -------------------------------
conn = sqlite3.connect("phonepe.db")

def load(query):
    return pd.read_sql(query, conn)

# -------------------------------
# LOAD DATA (REAL COLAB DATA)
# -------------------------------
df_trans = load("SELECT * FROM transactions")
df_user = load("SELECT * FROM users")
df_ins = load("SELECT * FROM insurance")

#st.write("Transaction columns:", df_trans.columns)

# -------------------------------
# SAFETY CHECK
# -------------------------------
if df_trans.empty:
    st.error("No data found in database")
    st.stop()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("Filters")

year = st.sidebar.selectbox("Select Year", sorted(df_trans["year"].unique()))
state = st.sidebar.selectbox("Select State", sorted(df_trans["state"].unique()))

# filtered dataset (for KPI only)
filtered_df = df_trans[
    (df_trans["year"] == year) &
    (df_trans["state"] == state)
]

# -------------------------------
# KPI (FILTERED VIEW)
# -------------------------------
st.subheader("📌 Filtered KPI (User Selection)")

col1, col2 = st.columns(2)

col1.metric("Transactions", int(filtered_df["count"].sum()))
col2.metric("Amount", int(filtered_df["amount"].sum()))

# -------------------------------
# GLOBAL INSIGHT - STATES (IMPORTANT FIX)
# -------------------------------
st.subheader("🏆 Top 10 States (Overall)")

state_rank = df_trans.groupby("state")["amount"].sum().sort_values(ascending=False).head(10)

st.bar_chart(state_rank)

# -------------------------------
# GLOBAL INSIGHT - USER BRANDS (FIX FOR XIAOMI ISSUE)
# -------------------------------
st.subheader("📱 Top Device Brands (Overall Users)")

brand_rank = df_user.groupby("brand")["count"].sum().sort_values(ascending=False)

st.bar_chart(brand_rank)

# -------------------------------
# YEARLY TREND
# -------------------------------
st.subheader("📈 Yearly Transaction Trend")

yearly = df_trans.groupby("year")["amount"].sum().sort_values()

st.line_chart(yearly)

# -------------------------------
# QUARTER TREND
# -------------------------------
st.subheader("📊 Quarter-wise Trend")

quarter = df_trans.groupby("quarter")["amount"].sum()

st.bar_chart(quarter)

# -------------------------------
# TRANSACTION TYPE DISTRIBUTION
# -------------------------------
st.subheader("💳 Transaction Type Distribution")

fig, ax = plt.subplots()
sns.countplot(data=df_trans, x="transaction_type" if "transaction_type" in df_trans.columns else "type", ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

# -------------------------------
# INSURANCE TREND
# -------------------------------
st.subheader("🛡 Insurance Trend")

ins = df_ins.groupby("year")["amount"].sum()

st.line_chart(ins)

# -------------------------------
# RAW DATA
# -------------------------------
st.subheader("📄 Raw Data (Transactions)")
st.dataframe(df_trans.head())

conn.close()