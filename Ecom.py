
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Fashion Sales Dashboard",
    page_icon="👗",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>
.stApp {
    background-color: #f4f6fa;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #dddddd;
}
</style>
""", unsafe_allow_html=True)

# TITLE
st.title("👗 Fashion Retail Sales Dashboard")
st.write("Sales | Revenue | Profit | Inventory Analytics")
st.divider()

# GENERATE SAMPLE SALES DATA
@st.cache_data
def generate_data():
    np.random.seed(42)

    products = {
        "Male": ["Jeans", "T-Shirts", "Shorts"],
        "Female": ["Jeans", "T-Shirts", "Shorts", "Skirts"]
    }

    prices = {
        "Jeans": 1499,
        "T-Shirts": 699,
        "Shorts": 899,
        "Skirts": 1199
    }

    records = []

    dates = pd.date_range(
        start="2022-01-01",
        end="2026-12-31",
        freq="D"
    )

    for date in dates:
        for gender, items in products.items():
            for product in items:

                units = np.random.randint(0, 9)
                price = prices[product]
                cost = price * 0.55

                revenue = units * price
                profit = revenue - (units * cost)

                records.append({
                    "Date": date,
                    "Year": date.year,
                    "Month": date.strftime("%b"),
                    "Gender": gender,
                    "Product": product,
                    "Units Sold": units,
                    "Revenue": revenue,
                    "Profit": profit
                })

    return pd.DataFrame(records)


df = generate_data()

# INVENTORY DATA
inventory = pd.DataFrame({
    "Gender": [
        "Male", "Male", "Male",
        "Female", "Female", "Female", "Female"
    ],
    "Product": [
        "Jeans", "T-Shirts", "Shorts",
        "Jeans", "T-Shirts", "Shorts", "Skirts"
    ],
    "Stock": [120, 45, 80, 95, 30, 65, 18],
    "Reorder Level": [40, 50, 30, 40, 50, 30, 25]
})

# SIDEBAR FILTERS
st.sidebar.title("⚙️ Dashboard Filters")

selected_year = st.sidebar.multiselect(
    "Select Year",
    sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)

selected_gender = st.sidebar.multiselect(
    "Select Gender",
    ["Male", "Female"],
    default=["Male", "Female"]
)

selected_product = st.sidebar.multiselect(
    "Select Product",
    sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

# FILTER DATA
filtered = df[
    (df["Year"].isin(selected_year)) &
    (df["Gender"].isin(selected_gender)) &
    (df["Product"].isin(selected_product))
]

# KPI CALCULATIONS
revenue = filtered["Revenue"].sum()
sales = filtered["Units Sold"].sum()
profit = filtered["Profit"].sum()

margin = (profit / revenue * 100) if revenue > 0 else 0

filtered_inventory = inventory[
    (inventory["Gender"].isin(selected_gender)) &
    (inventory["Product"].isin(selected_product))
]

stock = filtered_inventory["Stock"].sum()

low_stock = filtered_inventory[
    filtered_inventory["Stock"] <=
    filtered_inventory["Reorder Level"]
].shape[0]

# DISPLAY KPIs
st.subheader("📊 Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"₹{revenue:,.0f}")
c2.metric("Total Units Sold", f"{sales:,}")
c3.metric("Total Profit", f"₹{profit:,.0f}")
c4.metric("Profit Margin", f"{margin:.1f}%")

c5, c6 = st.columns(2)

c5.metric("Available Inventory", f"{stock:,} Units")
c6.metric("Low Stock Products", low_stock)

st.divider()

# DASHBOARD TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Sales Analytics",
    "👨 Male Collection",
    "👩 Female Collection",
    "📦 Inventory"
])

# TAB 1: SALES ANALYTICS
with tab1:

    st.subheader("Yearly Revenue and Profit")

    yearly = filtered.groupby("Year").agg({
        "Revenue": "sum",
        "Profit": "sum",
        "Units Sold": "sum"
    }).reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly["Year"],
        y=yearly["Revenue"],
        name="Revenue"
    ))

    fig.add_trace(go.Bar(
        x=yearly["Year"],
        y=yearly["Profit"],
        name="Profit"
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Year",
        yaxis_title="Amount (₹)"
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        product_sales = filtered.groupby(
            "Product"
        )["Units Sold"].sum().reset_index()

        fig2 = px.bar(
            product_sales,
            x="Product",
            y="Units Sold",
            color="Product",
            title="Product-wise Sales",
            text_auto=True
        )

        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        gender_revenue = filtered.groupby(
            "Gender"
        )["Revenue"].sum().reset_index()

        fig3 = px.pie(
            gender_revenue,
            names="Gender",
            values="Revenue",
            title="Revenue by Gender",
            hole=0.4
        )

        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Monthly Revenue")

    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    monthly = filtered.groupby("Month")[
        "Revenue"
    ].sum().reindex(month_order).reset_index()

    fig4 = px.line(
        monthly,
        x="Month",
        y="Revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    st.plotly_chart(fig4, use_container_width=True)

# TAB 2: MALE COLLECTION
with tab2:

    st.subheader("👨 Male Fashion Collection")

    male = filtered[filtered["Gender"] == "Male"]

    a, b, c = st.columns(3)

    a.metric("Male Revenue", f"₹{male['Revenue'].sum():,.0f}")
    b.metric("Male Sales", f"{male['Units Sold'].sum():,}")
    c.metric("Male Profit", f"₹{male['Profit'].sum():,.0f}")

    male_chart = male.groupby("Product")[
        "Revenue"
    ].sum().reset_index()

    fig5 = px.bar(
        male_chart,
        x="Product",
        y="Revenue",
        color="Product",
        title="Male Product Revenue",
        text_auto=True
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.dataframe(
        male.groupby("Product").agg({
            "Units Sold": "sum",
            "Revenue": "sum",
            "Profit": "sum"
        }).reset_index(),
        use_container_width=True,
        hide_index=True
    )

# TAB 3: FEMALE COLLECTION
with tab3:

    st.subheader("👩 Female Fashion Collection")

    female = filtered[filtered["Gender"] == "Female"]

    a, b, c = st.columns(3)

    a.metric("Female Revenue", f"₹{female['Revenue'].sum():,.0f}")
    b.metric("Female Sales", f"{female['Units Sold'].sum():,}")
    c.metric("Female Profit", f"₹{female['Profit'].sum():,.0f}")

    female_chart = female.groupby("Product")[
        "Revenue"
    ].sum().reset_index()

    fig6 = px.bar(
        female_chart,
        x="Product",
        y="Revenue",
        color="Product",
        title="Female Product Revenue",
        text_auto=True
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.dataframe(
        female.groupby("Product").agg({
            "Units Sold": "sum",
            "Revenue": "sum",
            "Profit": "sum"
        }).reset_index(),
        use_container_width=True,
        hide_index=True
    )

# TAB 4: INVENTORY
with tab4:

    st.subheader("📦 Inventory Management")

    inventory_view = filtered_inventory.copy()

    inventory_view["Status"] = np.where(
        inventory_view["Stock"] <=
        inventory_view["Reorder Level"],
        "Low Stock",
        "In Stock"
    )

    st.dataframe(
        inventory_view,
        use_container_width=True,
        hide_index=True
    )

    fig7 = px.bar(
        inventory_view,
        x="Product",
        y="Stock",
        color="Gender",
        barmode="group",
        title="Available Inventory",
        text_auto=True
    )

    st.plotly_chart(fig7, use_container_width=True)

    low_items = inventory_view[
        inventory_view["Status"] == "Low Stock"
    ]

    if len(low_items) > 0:
        st.warning("⚠️ Some products have low inventory!")
        st.dataframe(low_items, hide_index=True)
    else:
        st.success("All products have sufficient stock.")

# DOWNLOAD REPORT
st.divider()

st.subheader("📥 Export Sales Report")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV Report",
    data=csv,
    file_name="fashion_sales_report.csv",
    mime="text/csv"
)

st.caption("Developed using Python | Streamlit | Pandas | Plotly")
