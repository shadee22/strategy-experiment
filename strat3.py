import streamlit as st
import pandas as pd
from tabulate import tabulate
import math
import numpy as np

def calculate_targets(current_sales, percentage_increase):
    targets_need_to_achieve = current_sales * (1 + percentage_increase / 100)
    revenue_target = targets_need_to_achieve
    return targets_need_to_achieve, revenue_target

def compute_metrics(df, current_sales, percentage_increase):
    # Calculate the new revenue target by increasing the current sales by the given percentage
    revenue_target = current_sales * (1 + percentage_increase / 100)

    # Convert transaction_date to datetime format if it's not already
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Sort by cardholder_id and transaction_date
    df = df.sort_values(by=['cardholder_id', 'transaction_date'])

    # Calculate the difference in days between consecutive transactions for each user
    df['transaction_duration'] = df.groupby('cardholder_id')['transaction_date'].diff().dt.days

    # Calculate the average transaction duration for each user
    avg_duration_per_user = df.groupby('cardholder_id')['transaction_duration'].mean()

    # Calculate the overall average transaction duration for the cluster
    avg_transaction_duration = avg_duration_per_user.mean()

    # Group by cardholder_id and calculate total transaction and cashback values
    grouped = df.groupby('cardholder_id').agg(
        Total_Transaction_Value=('transaction_amount', 'sum'),
        Total_Cashback_Value=('cashback_amount', 'sum'),
        Transaction_Count=('transaction_amount', 'count')
    ).reset_index()

    # Calculate average transaction value and cashback per user
    grouped['Avg_Transaction_Value'] = grouped['Total_Transaction_Value'] / grouped['Transaction_Count']
    grouped['Avg_Cashback_Value'] = grouped['Total_Cashback_Value'] / grouped['Transaction_Count']

    avg_order = grouped['Avg_Transaction_Value'].mean()
    avg_cashback = grouped['Avg_Cashback_Value'].mean()

    # Calculate cashback percentage
    cashback_percentage = (avg_cashback / avg_order) * 100

    # Calculate the required number of customers to target
    no_of_customers_to_target = math.ceil(revenue_target / (avg_order - avg_cashback))

    # Calculate Daily Revenue per Customer
    daily_revenue_per_customer = (avg_order - avg_cashback) / avg_transaction_duration

    # Calculate Total Daily Revenue from All Targeted Customers
    total_daily_revenue = no_of_customers_to_target * daily_revenue_per_customer

    # Calculate Days to Achieve Target
    days_to_achieve_target = revenue_target / total_daily_revenue

    # Display the metrics in Streamlit
    st.subheader("Data")
    st.write(f"**No of Customers in Cluster:** {grouped['cardholder_id'].nunique()}")
    st.write(f"**Avg Order:** {round(avg_order, 2)}")
    st.write(f"**Avg Cashback:** {round(avg_cashback, 2)}")
    st.write(f"**Cashback %:** {round(cashback_percentage, 2)}%")
    st.write(f"**Avg Transaction Duration:** {round(avg_transaction_duration, 2)} days")

    st.subheader("Metrics Outputs")
    st.write(f"**No of Customers to Target:** {no_of_customers_to_target} (Approx.)")
    st.write(f"**Daily Revenue per Customer:** {daily_revenue_per_customer:.2f}")
    st.write(f"**Total Daily Revenue from Targeted Customers:** {total_daily_revenue:.2f}")
    st.write(f"**Days to Achieve Target:** {round(days_to_achieve_target, 2)} days")

    if days_to_achieve_target <= avg_transaction_duration:
        st.success(f"Yes, we can achieve the target in approximately {round(days_to_achieve_target, 2)} days with {no_of_customers_to_target} targeted customers!")
    else:
        st.warning(f"It may take longer than the average transaction duration to achieve the target with {no_of_customers_to_target} customers.")

    # Select top customers based on highest average transaction value
    top_customers = grouped.sort_values(by='Avg_Transaction_Value', ascending=False).head(no_of_customers_to_target)

    # Display the selected cardholders with only required columns
    st.subheader("Selected Cardholders")
    st.dataframe(top_customers[['cardholder_id', 'Avg_Transaction_Value', 'Avg_Cashback_Value']].reset_index(drop=True))

    # Calculate the sums for the selected cardholders
    sum_avg_transaction = np.round(top_customers['Avg_Transaction_Value'].sum(), 2)
    sum_avg_cashback = np.round(top_customers['Avg_Cashback_Value'].sum(), 2)
    profit_from_selected = sum_avg_transaction - sum_avg_cashback

    st.write(f"**Selected Cardholder's Sum of Avg Transaction Value:** {sum_avg_transaction}")
    st.write(f"**Selected Cardholder's Sum of Avg Cashback Value:** {sum_avg_cashback}")
    st.write(f"**Profit from Selected Cardholders:** {profit_from_selected}")

    if profit_from_selected >= revenue_target:
        st.success(f"Yes, we achieved the target successfully with the top {no_of_customers_to_target} customers based on highest Avg Transaction Value!")
    else:
        st.error(f"Sorry, we cannot achieve the target with the top {no_of_customers_to_target} customers based on highest Avg Transaction Value.")
def render():
    st.title("Cluster-Based Revenue Increase Strategy")
    st.markdown("This app analyzes transaction data to identify potential customer clusters for achieving revenue targets.")

    current_sales = st.sidebar.number_input("Enter Current Sales:", min_value=0, value=10000)
    percentage_increase = st.sidebar.number_input("Enter Percentage Increase:", min_value=0, max_value=100, value=20)
    # top_n_customers = st.sidebar.number_input("Enter Top N Customers to Target:", min_value=1, value=5)

    # Calculate and display merchant inputs
    targets_need_to_achieve, revenue_target = calculate_targets(current_sales, percentage_increase)

    st.markdown("---")
    st.subheader("Merchant Inputs")
    st.write(f"**Current Sales:** {current_sales}")
    st.write(f"**Targets Need to Achieve (Increased by {percentage_increase}%):** {targets_need_to_achieve}")
    st.write(f"**Revenue Target:** {revenue_target}")

    st.markdown("---")
    st.markdown("## Select the cluster")

    cluster_names = ['Loyal High Spenders', 'At-Risk Low Spenders', 'Top VIPs', 'New or Infrequent Shoppers', 'Occasional Bargain Seekers']
    files = [f'./Data/cluster_calculation/hashed/Full Dataset of Cluster {i}.csv' for i in range(5)]

    # Custom CSS to ensure all buttons are of the same height
    st.markdown("""
        <style>
        .streamlit-button {
            min-height: auto;
            padding: 10px;
            font-size: 16px;
        }
        .stButton button {
            width: 100%;
            height: 100px; /* Adjust this value to set the height */
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

