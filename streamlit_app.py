import streamlit as st
import pandas as pd
import plotly.express as px # Added for better charts
from blockchain_logic import MortgageChain

st.set_page_config(page_title="Blockchain Mortgage Ledger", layout="wide")

st.title("🏦 ELFakir's Blockchain Mortgage Annuity Calculator")
st.markdown("This app calculates monthly payments and stores the schedule in an immutable blockchain.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Loan Parameters")
principal = st.sidebar.number_input("Principal Amount ($)", min_value=1000, value=250000)
interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.1, value=6.5)# if you want as slider:  st.sidebar.slider("Annual Interest Rate (%)", 0.1, 15.0, 6.5)
years = st.sidebar.number_input("Loan Term (Years)", min_value=1, max_value=50, value=30)

# --- ANNUITY MATH ---
def calculate_annuity(P, annual_rate, years):
    r = (annual_rate / 100) / 12
    n = years * 12
    if r == 0: return P / n
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1)

monthly_payment = calculate_annuity(principal, interest_rate, years)

# --- BLOCKCHAIN GENERATION ---
if st.button("Generate Secure Mortgage Ledger"):
    my_loan_chain = MortgageChain()
    current_balance = principal
    monthly_rate = (interest_rate / 100) / 12
    
    ledger_for_display = []

    for i in range(1, (years * 12) + 1):
        interest_charge = current_balance * monthly_rate
        principal_repayment = monthly_payment - interest_charge
        current_balance -= principal_repayment
        
        data = {
            "Month": i,
            "Payment": round(monthly_payment, 2),
            "Principal_Paid": round(principal_repayment, 2),
            "Interest_Paid": round(interest_charge, 2),
            "Remaining_Balance": round(max(0, current_balance), 2)
        }
        
        my_loan_chain.add_payment(data)
        ledger_for_display.append({
            "Block_Hash": my_loan_chain.chain[-1].hash[:12] + "...",
            **data
        })

    # Convert to Dataframe for Visualization
    df = pd.DataFrame(ledger_for_display)

    # --- UI DISPLAY ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    col2.metric("Total Interest", f"${(df['Interest_Paid'].sum()):,.2f}")
    col3.metric("Total Cost", f"${(monthly_payment * years * 12):,.2f}")

    # --- VISUALIZATION ---
    st.subheader("Balance Over Time & Payment Breakdown")
    
    # Chart 1: Remaining Balance Curve
    fig_balance = px.area(df, x="Month", y="Remaining_Balance", title="Amortization Schedule (Remaining Principal)")
    st.plotly_chart(fig_balance, use_container_width=True)

    # Chart 2: Interest vs Principal
    fig_split = px.line(df, x="Month", y=["Principal_Paid", "Interest_Paid"], 
                        title="Principal vs. Interest Over Time",
                        labels={"value": "Amount ($)", "variable": "Type"})
    st.plotly_chart(fig_split, use_container_width=True)

    

    st.subheader("Immutable Blockchain Ledger")
    st.dataframe(df, use_container_width=True)
    st.success("✅ Ledger generated and cryptographically secured.")



