import streamlit as st
import pandas as pd
import math
import numpy as np

def calculate_targets(current_sales, percentage_increase):
    revenue_target = math.floor(current_sales * (1 + percentage_increase / 100))  # Floor the revenue target
    return revenue_target

def compute_metrics(df, current_sales, percentage_increase, required_days_to_achieve_target):
    # Calculate the new revenue target by increasing the current sales by the given percentage
    revenue_target = math.floor(current_sales * (1 + percentage_increase / 100))  # Floor the revenue target

    # Convert transaction_date to datetime format if it's not already
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Sort by cardholder_id and transaction_date
    df = df.sort_values(by=['cardholder_id', 'transaction_date'])

    # Calculate the difference in days between consecutive transactions for each user
    df['transaction_duration'] = df.groupby('cardholder_id')['transaction_date'].diff().dt.days

    # Calculate the average transaction duration for each user
    avg_duration_per_user = df.groupby('cardholder_id')['transaction_duration'].mean()

    # Calculate the overall average transaction duration for the cluster
    avg_transaction_duration = math.ceil(avg_duration_per_user.mean())  # Ceil the average transaction duration

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

    # Calculate the maximum potential revenue from the entire cluster
    max_potential_revenue = math.floor(grouped['Total_Transaction_Value'].sum() - grouped['Total_Cashback_Value'].sum())  # Floor the maximum potential revenue

    # Check if the revenue target is achievable with the selected cluster
    if max_potential_revenue < revenue_target:
        st.error(f"Sorry, the revenue target of {revenue_target:,} ¥ cannot be achieved with the selected cluster.")
        st.error(f"The maximum potential revenue from this cluster is **{max_potential_revenue:,} ¥**.")
        st.error("Please choose another cluster or adjust the target.")
        return

    # Calculate Daily Revenue per Customer
    daily_revenue_per_customer = math.floor((avg_order - avg_cashback) / avg_transaction_duration)  # Floor the daily revenue per customer

    # Calculate the maximum possible revenue within the required days
    max_possible_revenue_within_days = math.floor(daily_revenue_per_customer * required_days_to_achieve_target * len(grouped))  # Floor the maximum possible revenue within days

    # Check if the revenue target can be achieved within the required days
    if max_possible_revenue_within_days < revenue_target:
        st.error(f"Sorry, the revenue target of {revenue_target:,} ¥ cannot be achieved within {math.ceil(required_days_to_achieve_target)} days using the selected cluster.")
        st.error(f"The maximum possible revenue within this period is **{max_possible_revenue_within_days:,} ¥**.")
        st.error("Please choose another cluster or adjust the target.")
        return

    # Calculate the number of customers to target to achieve the revenue target within the required days
    no_of_customers_to_target = math.ceil(revenue_target / (daily_revenue_per_customer * required_days_to_achieve_target))

    # Calculate Total Daily Revenue from All Targeted Customers
    total_daily_revenue = math.floor(no_of_customers_to_target * daily_revenue_per_customer)  # Floor the total daily revenue

    # Calculate Days to Achieve Target
    days_to_achieve_target = math.ceil(revenue_target / total_daily_revenue)  # Ceil the days to achieve the target
    cashback_percentage = (avg_cashback / avg_order) * 100  
    # Custom CSS to style the metrics
    st.markdown("""
    <style>
        .metric-container {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
        .metric-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .metric-delta {
            color: #28a745;
            font-size: 14px;
        }
    </style>
    """, unsafe_allow_html=True)
    # Function to create a custom metric with border
    def custom_metric(label, value, delta):
        return f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta">↑ {delta}</div>
        </div>
        """
    with st.expander(f"Summary Statistics of the cluster"):
        st.write(f"**No of Customers in Cluster:** {grouped['cardholder_id'].nunique():,}")
        st.write(f"**Avg Order:** {math.floor(avg_order):,} ¥")  # Floor the average order value
        st.write(f"**Avg Cashback:** {math.floor(avg_cashback):,} ¥")  # Floor the average cashback value
        st.write(f"**Cashback %:** {round(cashback_percentage)}%")  # Rounded to nearest whole number
        st.write(f"**Avg Transaction Duration:** {avg_transaction_duration} days")  # Ceiled value
    # Display metrics in Streamlit
    st.subheader("Metrics Outputs")
    st.write(f"**No of Customers to Target to Achieve Revenue Target in {math.ceil(required_days_to_achieve_target)} Days:** {no_of_customers_to_target:,} (Approx.)")
    st.write(f"**Daily Revenue per Customer:** {daily_revenue_per_customer:,} ¥")
    st.write(f"**Total Daily Revenue from Targeted Customers:** {total_daily_revenue:,} ¥")
    st.write(f"**Estimated Days to Achieve Target with Current Average Transaction Duration:** {days_to_achieve_target:,} days")
    
    # Create two columns
    # col1, col2 = st.columns(2)

    # # First column
    # with col1:
    #     st.metric(
    #         label="No. of Customers to Target",
    #         value=f"{no_of_customers_to_target:,}",
    #         delta=f"in {math.ceil(required_days_to_achieve_target)} Days"
    #     )
    #     st.metric(
    #         label="Daily Revenue per Customer",
    #         value=f"{daily_revenue_per_customer:,} ¥"
    #     )

    # # Second column
    # with col2:
    #     st.metric(
    #         label="Total Daily Revenue",
    #         value=f"{total_daily_revenue:,} ¥",
    #         delta="from Targeted Customers"
    #     )
    #     st.metric(
    #         label="Est. Days to Achieve Target",
    #         value=f"{days_to_achieve_target:,}",
    #         delta="with Current Avg Transaction Duration"
    #     )
    
    
    # Create two columns
    col1, col2 = st.columns(2)

    # First column
    with col1:
        st.markdown(custom_metric("No. of Customers to Target", "7", "in 10 Days"), unsafe_allow_html=True)
        st.markdown(custom_metric("Daily Revenue per Customer", "177 ¥", ""), unsafe_allow_html=True)

    # Second column
    with col2:
        st.markdown(custom_metric("Total Daily Revenue", "1,239 ¥", "from Targeted Customers"), unsafe_allow_html=True)
        st.markdown(custom_metric("Est. Days to Achieve Target", "10", "with Current Avg Transaction Duration"), unsafe_allow_html=True)
    if days_to_achieve_target <= required_days_to_achieve_target:
        st.success(f"Yes, we can achieve the target in approximately {days_to_achieve_target:,} days with {no_of_customers_to_target:,} targeted customers!")
    else:
        st.warning(f"It may take longer than {math.ceil(required_days_to_achieve_target)} days to achieve the target with {no_of_customers_to_target:,} customers.")

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

    st.markdown("---")

def render():
    st.title("Cluster-Based Revenue Increase Strategy")
    st.markdown("This app analyzes transaction data to identify potential customer clusters for achieving revenue targets.")

    current_sales = st.sidebar.number_input("Enter Current Sales:", min_value=0, value=10000)
    percentage_increase = st.sidebar.number_input("Enter Percentage Increase:", min_value=0, max_value=100, value=20)
    required_days_to_achieve_target = math.ceil(st.sidebar.number_input("Enter Days to Achieve Target:", min_value=1, value=10))  # Ceil the days to achieve target

    # Calculate and display merchant inputs
    revenue_target = calculate_targets(current_sales, percentage_increase)

    st.markdown("---")
    st.subheader("Merchant Inputs")
    st.write(f"**Current Sales:** {math.floor(current_sales):,} ¥")
    st.write(f"**Targets Need to Achieve (Increased by {percentage_increase}%):** {revenue_target:,} ¥")
    st.write(f"**Revenue Target:** {revenue_target:,} ¥")
    st.write(f"**Days to Achieve:** {required_days_to_achieve_target:,}")

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