import streamlit as st
import pandas as pd
from tabulate import tabulate
import math
import numpy as np

def calculate_targets(current_sales, percentage_increase):
    targets_need_to_achieve = current_sales * (1 + percentage_increase / 100)
    revenue_target = math.floor(targets_need_to_achieve)  # Floor the revenue target
    return targets_need_to_achieve, revenue_target

def compute_metrics(df, current_sales, percentage_increase):
    revenue_target = math.floor(current_sales * (1 + percentage_increase / 100))  # Floor the revenue target

    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    df = df.sort_values(by=['cardholder_id', 'transaction_date'])

    df['transaction_duration'] = df.groupby('cardholder_id')['transaction_date'].diff().dt.days

    avg_duration_per_user = df.groupby('cardholder_id')['transaction_duration'].mean()

    avg_transaction_duration = math.ceil(avg_duration_per_user.mean())  # Ceil the average transaction duration

    grouped = df.groupby('cardholder_id').agg(
        Total_Transaction_Value=('transaction_amount', 'sum'),
        Total_Cashback_Value=('cashback_amount', 'sum'),
        Transaction_Count=('transaction_amount', 'count')
    ).reset_index()

    grouped['Avg_Transaction_Value'] = grouped['Total_Transaction_Value'] / grouped['Transaction_Count']
    grouped['Avg_Cashback_Value'] = grouped['Total_Cashback_Value'] / grouped['Transaction_Count']

    avg_order = grouped['Avg_Transaction_Value'].mean()
    avg_cashback = grouped['Avg_Cashback_Value'].mean()

    cashback_percentage = (avg_cashback / avg_order) * 100

    max_potential_revenue = math.floor(grouped['Total_Transaction_Value'].sum() - grouped['Total_Cashback_Value'].sum())  # Floor the maximum potential revenue

    if max_potential_revenue < revenue_target:
        st.error(f"Sorry, the revenue target of {revenue_target:,} ¥ cannot be achieved with the selected cluster.")
        st.error(f"The maximum potential revenue from this cluster is **{max_potential_revenue:,} ¥**.")
        st.error("Please choose another cluster or adjust the target.")
        return

    no_of_customers_to_target = math.ceil(revenue_target / (avg_order - avg_cashback))

    daily_revenue_per_customer = math.floor((avg_order - avg_cashback) / avg_transaction_duration)  # Floor the daily revenue per customer

    total_daily_revenue = math.floor(no_of_customers_to_target * daily_revenue_per_customer)  # Floor the total daily revenue

    days_to_achieve_target = math.ceil(revenue_target / total_daily_revenue)  # Ceil the days to achieve the target

    st.subheader("Data")
    st.write(f"**No of Customers in Cluster:** {grouped['cardholder_id'].nunique():,}")
    st.write(f"**Avg Order:** {math.floor(avg_order):,} ¥")  # Floor the average order value
    st.write(f"**Avg Cashback:** {math.floor(avg_cashback):,} ¥")  # Floor the average cashback value
    st.write(f"**Cashback %:** {round(cashback_percentage)}%")  # Rounded to nearest whole number
    st.write(f"**Avg Transaction Duration:** {avg_transaction_duration} days")  # Ceiled value

    st.subheader("Metrics Outputs")
    st.write(f"**No of Customers to Target:** {no_of_customers_to_target:,} (Approx.)")
    st.write(f"**Daily Revenue per Customer:** {daily_revenue_per_customer:,} ¥")
    st.write(f"**Total Daily Revenue from Targeted Customers:** {total_daily_revenue:,} ¥")
    st.write(f"**Days to Achieve Target:** {days_to_achieve_target} days")

    if days_to_achieve_target <= avg_transaction_duration:
        st.success(f"Yes, we can achieve the target in approximately {days_to_achieve_target} days with {no_of_customers_to_target:,} targeted customers!")
    else:
        st.warning(f"It may take longer than the average transaction duration to achieve the target with {no_of_customers_to_target:,} customers.")

    top_customers = grouped.sort_values(by='Avg_Transaction_Value', ascending=False).head(no_of_customers_to_target)

    st.subheader("Selected Cardholders")
    st.dataframe(top_customers[['cardholder_id', 'Avg_Transaction_Value', 'Avg_Cashback_Value']].reset_index(drop=True))

    sum_avg_transaction = math.floor(top_customers['Avg_Transaction_Value'].sum())  # Floor the sum of avg transaction values
    sum_avg_cashback = math.floor(top_customers['Avg_Cashback_Value'].sum())  # Floor the sum of avg cashback values
    profit_from_selected = math.floor(sum_avg_transaction - sum_avg_cashback)  # Floor the profit from selected customers

    st.write(f"**Selected Cardholder's Sum of Avg Transaction Value:** {sum_avg_transaction:,} ¥")
    st.write(f"**Selected Cardholder's Sum of Avg Cashback Value:** {sum_avg_cashback:,} ¥")
    st.write(f"**Profit from Selected Cardholders:** {profit_from_selected:,} ¥")

    if profit_from_selected >= revenue_target:
        st.success(f"Yes, we achieved the target successfully with the top {no_of_customers_to_target:,} customers based on highest Avg Transaction Value!")
    else:
        st.error(f"Sorry, we cannot achieve the target with the top {no_of_customers_to_target:,} customers based on highest Avg Transaction Value.")

def render():
    st.title("Cluster-Based Revenue Increase Strategy")
    st.markdown("This app analyzes transaction data to identify potential customer clusters for achieving revenue targets.")

    current_sales = st.sidebar.number_input("Enter Current Sales:", min_value=0, value=10000)
    percentage_increase = st.sidebar.number_input("Enter Percentage Increase:", min_value=0, max_value=100, value=20)

    targets_need_to_achieve, revenue_target = calculate_targets(current_sales, percentage_increase)

    st.markdown("---")
    st.subheader("Merchant Inputs")
    st.write(f"**Current Sales:** {math.floor(current_sales):,} ¥")
    st.write(f"**Targets Need to Achieve (Increased by {percentage_increase}%):** {math.floor(targets_need_to_achieve):,} ¥")
    st.write(f"**Revenue Target:** {revenue_target:,} ¥")

    st.markdown("---")
    st.markdown("## Select the cluster")

    cluster_names = ['Loyal High Spenders', 'At-Risk Low Spenders', 'Top VIPs', 'New or Infrequent Shoppers', 'Occasional Bargain Seekers']
    files = [f'./Data/cluster_calculation/hashed/Full Dataset of Cluster {i}.csv' for i in range(5)]

    st.markdown("""
        <style>
        .streamlit-button {
            min-height: auto;
            padding: 10px;
            font-size: 16px;
        }
        .stButton button {
            width: 100%;
            height: 100px;
        }
        </style>
        """, unsafe_allow_html=True)

    selected_cluster = None
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button('Loyal High Spenders'):
            selected_cluster = cluster_names[0]

    with col2:
        if st.button('At-Risk Low Spenders'):
            selected_cluster = cluster_names[1]

    with col3:
        if st.button('Top VIPs'):
            selected_cluster = cluster_names[2]

    with col4:
        if st.button('New or Infrequent Shoppers'):
            selected_cluster = cluster_names[3]

    with col5:
        if st.button('Occasional Bargain Seekers'):
            selected_cluster = cluster_names[4]

    if selected_cluster:
        file_index = cluster_names.index(selected_cluster)
        file = files[file_index]

        st.markdown(f"## Using {selected_cluster}")
        df = pd.read_csv(file)

        compute_metrics(df, current_sales, percentage_increase)
        st.markdown("---")