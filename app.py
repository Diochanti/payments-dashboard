import streamlit as st
import pandas as pd
import gspread
from io import BytesIO

st.set_page_config(page_title="Payments Dashboard", layout="wide")

st.title("💼 Payments Management Dashboard")

client = gspread.oauth(
    credentials_filename="credentials.json",
    authorized_user_filename="token.json"
)

spreadsheet = client.open_by_key("1XCugk_3eGhdouHRDfSgWz6b9BDABc8eB3knAOJCGr8E")

tabs = {
    "Monthly Overview": "Monthly Overview",
    "Payment Priority Queue": "Payment Priority Queue",
    "VAT Helper": "VAT Helper",
    "Unpaid Invoices": "Unpaid Invoices",
    "Paid Invoices": "Paid Invoices",
    "By Platform": "By Platform",
    "Top Affiliates": "Top Affiliates",
    "Overdue Invoices": "Overdue Invoices",
    "Pending Invoices": "Pending Invoices",
}

def load_tab(tab_name):
    worksheet = spreadsheet.worksheet(tab_name)
    return pd.DataFrame(worksheet.get_all_records())

def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()

def find_amount_column(df):
    possible = ["Amount", "Grand Total", "Total", "Net", "Commission", "Total Amount"]
    return next((col for col in possible if col in df.columns), None)

def find_column(df, possible_names):
    return next(
        (
            col for col in df.columns
            if str(col).strip().lower() in [name.strip().lower() for name in possible_names]
        ),
        None
    )

def apply_filters(df):
    filtered = df.copy()

    st.sidebar.markdown("### Filters")

    invoice_col = find_column(
        filtered,
        ["Invoice #", "Invoice", "Invoice Number", "Number", "Invoice No", "Invoice No."]
    )

    if invoice_col:
        invoice_search = st.sidebar.text_input("Search Invoice #")

        if invoice_search:
            filtered = filtered[
                filtered[invoice_col]
                .astype(str)
                .str.contains(invoice_search, case=False, na=False)
            ]

    possible_filters = {
        "Month": ["Month"],
        "Platform": ["Platform", "Brand"],
        "Affiliate": ["Affiliate", "Partner", "Display Name", "Partner/Display Name"],
        "Status": ["Status", "Payment Status"],
    }

    for label, columns in possible_filters.items():
        existing_col = find_column(filtered, columns)

        if existing_col:
            options = ["All"] + sorted(filtered[existing_col].dropna().astype(str).unique().tolist())
            selected = st.sidebar.selectbox(label, options)

            if selected != "All":
                filtered = filtered[filtered[existing_col].astype(str) == selected]

    return filtered

def build_priority_queue():
    frames = []

    sources = {
        "Overdue Invoices": "Overdue",
        "Pending Invoices": "Pending",
        "Unpaid Invoices": "Unpaid",
    }

    for tab_name, source_status in sources.items():
        try:
            temp = load_tab(tab_name)

            if not temp.empty:
                temp["Source"] = tab_name
                temp["Priority Type"] = source_status
                frames.append(temp)
        except Exception:
            pass

    if not frames:
        return pd.DataFrame()

    queue = pd.concat(frames, ignore_index=True)

    amount_col = find_amount_column(queue)

    if amount_col:
        queue[amount_col] = pd.to_numeric(queue[amount_col], errors="coerce").fillna(0)

    priority_order = {
        "Overdue": 1,
        "Pending": 2,
        "Unpaid": 3,
    }

    queue["Priority Rank"] = queue["Priority Type"].map(priority_order).fillna(9)

    if amount_col:
        queue = queue.sort_values(by=["Priority Rank", amount_col], ascending=[True, False])
    else:
        queue = queue.sort_values(by=["Priority Rank"], ascending=True)

    queue["Priority"] = queue["Priority Type"].map({
        "Overdue": "🔴 High",
        "Pending": "🟠 Medium",
        "Unpaid": "🟡 Review"
    })

    return queue

selected_tab = st.sidebar.selectbox("Select section", list(tabs.keys()))

if selected_tab == "Payment Priority Queue":
    df = build_priority_queue()
    df = apply_filters(df)
else:
    df = load_tab(tabs[selected_tab])
    df = apply_filters(df)

st.subheader(selected_tab)

if df.empty:
    st.warning("No data found for this section.")

else:
    if selected_tab == "Monthly Overview":
        st.markdown("### 📊 Executive Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Commissions", f"€{df['Total Commissions'].sum():,.0f}")
        col2.metric("Total Fixes", f"€{df['Total Fixes'].sum():,.0f}")
        col3.metric("Grand Total", f"€{df['Grand Total'].sum():,.0f}")

        st.markdown("### 💸 Outstanding Payables")

        omg_unpaid = df["OMG Unpaid"].sum() if "OMG Unpaid" in df.columns else 0
        ws_unpaid = df["WS Unpaid"].sum() if "WS Unpaid" in df.columns else 0
        total_unpaid = omg_unpaid + ws_unpaid

        col4, col5, col6 = st.columns(3)

        col4.metric("OMG Outstanding", f"€{omg_unpaid:,.0f}")
        col5.metric("WS Outstanding", f"€{ws_unpaid:,.0f}")
        col6.metric("Total Outstanding", f"€{total_unpaid:,.0f}")

        st.markdown("### 🚨 Payables Alert")

        if total_unpaid > 10000:
            st.error(f"⚠️ High outstanding payables: €{total_unpaid:,.0f}")
        elif total_unpaid > 5000:
            st.warning(f"⚠️ Medium outstanding payables: €{total_unpaid:,.0f}")
        else:
            st.success(f"✅ Outstanding payables under control: €{total_unpaid:,.0f}")

        st.markdown("### 🧾 Executive Summary Note")

        if total_unpaid > 0:
            main_exposure = (
                "OMG" if omg_unpaid > ws_unpaid
                else "WS" if ws_unpaid > omg_unpaid
                else "OMG and WS equally"
            )

            summary = (
                f"Outstanding payables currently stand at €{total_unpaid:,.0f}. "
                f"The highest exposure is associated with {main_exposure}. "
                f"These amounts should be reviewed for the upcoming payment cycle."
            )
        else:
            summary = "There are currently no outstanding payables requiring attention."

        st.info(summary)

        st.markdown("### 📈 Charts")

        if "Month" in df.columns and "Grand Total" in df.columns:
            st.bar_chart(df[["Month", "Grand Total"]].set_index("Month"))

        if "Month" in df.columns and "OMG Unpaid" in df.columns and "WS Unpaid" in df.columns:
            st.bar_chart(df[["Month", "OMG Unpaid", "WS Unpaid"]].set_index("Month"))

    elif selected_tab == "Payment Priority Queue":
        amount_col = find_amount_column(df)

        st.markdown("### 🚦 Payment Priority Queue")

        high_count = len(df[df["Priority Type"] == "Overdue"]) if "Priority Type" in df.columns else 0
        pending_count = len(df[df["Priority Type"] == "Pending"]) if "Priority Type" in df.columns else 0
        unpaid_count = len(df[df["Priority Type"] == "Unpaid"]) if "Priority Type" in df.columns else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Overdue Items", high_count)
        col2.metric("Pending Items", pending_count)
        col3.metric("Unpaid Items", unpaid_count)

        if amount_col:
            total_priority_amount = df[amount_col].sum()
            st.metric("Total Amount in Queue", f"€{total_priority_amount:,.0f}")

        st.info(
            "This queue prioritises overdue payments first, followed by pending and unpaid items. "
            "Within each group, higher amounts are shown first."
        )

    else:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if numeric_cols:
            st.markdown("### 📊 Totals")
            cols = st.columns(min(3, len(numeric_cols)))

            for i, col in enumerate(numeric_cols[:3]):
                cols[i].metric(col, f"€{df[col].sum():,.0f}")

    st.markdown("### 📋 Data")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📤 Download")

    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{selected_tab.replace(' ', '_')}.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download Excel",
        data=download_excel(df),
        file_name=f"{selected_tab.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )