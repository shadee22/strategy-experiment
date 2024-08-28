import streamlit as st
import pandas as pd
import math
import numpy as np

def calculate_targets(current_sales, percentage_increase):
    revenue_target = current_sales * (1 + percentage_increase / 100)
    return revenue_target

def compute_metrics(df, current_sales, percentage_increase, required_days_to_achieve_target):
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

    # Calculate Daily Revenue per Customer
    daily_revenue_per_customer = (avg_order - avg_cashback) / avg_transaction_duration

    # Calculate the number of customers to target to achieve the revenue target within the required days
    no_of_customers_to_target = math.ceil(revenue_target / (daily_revenue_per_customer * required_days_to_achieve_target))

    # Calculate Total Daily Revenue from All Targeted Customers
    total_daily_revenue = no_of_customers_to_target * daily_revenue_per_customer

    # Calculate Days to Achieve Target
    days_to_achieve_target = revenue_target / total_daily_revenue

    # Round the results for better display
    avg_order_rounded = round(avg_order, 2)
    avg_cashback_rounded = round(avg_cashback, 2)
    cashback_percentage_rounded = round(cashback_percentage, 2)
    days_to_achieve_target_rounded = round(days_to_achieve_target, 2)
    avg_transaction_duration_rounded = round(avg_transaction_duration, 2)

    # Display metrics in Streamlit
    st.subheader("Metrics Outputs")
    st.write(f"**No of Customers to Target to Achieve Revenue Target in {required_days_to_achieve_target} Days:** {no_of_customers_to_target} (Approx.)")
    st.write(f"**Daily Revenue per Customer:** {daily_revenue_per_customer:.2f}")
    st.write(f"**Total Daily Revenue from Targeted Customers:** {total_daily_revenue:.2f}")
    st.write(f"**Estimated Days to Achieve Target with Current Average Transaction Duration:** {days_to_achieve_target_rounded} days")

    if days_to_achieve_target_rounded <= required_days_to_achieve_target:
        st.success(f"Yes, we can achieve the target in approximately {days_to_achieve_target_rounded} days with {no_of_customers_to_target} targeted customers!")
    else:
        st.warning(f"It may take longer than {required_days_to_achieve_target} days to achieve the target with {no_of_customers_to_target} customers.")

def render():
    st.title("Cluster-Based Revenue Increase Strategy")
    st.markdown("This app analyzes transaction data to identify potential customer clusters for achieving revenue targets.")

    current_sales = st.sidebar.number_input("Enter Current Sales:", min_value=0, value=10000)
    percentage_increase = st.sidebar.number_input("Enter Percentage Increase:", min_value=0, max_value=100, value=20)
    required_days_to_achieve_target = st.sidebar.number_input("Enter Days to Achieve Target:", min_value=1, value=10)

    # Calculate and display merchant inputs
    revenue_target = calculate_targets(current_sales, percentage_increase)

    st.markdown("---")
    st.subheader("Merchant Inputs")
    st.write(f"**Current Sales:** {current_sales}")
    st.write(f"**Targets Need to Achieve (Increased by {percentage_increase}%):** {revenue_target}")
    st.write(f"**Revenue Target:** {revenue_target}")

    st.markdown("---")
    st.markdown("## Select the cluster")

    cluster_names = ['Loyal High Spenders', 'At-Risk Low Spenders', 'Top VIPs', 'New or Infrequent Shoppers', 'Occasional Bargain Seekers']
    files = [f'./Data/cluster_calculation/hashed/Full Dataset of Cluster {i}.csv' for i in range(5)]

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
        
        compute_metrics(df, current_sales, percentage_increase, required_days_to_achieve_target)
        st.markdown("---")

# Run the Streamlit app
if __name__ == "__main__":
    render()
