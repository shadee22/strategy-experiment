import streamlit as st
import pandas as pd
import math
from helpers.compute_metrics import custom_metric, CLUSTER_NAMES

# Constants
DATA_FILE_BASE_PATH = './Data/cluster_calculation/hashed/'


def load_data(selected_cluster: int) -> pd.DataFrame:
    """Load cluster-specific data."""
    data_file_path = f"{DATA_FILE_BASE_PATH}rfm_cluster_{selected_cluster}.csv"
    return pd.read_csv(data_file_path)


def load_full_data(selected_cluster: int) -> pd.DataFrame:
    """Load the full dataset for the selected cluster."""
    path = f'{DATA_FILE_BASE_PATH}Full Dataset of Cluster {selected_cluster}.csv'
    return pd.read_csv(path)


def get_cluster_statistics(selected_cluster: int) -> dict:
    """Get statistical data (avg order, cashback, and count) for the selected cluster."""
    df = load_full_data(selected_cluster)
    
    # Group by cardholder_id to calculate statistics
    grouped = df.groupby('cardholder_id').agg(
        Total_Transaction_Value=('transaction_amount', 'sum'),
        Total_Cashback_Value=('cashback_amount', 'sum'),
        Transaction_Count=('transaction_amount', 'count')
    ).reset_index()

    grouped['Avg_Transaction_Value'] = grouped['Total_Transaction_Value'] / grouped['Transaction_Count']
    grouped['Avg_Cashback_Value'] = grouped['Total_Cashback_Value'] / grouped['Transaction_Count']

    # Calculate mean values
    avg_order = grouped['Avg_Transaction_Value'].mean()
    avg_cashback = grouped['Avg_Cashback_Value'].mean()

    return {
        'avg_order': math.floor(avg_order),
        'avg_cashback': math.floor(avg_cashback),
        'cardholder_count': grouped['cardholder_id'].nunique(), 
        'df': grouped
    }


def calculate_cashback_budget_and_customers(revenue_target: float, avg_order: float, avg_cashback: float, num_users: int):
    """Calculate cashback budget, number of customers to target, and potential errors."""
    potential_cashback_budget = avg_cashback * num_users
    max_possible_revenue = avg_order * num_users

    # Ensure the revenue target is feasible
    if revenue_target < potential_cashback_budget:
        return None, f"Error: The revenue target must be at least {math.floor(potential_cashback_budget)} ¥ to cover the minimum cashback budget."

    # Calculate the number of customers needed to reach the target
    num_customers_to_target = min(revenue_target / avg_order, num_users)
    cashback_budget_needed = num_customers_to_target * avg_cashback

    # Error handling for exceeding max possible revenue
    if num_customers_to_target == num_users and revenue_target > max_possible_revenue:
        return None, f"Error: The revenue target of {revenue_target} ¥ exceeds the maximum possible revenue ({math.floor(max_possible_revenue)} ¥) for this cluster."

    # Additional metrics
    days_to_achieve_target, no_of_customers_to_target, avg_transaction_duration, total_daily_revenue = calculate_days_to_achieve_target(
        revenue_target, avg_order, avg_cashback)
    
    return cashback_budget_needed, num_customers_to_target, days_to_achieve_target, no_of_customers_to_target


def calculate_days_to_achieve_target(revenue_target: float, avg_order: float, avg_cashback: float):
    """Calculate the number of days to achieve the revenue target based on transactions."""
    df = load_full_data(st.session_state.selected_cluster)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df = df.sort_values(by=['cardholder_id', 'transaction_date'])
    df['transaction_duration'] = df.groupby('cardholder_id')['transaction_date'].diff().dt.days
    avg_duration_per_user = df.groupby('cardholder_id')['transaction_duration'].mean()

    # Calculate average transaction duration and daily revenue metrics
    avg_transaction_duration = math.ceil(avg_duration_per_user.mean()) 
    no_of_customers_to_target = math.ceil(revenue_target / (avg_order - avg_cashback))
    daily_revenue_per_customer = math.floor((avg_order - avg_cashback) / avg_transaction_duration)  
    total_daily_revenue = math.floor(no_of_customers_to_target * daily_revenue_per_customer)  
    days_to_achieve_target = math.ceil(revenue_target / total_daily_revenue) 

    return days_to_achieve_target, no_of_customers_to_target, avg_transaction_duration, total_daily_revenue


def display_cluster_summary(cluster_stats: dict, df: pd.DataFrame):
    """Display a summary of the cluster's statistics."""
    st.subheader(f"Cluster Summary Statistics")
    st.write(f"Number of Users: {cluster_stats['cardholder_count']}")
    st.write(f"Average **(R)** Recency: {math.ceil(df['Recency'].mean())} days")
    st.write(f"Average **(F)** Frequency: {math.ceil(df['Frequency'].mean())} transactions")
    st.write(f"Average **(M)** Monetary Value: {math.floor(df['Monetary'].mean()):.2f} ¥")
    st.write(f"Average Order Value: {cluster_stats['avg_order']:.2f} ¥")
    st.write(f"Average Cashback per User: {cluster_stats['avg_cashback']:.2f} ¥")


def display_results(revenue_target: float, cashback_budget: float, num_customers: int, days_to_achieve_target: int, df: pd.DataFrame, prefix: str = ""):
    """Display the result of the calculations."""
    st.write(f"**To achieve a revenue target of** {math.floor(revenue_target):,.0f} ¥:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(custom_metric(label=f"{prefix}Cashback Budget Needed", value=f"{math.floor(cashback_budget):,.0f} ¥"), unsafe_allow_html=True)
        st.markdown(custom_metric(label=f"{prefix}Days to Achieve Target", value=f"{math.floor(days_to_achieve_target):,.0f} Days"), unsafe_allow_html=True)
    with col2:
        st.markdown(custom_metric(label=f"{prefix}Number of Customers to Target", value=f"{math.ceil(num_customers):,.0f} customers"), unsafe_allow_html=True)

    top_customers = df.sort_values('Monetary', ascending=False).head(math.ceil(num_customers)).reset_index(drop=True)
    
    st.subheader(f"{prefix}Top Customers Preview")
    st.dataframe(top_customers)
    
    st.download_button(
        label=f"📥 Download {prefix}Top Customer Data as CSV",
        data=top_customers.to_csv(index=True).encode('utf-8'),
        file_name=f'{prefix.lower()}top_customers_cluster_{st.session_state.selected_cluster}.csv',
        mime='text/csv',
        key=f"download_{prefix.lower()}"
    )


def render_sliders_and_results(avg_cashback: float, avg_order: float, initial_num_customers: int, initial_cashback_budget: float, days_to_achieve_target: int, df: pd.DataFrame):
    """Render sliders to adjust customer targeting and display the results."""
    if 'adjusted_num_customers' not in st.session_state:
        st.session_state.adjusted_num_customers = int(math.ceil(initial_num_customers))
    if 'adjusted_cashback_amount' not in st.session_state:
        st.session_state.adjusted_cashback_amount = initial_cashback_budget

    st.markdown("---")
    st.subheader("Adjust Parameters")

    # Slider for adjusting the number of customers
    adjusted_num_customers = st.slider(
        "Adjust the number of customers to target:",
        min_value=1,
        max_value=int(math.ceil(initial_num_customers)),
        value=st.session_state.adjusted_num_customers,
        key="slider_num_customers"
    )
    st.session_state.adjusted_num_customers = adjusted_num_customers

    # Adjust cashback and revenue based on the selected number of customers
    adjusted_cashback_budget = math.floor(adjusted_num_customers * avg_cashback)
    adjusted_target_revenue = math.floor(adjusted_num_customers * avg_order)
    
    display_results(adjusted_target_revenue, adjusted_cashback_budget, adjusted_num_customers, days_to_achieve_target, df, prefix="Adjusted ")

    st.markdown("---")

    # Slider for adjusting the cashback amount
    adjusted_cashback_amount = st.slider(
        "Adjust the cashback amount (total):",
        min_value=0.0,
        max_value=initial_cashback_budget,
        value=st.session_state.adjusted_cashback_amount,
        key="slider_cashback_amount"
    )
    st.session_state.adjusted_cashback_amount = adjusted_cashback_amount

    # Recalculate based on the adjusted cashback
    final_num_customers = math.ceil(adjusted_cashback_amount / avg_cashback)
    final_target_revenue = math.floor(final_num_customers * avg_order)

    display_results(final_target_revenue, adjusted_cashback_amount, final_num_customers

, days_to_achieve_target, df, prefix="Final ")


def render():
    """Main function to render the Streamlit app."""
    st.image("./Data/assets/logo.png", width=200)
    st.title("Cashback Budget Calculator")

    if 'selected_cluster' not in st.session_state:
        st.session_state.selected_cluster = None
    if 'revenue_target' not in st.session_state:
        st.session_state.revenue_target = 1000000
    if 'calculation_done' not in st.session_state:
        st.session_state.calculation_done = False

    st.markdown("""
    <style>
    button[kind="secondary"] {
        min-height: auto;
        padding: 10px;
        font-size: 16px;
        width: 100%;
        height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            if st.button(CLUSTER_NAMES[i]):
                st.session_state.selected_cluster = i
                st.session_state.revenue_target = 1000000  # Reset revenue target when cluster changes
                st.session_state.calculation_done = False
                if 'adjusted_num_customers' in st.session_state:
                    del st.session_state.adjusted_num_customers
                if 'adjusted_cashback_amount' in st.session_state:
                    del st.session_state.adjusted_cashback_amount

    if st.session_state.selected_cluster is None:
        return

    st.markdown(f"<h4>Selected Cluster: {CLUSTER_NAMES[st.session_state.selected_cluster]}</h4>", unsafe_allow_html=True)

    df = load_data(st.session_state.selected_cluster)
    cluster_stats = get_cluster_statistics(st.session_state.selected_cluster)

    with st.expander("Summary Statistics of the cluster"):
        display_cluster_summary(cluster_stats, df)

    st.markdown("---")
    st.session_state.revenue_target = st.number_input("Enter your Revenue Target (in ¥):", min_value=0, step=10000, value=st.session_state.revenue_target)

    result = calculate_cashback_budget_and_customers(st.session_state.revenue_target, cluster_stats['avg_order'], cluster_stats['avg_cashback'], cluster_stats['cardholder_count'])

    if isinstance(result[0], float):
        cashback_budget_needed, num_customers_to_target, days_to_achieve_target, no_of_customers_to_target = result
        display_results(st.session_state.revenue_target, cashback_budget_needed, num_customers_to_target, days_to_achieve_target, df, prefix="Initial ")
        st.session_state.calculation_done = True
    else:
        st.error(result[1])
        st.session_state.calculation_done = False

    if st.session_state.calculation_done:
        render_sliders_and_results(cluster_stats['avg_cashback'], cluster_stats['avg_order'], num_customers_to_target, cashback_budget_needed, days_to_achieve_target, df)

# Uncomment the line below to run the app in a Streamlit environment.
# if __name__ == "__main__":
#     render()