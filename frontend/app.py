"""Streamlit user interface for the income tax calculator."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


st.set_page_config(
    page_title="Income Tax Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    [data-testid="stSidebar"] {
        background-color: #172554;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 20px;
    }

    .total-tax-row {
        background-color: #dbeafe;
        border: 2px solid #2563eb;
        border-radius: 8px;
        padding: 14px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


defaults = {
    "token": None,
    "user": None,
    "taxpayer": {},
    "salary": {},
    "deductions": {},
    "tax_result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def api_request(
    endpoint,
    method="GET",
    payload=None,
    authenticated=False,
):
    """Send an HTTP request to the tax calculator API.

    Args:
        endpoint: API path appended to the configured base URL.
        method: HTTP method to use.
        payload: Optional JSON-serializable request body.
        authenticated: Whether to include the saved bearer token.

    Returns:
        The decoded JSON response, or ``None`` if the request fails.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if authenticated:
        token = st.session_state.get("token")

        if not token:
            st.error("Authentication token is missing.")
            return None

        headers["Authorization"] = f"Bearer {token}"

    data = None

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(
        f"{API_URL}{endpoint}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=30) as response:
            response_data = response.read().decode("utf-8")

            if not response_data:
                return {}

            return json.loads(response_data)

    except HTTPError as error:
        details = error.read().decode("utf-8")

        try:
            error_data = json.loads(details)
            message = error_data.get("detail", details)
        except json.JSONDecodeError:
            message = details

        st.error(f"API Error ({error.code}): {message}")

    except URLError:
        st.error("Cannot connect to FastAPI. Check whether the backend is running.")

    except TimeoutError:
        st.error("The API request timed out.")

    return None


def show_authentication():
    """Render login and registration forms and process submissions."""

    st.title("💰 Income Tax Calculator")
    st.caption("Securely access your personal tax calculator.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Welcome Back")

        with st.form("login_form"):
            email = st.text_input(
                "Email Address",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

            if submitted:
                if not email.strip() or not password:
                    st.error("Please enter your email and password.")

                else:
                    result = api_request(
                        "/auth/login",
                        method="POST",
                        payload={
                            "email": email.strip(),
                            "password": password,
                        },
                    )

                    if result and result.get("access_token"):
                        st.session_state.token = result["access_token"]

                        user = api_request(
                            "/auth/me",
                            authenticated=True,
                        )

                        if user:
                            st.session_state.user = user

                            st.success("Login successful!")

                            st.rerun()

                        else:
                            st.session_state.token = None
                            st.session_state.user = None

    with register_tab:
        st.subheader("Create an Account")

        with st.form("register_form"):
            name = st.text_input(
                "Full Name",
                key="register_name",
            )

            email = st.text_input(
                "Email Address",
                key="register_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="register_confirm_password",
            )

            submitted = st.form_submit_button(
                "Register",
                use_container_width=True,
            )

            if submitted:
                if not name.strip():
                    st.error("Please enter your name.")

                elif len(name.strip()) < 2:
                    st.error("Name must contain at least 2 characters.")

                elif not email.strip():
                    st.error("Please enter your email.")

                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")

                elif password != confirm_password:
                    st.error("Passwords do not match.")

                else:
                    result = api_request(
                        "/auth/register",
                        method="POST",
                        payload={
                            "name": name.strip(),
                            "email": email.strip(),
                            "password": password,
                        },
                    )

                    if result and result.get("id"):
                        st.success(
                            "Registration successful! "
                            "Please login using your credentials."
                        )


def format_inr(amount, decimals=False):
    """Format an amount as Indian rupees.

    Args:
        amount: Numeric amount to format.
        decimals: Whether to display two decimal places.

    Returns:
        The amount formatted with rupee currency and thousands separators.
    """

    amount = float(amount)

    formatted = f"{amount:,.2f}" if decimals else f"{amount:,.0f}"

    return f"₹{formatted}"


def calculate_tax(payload):
    """Submit an authenticated tax calculation request.

    Args:
        payload: JSON-serializable salary and deduction details.

    Returns:
        The API calculation result, or ``None`` if the request fails.
    """

    return api_request(
        "/tax/calculate",
        method="POST",
        payload=payload,
        authenticated=True,
    )


def show_slab_breakdown(result):
    """Render the tax slab breakdown from a calculation result.

    Args:
        result: Tax calculation response containing slab details.
    """

    slab_breakdown = result.get(
        "tax_slab_breakdown",
        [],
    )

    if not slab_breakdown:
        st.info("No slab breakdown available.")
        return

    slab_data = []

    for slab in slab_breakdown:
        slab_data.append(
            {
                "Tax Rate": slab.get("slab_rate", "0%"),
                "Taxable Amount": format_inr(slab.get("taxable_amount", 0)),
                "Tax": format_inr(slab.get("tax", 0)),
            }
        )

    st.table(slab_data)


def show_tax_summary(result):
    """Render total tax and taxable income metrics.

    Args:
        result: Tax calculation response to summarize.
    """

    st.subheader("Tax Summary")

    st.metric(
        "Total Tax",
        format_inr(result.get("total_tax", 0)),
    )

    st.metric(
        "Taxable Income",
        format_inr(result.get("taxable_income", 0)),
    )


def show_comparison_table(old_tax, new_tax):
    """Render a side-by-side comparison of regime results.

    Args:
        old_tax: Calculation result for the old tax regime.
        new_tax: Calculation result for the new tax regime.
    """

    comparison_data = {
        "Details": [
            "Gross Salary",
            "HRA Exemption",
            "Standard Deduction",
            "80C Deduction",
            "Taxable Income",
            "Income Tax",
            "Cess",
        ],
        "Old Regime": [
            format_inr(old_tax.get("gross_salary", 0)),
            format_inr(old_tax.get("hra_exemption", 0)),
            format_inr(old_tax.get("standard_deduction", 0)),
            format_inr(old_tax.get("80c_deduction", 0)),
            format_inr(old_tax.get("taxable_income", 0)),
            format_inr(old_tax.get("tax_before_cess", 0)),
            format_inr(old_tax.get("cess_amount", 0)),
        ],
        "New Regime": [
            format_inr(new_tax.get("gross_salary", 0)),
            format_inr(new_tax.get("hra_exemption", 0)),
            format_inr(new_tax.get("standard_deduction", 0)),
            format_inr(new_tax.get("80c_deduction", 0)),
            format_inr(new_tax.get("taxable_income", 0)),
            format_inr(new_tax.get("tax_before_cess", 0)),
            format_inr(new_tax.get("cess_amount", 0)),
        ],
    }

    st.table(comparison_data)

    st.markdown(
        '<div class="total-tax-row"><h4>💰 TOTAL TAX COMPARISON</h4></div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    old_total = old_tax.get("total_tax", 0)
    new_total = new_tax.get("total_tax", 0)

    with col1:
        st.metric(
            "Old Regime - Total Tax",
            format_inr(old_total),
        )

    with col2:
        st.metric(
            "New Regime - Total Tax",
            format_inr(new_total),
            delta=(
                f"{format_inr(abs(old_total - new_total))} "
                + ("saved" if old_total > new_total else "more")
            ),
            delta_color=("normal" if old_total >= new_total else "inverse"),
        )


if not st.session_state.token:
    show_authentication()

    st.stop()


st.sidebar.title("💰 Tax Calculator")
st.sidebar.caption("Indian Income Tax Estimator")

st.sidebar.divider()

user = st.session_state.user or {}

st.sidebar.write(f"Logged in as **{user.get('name', 'User')}**")

st.sidebar.caption(user.get("email", ""))

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Taxpayer Details",
        "💵 Salary Details",
        "📋 Deductions",
        "📊 Tax Calculation",
        "📜 Tax History",
    ],
)

st.sidebar.divider()

if st.sidebar.button(
    "Logout",
    use_container_width=True,
):
    st.session_state.token = None
    st.session_state.user = None

    st.session_state.taxpayer = {}
    st.session_state.salary = {}
    st.session_state.deductions = {}
    st.session_state.tax_result = None

    st.rerun()

st.sidebar.caption("Income Tax Calculator")


if page == "🏠 Dashboard":
    st.title("Income Tax Dashboard")

    st.write("Manage your details and compare income tax regimes.")

    taxpayer = st.session_state.taxpayer
    salary = st.session_state.salary
    deductions = st.session_state.deductions

    gross_salary = sum(salary.values()) if salary else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Taxpayer",
            taxpayer.get("name", "Not added"),
        )

    with col2:
        st.metric(
            "Gross Annual Salary",
            format_inr(gross_salary),
        )

    with col3:
        st.metric(
            "80C Investments",
            format_inr(deductions.get("deduction_80c", 0)),
        )

    st.subheader("Your Progress")

    st.write("✅ Taxpayer details completed" if taxpayer else "⬜ Add taxpayer details")

    st.write("✅ Salary details completed" if salary else "⬜ Add salary details")

    st.write(
        "✅ Deduction details completed" if deductions else "⬜ Add deduction details"
    )

    if st.session_state.tax_result:
        st.divider()

        st.subheader("Latest Tax Calculation")

        result = st.session_state.tax_result

        comparison = result.get("comparison", {})

        recommended_regime = comparison.get("recommended_regime")

        if recommended_regime == "old":
            st.metric(
                "Recommended Regime",
                "Old Tax Regime",
            )

        elif recommended_regime == "new":
            st.metric(
                "Recommended Regime",
                "New Tax Regime",
            )

        elif recommended_regime == "both":
            st.metric(
                "Recommended Regime",
                "Both Regimes",
            )


elif page == "👤 Taxpayer Details":
    st.title("Taxpayer Details")

    st.write("Enter your personal details.")

    saved = st.session_state.taxpayer

    with st.form("taxpayer_form"):
        name = st.text_input(
            "Full Name",
            value=saved.get("name", ""),
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=saved.get("age", 25),
            step=1,
        )

        regime_options = [
            "Compare Both",
            "Old Regime",
            "New Regime",
        ]

        regime_mapping = {
            "old": "Old Regime",
            "new": "New Regime",
            None: "Compare Both",
        }

        default_regime = regime_mapping.get(
            saved.get("tax_regime"),
            "Compare Both",
        )

        selected_regime = st.selectbox(
            "Tax Regime",
            regime_options,
            index=regime_options.index(default_regime),
        )

        submitted = st.form_submit_button("Save Taxpayer Details")

        if submitted:
            if not name.strip():
                st.error("Please enter the taxpayer name.")

            elif len(name.strip()) < 2:
                st.error("Name must contain at least 2 characters.")

            elif age <= 0:
                st.error("Age must be greater than zero.")

            elif age >= 120:
                st.error("Please enter a valid age below 120.")

            else:
                regime_values = {
                    "Compare Both": None,
                    "Old Regime": "old",
                    "New Regime": "new",
                }

                st.session_state.taxpayer = {
                    "name": name.strip(),
                    "age": int(age),
                    "tax_regime": regime_values[selected_regime],
                }

                st.session_state.tax_result = None

                st.success("Taxpayer details saved successfully.")

    saved = st.session_state.taxpayer

    if saved:
        st.divider()

        st.subheader("Saved Details")

        st.write(f"**Name:** {saved.get('name', '')}")

        st.write(f"**Age:** {saved.get('age', '')}")

        st.write(f"**Regime:** {saved.get('tax_regime') or 'Compare Both'}")


elif page == "💵 Salary Details":
    st.title("Salary Details")

    st.write("Enter your annual salary components.")

    saved = st.session_state.salary

    with st.form("salary_form"):
        col1, col2 = st.columns(2)

        with col1:
            basic_salary = st.number_input(
                "Basic Salary (₹)",
                min_value=0.0,
                value=float(saved.get("basic_salary", 0)),
                step=10000.0,
            )

            hra = st.number_input(
                "HRA (₹)",
                min_value=0.0,
                value=float(saved.get("hra", 0)),
                step=5000.0,
            )

        with col2:
            special_allowance = st.number_input(
                "Special Allowance (₹)",
                min_value=0.0,
                value=float(saved.get("special_allowance", 0)),
                step=5000.0,
            )

            bonus = st.number_input(
                "Bonus (₹)",
                min_value=0.0,
                value=float(saved.get("bonus", 0)),
                step=5000.0,
            )

        submitted = st.form_submit_button("Save Salary Details")

        if submitted:
            if basic_salary == 0 and hra == 0 and special_allowance == 0 and bonus == 0:
                st.error("Please enter at least one salary component.")

            else:
                st.session_state.salary = {
                    "basic_salary": basic_salary,
                    "hra": hra,
                    "special_allowance": special_allowance,
                    "bonus": bonus,
                }

                st.session_state.tax_result = None

                st.success("Salary details saved successfully.")

    saved = st.session_state.salary

    if saved:
        st.divider()

        gross_salary = sum(saved.values())

        st.metric(
            "Gross Annual Salary",
            format_inr(gross_salary),
        )


elif page == "📋 Deductions":
    st.title("Deductions")

    st.write("Enter your eligible deductions.")

    saved = st.session_state.deductions

    with st.form("deductions_form"):
        col1, col2 = st.columns(2)

        with col1:
            annual_rent = st.number_input(
                "Annual Rent Paid (₹)",
                min_value=0.0,
                value=float(saved.get("annual_rent", 0)),
                step=5000.0,
            )

        with col2:
            deduction_80c = st.number_input(
                "80C Investments (₹)",
                min_value=0.0,
                value=float(saved.get("deduction_80c", 0)),
                step=5000.0,
            )

        submitted = st.form_submit_button("Save Deduction Details")

        if submitted:
            if deduction_80c > 150000:
                st.error("80C investments cannot exceed ₹1,50,000.")

            else:
                st.session_state.deductions = {
                    "annual_rent": annual_rent,
                    "deduction_80c": deduction_80c,
                }

                st.session_state.tax_result = None

                st.success("Deduction details saved successfully.")

    saved = st.session_state.deductions

    if saved:
        st.divider()

        st.metric(
            "80C Investments",
            format_inr(saved.get("deduction_80c", 0)),
        )


elif page == "📊 Tax Calculation":
    st.title("📊 Tax Calculation")

    taxpayer = st.session_state.taxpayer
    salary = st.session_state.salary
    deductions = st.session_state.deductions

    selected_regime = taxpayer.get("tax_regime")

    if not taxpayer or not salary or not deductions:
        st.warning(
            "Please complete Taxpayer Details, Salary Details, "
            "and Deductions before calculating tax."
        )

    else:
        if selected_regime is None:
            st.write("Compare your income tax under both regimes.")

        elif selected_regime == "old":
            st.write("Calculate your income tax under the Old Regime.")

        else:
            st.write("Calculate your income tax under the New Regime.")

        if st.button(
            "Calculate Income Tax",
            use_container_width=True,
        ):
            payload = {
                "basic_salary": salary["basic_salary"],
                "hra_received": salary["hra"],
                "special_allowance": salary["special_allowance"],
                "bonus": salary["bonus"],
                "rent_paid": deductions["annual_rent"],
                "eligible_investments": deductions["deduction_80c"],
                "tax_regime": selected_regime,
            }

            with st.spinner("Calculating income tax..."):
                result = calculate_tax(payload)

            if result:
                st.session_state.tax_result = result

        result = st.session_state.tax_result

        if result:
            st.success("Tax calculation completed successfully!")

            if "comparison" in result:
                comparison = result["comparison"]

                old_tax = comparison.get(
                    "old_regime",
                    {},
                )

                new_tax = comparison.get(
                    "new_regime",
                    {},
                )

                st.subheader("Tax Regime Comparison")

                show_comparison_table(
                    old_tax,
                    new_tax,
                )

                recommended_regime = comparison.get("recommended_regime")

                st.subheader("Recommended Tax Regime")

                if recommended_regime == "old":
                    st.success("Recommended Regime: Old Tax Regime")

                elif recommended_regime == "new":
                    st.success("Recommended Regime: New Tax Regime")

                elif recommended_regime == "both":
                    st.info("Both tax regimes result in the same tax.")

                tax_saving = comparison.get(
                    "tax_saving",
                    0,
                )

                st.metric(
                    "Potential Tax Savings",
                    format_inr(tax_saving),
                )

                st.subheader("Tax Slab Breakdown")

                tab_old, tab_new = st.tabs(["Old Regime", "New Regime"])

                with tab_old:
                    st.write("Old Regime Slab Details")

                    show_slab_breakdown(old_tax)

                with tab_new:
                    st.write("New Regime Slab Details")

                    show_slab_breakdown(new_tax)

            else:
                tax_regime = result.get("tax_regime")

                if tax_regime == "old":
                    st.subheader("Old Tax Regime Result")

                elif tax_regime == "new":
                    st.subheader("New Tax Regime Result")

                else:
                    st.error("Unknown tax regime in API response.")

                    st.stop()

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Gross Salary",
                        format_inr(result.get("gross_salary", 0)),
                    )

                    st.metric(
                        "Taxable Income",
                        format_inr(result.get("taxable_income", 0)),
                    )

                with col2:
                    st.metric(
                        "Income Tax",
                        format_inr(result.get("tax_before_cess", 0)),
                    )

                    st.metric(
                        "Cess",
                        format_inr(result.get("cess_amount", 0)),
                    )

                st.subheader("Total Tax Payable")

                st.metric(
                    "Total Tax",
                    format_inr(result.get("total_tax", 0)),
                )

                st.subheader("Tax Slab Breakdown")

                show_slab_breakdown(result)


elif page == "📜 Tax History":
    st.title("📜 Tax Calculation History")

    st.write("View your previously saved tax calculations.")

    if st.button(
        "Refresh History",
        use_container_width=False,
    ):
        st.rerun()

    history = api_request(
        "/tax/history",
        authenticated=True,
    )

    if history is not None:
        if not history:
            st.info("You haven't saved any tax calculations yet.")

        else:
            st.success(f"{len(history)} calculation(s) found.")

            for calculation in history:
                calculation_id = calculation.get("id")

                created_at = calculation.get(
                    "created_at",
                    "",
                )

                result = calculation.get(
                    "result",
                    {},
                )

                request_data = calculation.get(
                    "request",
                    {},
                )

                with st.expander(f"Calculation #{calculation_id} — {created_at}"):
                    st.write(
                        "**Tax Regime:** "
                        f"{request_data.get('tax_regime') or 'Compare Both'}"
                    )

                    st.write(
                        "**Basic Salary:** "
                        f"{format_inr(request_data.get('basic_salary', 0))}"
                    )

                    if "comparison" in result:
                        comparison = result["comparison"]

                        old_tax = comparison.get(
                            "old_regime",
                            {},
                        )

                        new_tax = comparison.get(
                            "new_regime",
                            {},
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Old Regime Total Tax",
                                format_inr(old_tax.get("total_tax", 0)),
                            )

                        with col2:
                            st.metric(
                                "New Regime Total Tax",
                                format_inr(new_tax.get("total_tax", 0)),
                            )

                        st.write(
                            "**Recommended Regime:** "
                            f"{comparison.get('recommended_regime', 'N/A')}"
                        )

                    else:
                        st.metric(
                            "Total Tax",
                            format_inr(result.get("total_tax", 0)),
                        )

                    with st.popover("View Full Calculation"):
                        st.json(result)
