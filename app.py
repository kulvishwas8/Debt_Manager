# interactive debt manager
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -----------------------------
# Helper Functions
# -----------------------------


def calculate_emi(principal, annual_rate, tenure_months):
    """ Calculate EMI based on loan parameters """
    monthly_rate = annual_rate / (12 * 100)
    emi = (principal * monthly_rate * ((1 + monthly_rate)**tenure_months)
           ) / (((1 + monthly_rate)**tenure_months) - 1)
    return emi


def generate_amortization_schedule(principal, annual_rate, tenure_months, start_date, lumpsum_payments):
    """Generate amortization schedule including lumpsum payments"""
    schedule = []
    current_balance = principal
    monthly_rate = annual_rate / (12 * 100)
    emi = calculate_emi(principal, annual_rate, tenure_months)

    current_date = start_date
    for month in range(1, tenure_months + 1):
        interest = current_balance * monthly_rate
        principal_component = emi - interest
        current_balance -= principal_component

        # Apply lumpsum payments (if any)
        for l_date, amount in lumpsum_payments.items():
            if current_date.date() == datetime.strptime(l_date, "%Y-%m-%d").date():
                current_balance -= amount
                if current_balance < 0:
                    current_balance = 0

        schedule.append({
            "Month": month,
            "Payment Date": current_date.strftime("%Y-%m-%d"),
            "EMI": round(emi, 2),
            "Principal Paid": round(principal_component, 2),
            "Interest Paid": round(interest, 2),
            "Balance": round(max(current_balance, 0), 2)
        })

        current_date += timedelta(days=30)  # approximate monthly increment
        if current_balance <= 0:
            break

    df = pd.DataFrame(schedule)
    return df


def load_visitor_count():
    try:
        with open("visitor_count.txt", "r") as f:
            count = int(f.read().strip())
    except FileNotFoundError:
        count = 0
    return count


def increment_visitor_count():
    count = load_visitor_count() + 1
    with open("visitor_count.txt", "w") as f:
        f.write(str(count))
    return count


# -----------------------------
# Streamlit App Configuration
# -----------------------------
st.set_page_config(page_title="Interactive Debt Manager", layout="centered")

st.title(" Debt Manager ")

st.markdown(
    f"Debt is a silent promise etched in trust—its weight not just financial, but moral.")
st.markdown(
    f"To repay it on time is to honor the invisible thread that binds integrity to obligation.")

# Increment visitor counter

st.sidebar.markdown(f" How to use this App?")
st.sidebar.markdown(f" 1)Enter Loan Details.")
st.sidebar.markdown(
    f" 2)Enter lumpsum if you are paying any additional amount.")
st.sidebar.markdown(f" 3)You will get amortization schedule with graph.")


st.sidebar.markdown(
    f"Here are three successful methods to get out of debt early")
st.sidebar.markdown(
    f" 1)Avalanche Method:-Prioritize paying off debts with the highest interest rates first to minimize total interest paid.")
st.sidebar.markdown(
    f" 2)Snowball Method:-Start by paying off your smallest debts first to gain quick wins.")
st.sidebar.markdown(
    f" 3)Debt Consolidation:-Combine multiple debts into a single loan with better terms to streamline payments.")


visitor_count = increment_visitor_count()
st.sidebar.markdown(f"   Visitor Count:   {visitor_count}")

# -----------------------------
# User Inputs
# -----------------------------


st.header("Loan Details")

col1, col2, col3 = st.columns(3)
with col1:
    principal = st.number_input(
        "Loan Amount (₹)", min_value=0.0, value=500000.0, step=1000.0)
with col2:
    annual_rate = st.number_input(
        "Annual Interest Rate (%)", min_value=0.0, value=8.5, step=0.1)
with col3:
    tenure_months = st.number_input(
        "Tenure (months)", min_value=1, value=60, step=1)

start_date = st.date_input("Date of Taking Debt", datetime.today())

st.write("### Lumpsum Payments")
lumpsum_payments = {}
num_lumpsums = st.number_input(
    "How many lumpsum payments?(Enter Amount in multiples of EMI e.g 1-10)", min_value=0, max_value=10, step=1)

for i in range(num_lumpsums):
    c1, c2 = st.columns(2)
    with c1:
        lumpsum_date = st.date_input(
            f"Lumpsum Date {i+1}", datetime.today(), key=f"l_date_{i}")
    with c2:
        lumpsum_amount = st.number_input(
            f"Lumpsum Amount {i+1} (₹)", min_value=0.0, value=0.0, key=f"l_amt_{i}")
    lumpsum_payments[lumpsum_date.strftime("%Y-%m-%d")] = lumpsum_amount

# -----------------------------
# Generate Amortization Schedule
# -----------------------------
if st.button(" Generate Amortization Schedule"):
    schedule_df = generate_amortization_schedule(principal, annual_rate, tenure_months, datetime.combine(
        start_date, datetime.min.time()), lumpsum_payments)
    st.success(" Amortization Schedule Generated Successfully!")
    st.dataframe(schedule_df)

    total_interest = schedule_df["Interest Paid"].sum()
    total_principal = schedule_df["Principal Paid"].sum()
    st.markdown(f" Total Interest Paid: ₹{total_interest:,.2f}")
    st.markdown(f" Total Principal Paid: ₹{total_principal:,.2f}")
    st.markdown(
        f"Loan Fully Paid by: {schedule_df.iloc[-1]['Payment Date']}")

    st.line_chart(schedule_df[["Principal Paid", "Interest Paid"]])


st.caption(
    " Developed by kulvishwas8| Streamlit Debt Management App ")
