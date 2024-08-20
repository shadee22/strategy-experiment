import streamlit as st
import pandas as pd

data_file_path = './Data/cluster_calculation/hashed/rfm_cluster_1.csv'

def render():
    
    # read the file and calculate these values. 
    mean_monetary = 2001.3
    avg_cashback = 297.28
    num_users = 3258
    # Function to calculate cashback budget and customers to target
    def calculate_cashback_budget_and_customers(revenue_target):
        # Calculate potential cashback budget if targeting all users
        potential_cashback_budget = avg_cashback * num_users
        max_possible_revenue = mean_monetary * num_users
        # Ensure the revenue target is greater than or equal to the minimum cashback budget
        if revenue_target < potential_cashback_budget:
            return None, f"Error: The revenue target must be at least {potential_cashback_budget:.2f} yen to cover the minimum cashback budget."
        # Calculate the number of customers to target
        num_customers_to_target = min(revenue_target / mean_monetary, num_users)
        # Calculate the cashback budget needed for these customers
        cashback_budget_needed = num_customers_to_target * avg_cashback
        # If the revenue target requires targeting more users than available
        if num_customers_to_target == num_users and revenue_target > max_possible_revenue:
            return None, f"Error: The revenue target of {revenue_target} yen exceeds the maximum possible revenue ({max_possible_revenue:.2f} yen) that can be generated from this cluster."
        print("num_customers_to_target", num_customers_to_target)
        return cashback_budget_needed, num_customers_to_target

    # Streamlit UI
    st.image("./Data/assets/logo.png", width=200)  # Add your company logo here
    st.markdown("<h1>Cashback Budget Calculator<br>for At-Risk Low Spenders</h1>", unsafe_allow_html=True)
    # Initialize session state
    if 'revenue_target' not in st.session_state:
        st.session_state.revenue_target = 1000000
        st.session_state.calculated = False
        st.session_state.cashback_budget = None
        st.session_state.num_customers = None
        st.session_state.error = None
        st.session_state.show_summary = False  # Track the visibility of the summary
    # Input: Revenue target
    revenue_target = st.number_input("Enter your Revenue Target (in yen):", min_value=0.0, step=1.0  , value=1000000.0)
    # Check if the revenue target has changed
    if revenue_target != st.session_state.revenue_target:
        st.session_state.revenue_target = revenue_target
        st.session_state.calculated = False
        st.session_state.cashback_budget = None
        st.session_state.num_customers = None
        st.session_state.error = None
    # Calculate and display results
    if st.button("Calculate Cashback Budget") or st.session_state.calculated:
        if not st.session_state.calculated:
            result, error = calculate_cashback_budget_and_customers(revenue_target)
            if result:
                st.session_state.cashback_budget, st.session_state.num_customers = result, error
                st.session_state.error = None
                st.session_state.calculated = True
            else:
                st.session_state.error = error
                st.session_state.calculated = True
        if st.session_state.error:
            st.error(st.session_state.error)
        else:
            cashback_budget, num_customers = st.session_state.cashback_budget, st.session_state.num_customers
            st.write(f"**To achieve a revenue target of**  {revenue_target:,.0f} yen:")
            st.success(f"**Cashback Budget Needed:** {cashback_budget:,.0f} yen")
            st.success(f"**Number of Customers to Target:** {num_customers:,.0f} customers")
            
            df = pd.read_csv(data_file_path)

            top_customers = df.head(round(num_customers))
            top_customers = top_customers.reset_index(drop=True)

            # Preview the top customers dataset
            st.subheader("Top Customers Preview")
            st.dataframe(top_customers)

            st.download_button(
                label="Download Top Customer Data as CSV",
                data=top_customers.to_csv(index=True).encode('utf-8'),
                file_name=f'top_customers.csv',
                mime='text/csv'
            )
            # Apply custom CSS to increase the thickness of the slider
            # st.markdown("""
            #     <style>
            #     /* Increase the thickness of the slider track */
            #     .stSlider > div > div > div > div {
            #         height: 50px;  /* Increase this value to thicken the slider line */
            #         background-color: #ff5f56;  /* Optional: Change the color of the slider track */
            #     }
            #     </style>
            #     """, unsafe_allow_html=True)

            
            # Add a checkbox to show or hide the sliders
            if st.checkbox("Show and Adjust Sliders"):
                # User adjustment of number of customers to target
                adjusted_num_customers = st.slider("Adjust the number of customers to target:",
                                                min_value=1, max_value=int(num_customers), value=int(num_customers))
                # Recalculate based on adjusted number of customers
                adjusted_cashback_budget = adjusted_num_customers * avg_cashback
                adjusted_target_revenue = adjusted_num_customers * mean_monetary
                st.success(f"**Adjusted Cashback Budget:** {adjusted_cashback_budget:,.0f} yen")
                st.success(f"**Adjusted Target Revenue:** {adjusted_target_revenue:,.0f} yen")
                
                df_sorted = df.sort_values(by='Monetary', ascending=False)
                # Select top customers based on final_num_customers
                top_customers = df_sorted.head(int(adjusted_num_customers))
                top_customers = top_customers.reset_index(drop=True)

                # Preview the adjusted top customers dataset
                st.subheader("Adjusted Top Customers Preview")
                st.dataframe(top_customers)
                
                st.download_button(
                    label="Download Top Customer Data as CSV",
                    data=top_customers.to_csv(index=True).encode('utf-8'),
                    file_name='top_customers.csv',
                    mime='text/csv',
                    key="download_selected"
                )
                
                st.markdown("---")
                
                # User adjustment of cashback amount
                adjusted_cashback_amount = st.slider("Adjust the cashback amount (total):",
                                                    min_value=0.0, max_value=cashback_budget, value=cashback_budget)
                # Recalculate based on adjusted cashback amount
                final_num_customers = adjusted_cashback_amount / avg_cashback
                final_target_revenue = final_num_customers * mean_monetary
                st.success(f"**Final Number of Customers to Target:**  {final_num_customers:.0f} customers")
                # st.success(f"**Final Number of Customers to Target:**  {final_num_customers:,.0f} customers")
                st.success(f"**Final Adjusted Target Revenue:** {final_target_revenue:,.0f} yen")
                
                # Load customer data (replace with the path to your dataset)
                df = pd.read_csv(data_file_path)
                # Sort by Monetary value in descending order
                df_sorted = df.sort_values('Monetary', ascending=False)
                # Select top customers based on final_num_customers
                top_customers = df_sorted.head(int(final_num_customers))
                top_customers = top_customers.reset_index( drop=True  )
                
                # Preview the final adjusted top customers dataset
                st.subheader("Final Adjusted Top Customers Preview")
                st.dataframe(top_customers)

                # Option to download the data as a CSV file
                st.download_button(
                    label="Download Top Customer Data as CSV",
                    data=top_customers.to_csv(index=True).encode('utf-8'),
                    file_name='top_customers.csv',
                    mime='text/csv',
                    key="button_cashback"
                )
    # Button to toggle Cluster 1 Summary Statistics visibility
    if st.button("View At-Risk Low Spenders Summary Statistics"):
        st.session_state.show_summary = not st.session_state.show_summary
    # Display the summary statistics if the toggle is on
    if st.session_state.show_summary:
        st.subheader("At-Risk Low Spenders Summary Statistics")
        st.write(f"Number of Users: {num_users}")
        st.write(f"Average Recency: {36.97:.2f} days")
        st.write(f"Average Frequency: {1.43:.2f} transactions")
        st.write(f"Average Monetary Value: {mean_monetary:.2f} yen")
        st.write(f"Average Cashback per User: {avg_cashback:.2f} yen")
