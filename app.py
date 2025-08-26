import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("colleges.csv")

st.set_page_config(page_title="EduLoanMap", layout="centered")
st.title("🎓 EduLoanMap — Education Loan Finder")

college_names = df['college_name'].unique()

typed_college = st.text_input("Start typing your college name", placeholder="e.g. VIT, Loyola, IIT Bombay")
selected_college = None

if typed_college:
    filtered_colleges = [c for c in college_names if typed_college.lower() in c.lower()]
    if filtered_colleges:
        selected_college = st.selectbox("Select your college", filtered_colleges)
    else:
        st.warning("No colleges found matching your input.")
else:
    st.info("Please start typing your college name above.")

if selected_college:
    st.success(f"Selected college: {selected_college}")

    col1, col2 = st.columns(2)
    with col1:
        collateral_filter = st.checkbox("Show only loans without collateral", value=False)
    with col2:
        banks = ['All Banks'] + sorted(df['bank_name'].unique())
        selected_bank = st.selectbox("Preferred Bank", banks)

    # Filter loans
    results = df[df['college_name'] == selected_college]
    if collateral_filter:
        results = results[results['collateral_required'].str.lower() == 'no']
    if selected_bank != 'All Banks':
        results = results[results['bank_name'] == selected_bank]

    if not results.empty:
        results['interest_rate_float'] = results['interest_rate'].apply(lambda x: float(x.strip('%')))
        results = results.sort_values('interest_rate_float')

        st.markdown("---")
        st.markdown("### Available Loan Offers")

        loans = results.to_dict('records')
        num_cols = 3
        for i in range(0, len(loans), num_cols):
            cols = st.columns(num_cols)
            for idx, loan in enumerate(loans[i:i+num_cols]):
                with cols[idx]:
                    st.markdown(f"""
                    **🏦 {loan['bank_name']}**  
                    Max Loan: ₹{int(loan['max_loan_amount']):,}  
                    Interest Rate: {loan['interest_rate']}  
                    Collateral: {loan['collateral_required']}  
                    Notes: {loan['notes']}
                    """)

        # EMI Calculator section
        st.markdown("---")
        st.subheader("EMI Calculator")

        selected_idx = st.selectbox(
            "Select a loan offer for EMI calculation",
            options=range(len(loans)),
            format_func=lambda x: f"{loans[x]['bank_name']} - {loans[x]['interest_rate']} interest"
        )

        selected_loan = loans[selected_idx]

        loan_amount = st.number_input("Loan Amount (₹)", min_value=10000, step=10000, value=int(selected_loan['max_loan_amount']))
        loan_tenure = st.number_input("Loan Tenure (years)", min_value=1, max_value=20, step=1, value=5)

        def calculate_emi(P, annual_rate, years):
            r = annual_rate / (12 * 100)
            n = years * 12
            emi = (P * r * (1 + r) ** n) / ((1 + r) ** n - 1)
            return emi

        interest_rate_float = float(selected_loan['interest_rate'].strip('%'))

        if loan_amount > 0:
            emi = calculate_emi(loan_amount, interest_rate_float, loan_tenure)
            st.markdown(f"**Estimated EMI:** ₹{emi:,.2f} per month for {loan_tenure} years")
    else:
        st.error("No loan options found matching your criteria.")
