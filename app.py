import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bullwhip Effect Simulator",
    page_icon="📈",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📈 Bullwhip Effect Simulator")

st.markdown(
    """
    ### Interactive Supply Chain Variability Analysis

    This application demonstrates how demand variability can become
    increasingly amplified as we move upstream:

    **Customer → Retailer → Distributor → Manufacturer**

    Change the weekly demand/order values in the sidebar or directly
    in the editable table and observe how the **variance** and
    **Bullwhip Ratio** change.
    """
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Simulation Settings")

# ---------------------------------------------------------
# Number of weeks
# ---------------------------------------------------------

number_of_weeks = st.sidebar.number_input(
    "Number of Weeks",
    min_value=2,
    max_value=52,
    value=8,
    step=1
)


# ---------------------------------------------------------
# Data generation option
# ---------------------------------------------------------

st.sidebar.subheader("Data Input Method")

input_method = st.sidebar.radio(
    "Choose method:",
    [
        "Enter data manually",
        "Generate random data"
    ]
)


# =========================================================
# GENERATE DEFAULT DATA
# =========================================================

default_customer = [
    100, 110, 90, 105,
    120, 95, 115, 105
]

default_retailer = [
    100, 120, 80, 130,
    110, 85, 145, 95
]

default_distributor = [
    100, 140, 60, 150,
    100, 70, 170, 80
]

default_manufacturer = [
    100, 160, 40, 170,
    90, 50, 200, 60
]


# =========================================================
# MANUAL INPUT
# =========================================================

if input_method == "Enter data manually":

    # Adjust default arrays according to number of weeks

    customer_data = (
        default_customer[:number_of_weeks]
        + [100] * max(
            0,
            number_of_weeks - len(default_customer)
        )
    )

    retailer_data = (
        default_retailer[:number_of_weeks]
        + [100] * max(
            0,
            number_of_weeks - len(default_retailer)
        )
    )

    distributor_data = (
        default_distributor[:number_of_weeks]
        + [100] * max(
            0,
            number_of_weeks - len(default_distributor)
        )
    )

    manufacturer_data = (
        default_manufacturer[:number_of_weeks]
        + [100] * max(
            0,
            number_of_weeks - len(default_manufacturer)
        )
    )


# =========================================================
# RANDOM DATA
# =========================================================

else:

    random_seed = st.sidebar.number_input(
        "Random Seed",
        min_value=0,
        max_value=10000,
        value=42,
        step=1
    )

    base_demand = st.sidebar.number_input(
        "Average Demand",
        min_value=1,
        max_value=10000,
        value=100,
        step=10
    )

    demand_variability = st.sidebar.slider(
        "Customer Demand Variability",
        min_value=0,
        max_value=100,
        value=10,
        step=1
    )

    np.random.seed(random_seed)

    customer_data = np.maximum(
        0,
        np.random.normal(
            base_demand,
            demand_variability,
            number_of_weeks
        )
    ).round().astype(int)

    retailer_data = np.maximum(
        0,
        customer_data
        + np.random.normal(
            0,
            demand_variability * 1.5,
            number_of_weeks
        )
    ).round().astype(int)

    distributor_data = np.maximum(
        0,
        retailer_data
        + np.random.normal(
            0,
            demand_variability * 2,
            number_of_weeks
        )
    ).round().astype(int)

    manufacturer_data = np.maximum(
        0,
        distributor_data
        + np.random.normal(
            0,
            demand_variability * 2.5,
            number_of_weeks
        )
    ).round().astype(int)


# =========================================================
# CREATE DATAFRAME
# =========================================================

weeks = np.arange(
    1,
    number_of_weeks + 1
)

data = pd.DataFrame({

    "Week": weeks,

    "Customer Demand":
        customer_data,

    "Retailer Orders":
        retailer_data,

    "Distributor Orders":
        distributor_data,

    "Manufacturer Production":
        manufacturer_data
})


# =========================================================
# DATA EDITOR
# =========================================================

st.header("📝 Weekly Supply Chain Data")

st.markdown(
    """
    You can directly edit the values below.
    After changing the values, Streamlit automatically recalculates
    the Bullwhip Effect.
    """
)

edited_data = st.data_editor(
    data,
    use_container_width=True,
    num_rows="fixed",
    column_config={

        "Week": st.column_config.NumberColumn(
            "Week",
            disabled=True
        ),

        "Customer Demand":
            st.column_config.NumberColumn(
                "Customer Demand",
                min_value=0,
                step=1
            ),

        "Retailer Orders":
            st.column_config.NumberColumn(
                "Retailer Orders",
                min_value=0,
                step=1
            ),

        "Distributor Orders":
            st.column_config.NumberColumn(
                "Distributor Orders",
                min_value=0,
                step=1
            ),

        "Manufacturer Production":
            st.column_config.NumberColumn(
                "Manufacturer Production",
                min_value=0,
                step=1
            )
    }
)


# =========================================================
# EXTRACT DATA
# =========================================================

customer_demand = edited_data[
    "Customer Demand"
].to_numpy()

retailer_orders = edited_data[
    "Retailer Orders"
].to_numpy()

distributor_orders = edited_data[
    "Distributor Orders"
].to_numpy()

manufacturer_production = edited_data[
    "Manufacturer Production"
].to_numpy()


# =========================================================
# VARIANCE
# =========================================================

customer_variance = np.var(
    customer_demand
)

retailer_variance = np.var(
    retailer_orders
)

distributor_variance = np.var(
    distributor_orders
)

manufacturer_variance = np.var(
    manufacturer_production
)


# =========================================================
# STANDARD DEVIATION
# =========================================================

customer_std = np.std(
    customer_demand
)

retailer_std = np.std(
    retailer_orders
)

distributor_std = np.std(
    distributor_orders
)

manufacturer_std = np.std(
    manufacturer_production
)


# =========================================================
# BULLWHIP RATIO
# =========================================================

if customer_variance == 0:

    retailer_bw = np.nan
    distributor_bw = np.nan
    manufacturer_bw = np.nan

else:

    retailer_bw = (
        retailer_variance
        / customer_variance
    )

    distributor_bw = (
        distributor_variance
        / customer_variance
    )

    manufacturer_bw = (
        manufacturer_variance
        / customer_variance
    )


# =========================================================
# SUMMARY DATAFRAME
# =========================================================

stages = [
    "Customer",
    "Retailer",
    "Distributor",
    "Manufacturer"
]

variances = [
    customer_variance,
    retailer_variance,
    distributor_variance,
    manufacturer_variance
]

standard_deviations = [
    customer_std,
    retailer_std,
    distributor_std,
    manufacturer_std
]

bullwhip_ratios = [
    1,
    retailer_bw,
    distributor_bw,
    manufacturer_bw
]

summary = pd.DataFrame({

    "Stage": stages,

    "Variance": variances,

    "Standard Deviation":
        standard_deviations,

    "Bullwhip Ratio":
        bullwhip_ratios
})


# =========================================================
# KEY METRICS
# =========================================================

st.header("📊 Key Results")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Customer Variance",
        f"{customer_variance:.2f}"
    )


with col2:

    st.metric(
        "Retailer Bullwhip",
        f"{retailer_bw:.2f}"
        if not np.isnan(retailer_bw)
        else "N/A"
    )


with col3:

    st.metric(
        "Distributor Bullwhip",
        f"{distributor_bw:.2f}"
        if not np.isnan(distributor_bw)
        else "N/A"
    )


with col4:

    st.metric(
        "Manufacturer Bullwhip",
        f"{manufacturer_bw:.2f}"
        if not np.isnan(manufacturer_bw)
        else "N/A"
    )


# =========================================================
# INTERPRETATION
# =========================================================

st.subheader("🎯 Interpretation")

if manufacturer_bw > 1:

    st.success(
        f"""
        **Bullwhip Effect is present.**

        Manufacturer production has a Bullwhip Ratio of
        **{manufacturer_bw:.2f}**, meaning its variance is approximately
        **{manufacturer_bw:.2f} times** the variance of customer demand.
        """
    )

elif manufacturer_bw <= 1:

    st.info(
        """
        The manufacturer does not show amplification relative
        to customer demand in this dataset.
        """
    )


# =========================================================
# SUMMARY TABLE
# =========================================================

st.header("📋 Variance and Bullwhip Analysis")

st.dataframe(
    summary.style.format({
        "Variance": "{:.2f}",
        "Standard Deviation": "{:.2f}",
        "Bullwhip Ratio": "{:.2f}"
    }),
    use_container_width=True
)


# =========================================================
# VISUALIZATION 1
# DEMAND / ORDERS THROUGH SUPPLY CHAIN
# =========================================================

st.header(
    "1️⃣ Demand and Orders Across the Supply Chain"
)

fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.plot(
    weeks,
    customer_demand,
    marker="o",
    linewidth=2,
    label="Customer Demand"
)

ax.plot(
    weeks,
    retailer_orders,
    marker="o",
    linewidth=2,
    label="Retailer Orders"
)

ax.plot(
    weeks,
    distributor_orders,
    marker="o",
    linewidth=2,
    label="Distributor Orders"
)

ax.plot(
    weeks,
    manufacturer_production,
    marker="o",
    linewidth=2,
    label="Manufacturer Production"
)

ax.set_title(
    "Bullwhip Effect: Demand Variability Across the Supply Chain"
)

ax.set_xlabel("Week")
ax.set_ylabel("Units")

ax.set_xticks(weeks)

ax.grid(
    True,
    alpha=0.3
)

ax.legend()

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 2
# VARIANCE
# =========================================================

st.header(
    "2️⃣ Variance by Supply Chain Stage"
)

fig, ax = plt.subplots(
    figsize=(10, 5)
)

ax.bar(
    stages,
    variances
)

ax.set_title(
    "Demand / Order Variance"
)

ax.set_xlabel(
    "Supply Chain Stage"
)

ax.set_ylabel(
    "Variance"
)

ax.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 3
# BULLWHIP RATIO
# =========================================================

st.header(
    "3️⃣ Bullwhip Ratio"
)

fig, ax = plt.subplots(
    figsize=(10, 5)
)

ax.bar(
    stages,
    bullwhip_ratios
)

ax.axhline(
    y=1,
    linestyle="--",
    linewidth=2,
    label="No Amplification (Ratio = 1)"
)

ax.set_title(
    "Bullwhip Ratio Across the Supply Chain"
)

ax.set_xlabel(
    "Supply Chain Stage"
)

ax.set_ylabel(
    "Bullwhip Ratio"
)

ax.grid(
    axis="y",
    alpha=0.3
)

ax.legend()

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 4
# STANDARD DEVIATION
# =========================================================

st.header(
    "4️⃣ Standard Deviation by Stage"
)

fig, ax = plt.subplots(
    figsize=(10, 5)
)

ax.bar(
    stages,
    standard_deviations
)

ax.set_title(
    "Variability Measured by Standard Deviation"
)

ax.set_xlabel(
    "Supply Chain Stage"
)

ax.set_ylabel(
    "Standard Deviation"
)

ax.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 5
# NORMALIZED DEMAND
# =========================================================

st.header(
    "5️⃣ Normalized Demand / Orders"
)

normalized_data = edited_data.copy()

for column in [
    "Customer Demand",
    "Retailer Orders",
    "Distributor Orders",
    "Manufacturer Production"
]:

    mean_value = normalized_data[
        column
    ].mean()

    if mean_value != 0:

        normalized_data[
            column
        ] = (
            normalized_data[column]
            / mean_value
        ) * 100


fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.plot(
    weeks,
    normalized_data[
        "Customer Demand"
    ],
    marker="o",
    label="Customer"
)

ax.plot(
    weeks,
    normalized_data[
        "Retailer Orders"
    ],
    marker="o",
    label="Retailer"
)

ax.plot(
    weeks,
    normalized_data[
        "Distributor Orders"
    ],
    marker="o",
    label="Distributor"
)

ax.plot(
    weeks,
    normalized_data[
        "Manufacturer Production"
    ],
    marker="o",
    label="Manufacturer"
)

ax.axhline(
    100,
    linestyle="--",
    linewidth=1.5
)

ax.set_title(
    "Normalized Supply Chain Variability"
)

ax.set_xlabel("Week")

ax.set_ylabel(
    "Index (Average = 100)"
)

ax.set_xticks(weeks)

ax.grid(alpha=0.3)

ax.legend()

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 6
# RANGE / MAX-MIN
# =========================================================

st.header(
    "6️⃣ Demand and Order Range"
)

ranges = [
    np.max(customer_demand)
    - np.min(customer_demand),

    np.max(retailer_orders)
    - np.min(retailer_orders),

    np.max(distributor_orders)
    - np.min(distributor_orders),

    np.max(manufacturer_production)
    - np.min(manufacturer_production)
]

fig, ax = plt.subplots(
    figsize=(10, 5)
)

ax.bar(
    stages,
    ranges
)

ax.set_title(
    "Maximum-Minimum Range by Stage"
)

ax.set_xlabel(
    "Supply Chain Stage"
)

ax.set_ylabel(
    "Range (Units)"
)

ax.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 7
# WEEK-TO-WEEK CHANGE
# =========================================================

st.header(
    "7️⃣ Week-to-Week Changes"
)

customer_change = np.diff(
    customer_demand
)

retailer_change = np.diff(
    retailer_orders
)

distributor_change = np.diff(
    distributor_orders
)

manufacturer_change = np.diff(
    manufacturer_production
)

change_weeks = weeks[1:]

fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.plot(
    change_weeks,
    customer_change,
    marker="o",
    label="Customer"
)

ax.plot(
    change_weeks,
    retailer_change,
    marker="o",
    label="Retailer"
)

ax.plot(
    change_weeks,
    distributor_change,
    marker="o",
    label="Distributor"
)

ax.plot(
    change_weeks,
    manufacturer_change,
    marker="o",
    label="Manufacturer"
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=1.5
)

ax.set_title(
    "Week-to-Week Change in Demand / Orders"
)

ax.set_xlabel("Week")

ax.set_ylabel(
    "Change in Units"
)

ax.grid(alpha=0.3)

ax.legend()

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# VISUALIZATION 8
# COST / VARIABILITY STYLE COMPARISON
# =========================================================

st.header(
    "8️⃣ Variability Amplification"
)

amplification = [
    1,
    retailer_std / customer_std
    if customer_std != 0 else np.nan,

    distributor_std / customer_std
    if customer_std != 0 else np.nan,

    manufacturer_std / customer_std
    if customer_std != 0 else np.nan
]

fig, ax = plt.subplots(
    figsize=(10, 5)
)

ax.bar(
    stages,
    amplification
)

ax.axhline(
    1,
    linestyle="--",
    linewidth=2,
    label="Baseline = 1"
)

ax.set_title(
    "Standard Deviation Amplification"
)

ax.set_xlabel(
    "Supply Chain Stage"
)

ax.set_ylabel(
    "SD Ratio vs Customer"
)

ax.grid(
    axis="y",
    alpha=0.3
)

ax.legend()

plt.tight_layout()

st.pyplot(fig)


# =========================================================
# DATA DOWNLOAD
# =========================================================

st.header(
    "💾 Download Results"
)

csv_data = summary.to_csv(
    index=False
)

st.download_button(
    label="⬇️ Download Summary CSV",
    data=csv_data,
    file_name="bullwhip_analysis.csv",
    mime="text/csv"
)


# =========================================================
# FORMULA
# =========================================================

st.header(
    "📚 Bullwhip Ratio Formula"
)

st.latex(
    r"""
    \text{Bullwhip Ratio}
    =
    \frac{\operatorname{Variance(Orders)}}
    {\operatorname{Variance(Customer\ Demand)}}
    """
)

st.markdown(
    """
    **Interpretation:**

    - **Ratio = 1:** No amplification
    - **Ratio > 1:** Bullwhip Effect / amplification
    - **Ratio < 1:** Variability is lower than customer demand variability

    The further upstream the ratio increases, the stronger the
    Bullwhip Effect.
    """
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Bullwhip Effect Simulator | "
    "Operations Management / Supply Chain Management"
)