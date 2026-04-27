import json
from io import BytesIO
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Payments Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# CUSTOM DARK CORPORATE CSS
# =====================================================

st.markdown("""
<style>
    /* Main dark background */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(30, 64, 175, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(15, 118, 110, 0.12), transparent 26%),
            linear-gradient(135deg, #020617 0%, #0f172a 48%, #111827 100%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* General text visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    p, span, label {
        color: inherit;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    [data-testid="stSidebar"] label {
        color: #e5e7eb !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] input {
        color: #020617 !important;
        background-color: #f8fafc !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #020617 !important;
    }

    [data-testid="stSidebar"] .stCaptionContainer {
        color: #cbd5e1 !important;
    }

    /* Main dashboard header */
    .dashboard-header {
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 55%, rgba(51, 65, 85, 0.98) 100%);
        padding: 30px 34px;
        border-radius: 22px;
        color: white;
        margin-bottom: 26px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.22);
    }

    .dashboard-title {
        font-size: 32px;
        font-weight: 850;
        margin-bottom: 6px;
        letter-spacing: -0.03em;
        color: #ffffff !important;
    }

    .dashboard-subtitle {
        font-size: 15px;
        color: #cbd5e1 !important;
        line-height: 1.6;
    }

    .status-pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background-color: rgba(34, 197, 94, 0.14);
        color: #bbf7d0 !important;
        font-size: 12px;
        font-weight: 750;
        margin-top: 14px;
        border: 1px solid rgba(187, 247, 208, 0.26);
    }

    /* Section titles */
    .section-title {
        font-size: 25px;
        font-weight: 850;
        color: #f8fafc !important;
        margin-top: 8px;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }

    .section-subtitle {
        font-size: 14px;
        color: #cbd5e1 !important;
        margin-bottom: 18px;
        line-height: 1.6;
    }

    .corporate-card {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.26);
        margin-bottom: 18px;
    }

    /* Metric cards - dark premium */
    div[data-testid="stMetric"] {
        background:
            linear-gradient(180deg, rgba(30, 41, 59, 0.96) 0%, rgba(15, 23, 42, 0.96) 100%) !important;
        border: 1px solid rgba(148, 163, 184, 0.22);
        padding: 18px 20px;
        border-radius: 18px;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.26);
    }

    div[data-testid="stMetric"] * {
        color: #f8fafc !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 750;
        color: #cbd5e1 !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 850;
        color: #ffffff !important;
    }

    div[data-testid="stMetricDelta"] {
        color: #cbd5e1 !important;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] p {
        color: #cbd5e1 !important;
    }

    .small-note {
        font-size: 13px;
        color: #cbd5e1 !important;
        line-height: 1.6;
    }

    .divider {
        height: 1px;
        background: rgba(148, 163, 184, 0.20);
        margin: 20px 0;
    }

    /* Executive Action box */
    .action-box {
        background:
            linear-gradient(135deg, rgba(124, 45, 18, 0.48) 0%, rgba(15, 23, 42, 0.94) 55%, rgba(30, 41, 59, 0.92) 100%);
        border: 1px solid rgba(251, 146, 60, 0.34);
        border-left: 6px solid #fb923c;
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 24px;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28);
    }

    .action-title {
        font-size: 19px;
        font-weight: 850;
        color: #fed7aa !important;
        margin-bottom: 8px;
    }

    .action-text {
        font-size: 14px;
        color: #ffedd5 !important;
        line-height: 1.7;
    }

    .action-text strong {
        color: #ffffff !important;
    }

    /* Smart Recommendation box */
    .recommendation-box {
        background:
            linear-gradient(135deg, rgba(30, 64, 175, 0.44) 0%, rgba(15, 23, 42, 0.94) 55%, rgba(30, 41, 59, 0.92) 100%);
        border: 1px solid rgba(96, 165, 250, 0.34);
        border-left: 6px solid #60a5fa;
        border-radius: 20px;
        padding: 22px 24px;
        margin-top: 18px;
        margin-bottom: 22px;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28);
    }

    .recommendation-title {
        font-size: 19px;
        font-weight: 850;
        color: #bfdbfe !important;
        margin-bottom: 8px;
    }

    .recommendation-text {
        font-size: 14px;
        color: #dbeafe !important;
        line-height: 1.7;
    }

    .recommendation-text strong {
        color: #ffffff !important;
    }

    /* Streamlit alerts - keep readable on dark app */
    div[data-testid="stAlert"] {
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }

    div[data-testid="stAlert"] * {
        color: #0f172a !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 700;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
    }

    /* Dataframe area */
    div[data-testid="stDataFrame"] {
        background-color: rgba(15, 23, 42, 0.92);
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        overflow: hidden;
    }

    /* Buttons */
    button[kind="secondary"] {
        border-radius: 13px !important;
        border: 1px solid rgba(148, 163, 184, 0.38) !important;
        font-weight: 750 !important;
        background-color: rgba(30, 41, 59, 0.96) !important;
        color: #f8fafc !important;
    }

    button[kind="secondary"]:hover {
        border-color: rgba(96, 165, 250, 0.70) !important;
        background-color: rgba(51, 65, 85, 0.98) !important;
    }

    .stDownloadButton button {
        width: 100%;
    }

    /* Captions */
    .stCaptionContainer {
        color: #cbd5e1 !important;
    }

    /* Markdown horizontal line */
    hr {
        border-color: rgba(148, 163, 184, 0.22) !important;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# GOOGLE SHEETS CONNECTION
# =====================================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds_data = st.secrets["gcp"]["credentials"]

if isinstance(creds_data, str):
    creds_data = json.loads(creds_data)

creds = Credentials.from_service_account_info(creds_data, scopes=scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key("1XCugk_3eGhdouHRDfSgWz6b9BDABc8eB3knAOJCGr8E")


# =====================================================
# AVAILABLE SECTIONS
# =====================================================

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


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def load_tab(tab_name):
    worksheet = spreadsheet.worksheet(tab_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)


def download_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")

    return output.getvalue()


def find_amount_column(df):
    possible = [
        "Amount",
        "Grand Total",
        "Total",
        "Net",
        "Commission",
        "Total Amount",
        "Total Commissions",
    ]

    return next((col for col in possible if col in df.columns), None)


def find_column(df, possible_names):
    return next(
        (
            col for col in df.columns
            if str(col).strip().lower()
            in [name.strip().lower() for name in possible_names]
        ),
        None
    )


def clean_numeric(series):
    return (
        series.astype(str)
        .str.replace("€", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .replace("", "0")
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )


def safe_sum(df, column):
    if column in df.columns:
        return clean_numeric(df[column]).sum()

    return 0


def format_currency(value):
    return f"€{value:,.0f}"


def apply_filters(df):
    filtered = df.copy()

    st.sidebar.markdown("## Control Panel")
    st.sidebar.caption("Filter and explore payment data")

    invoice_col = find_column(
        filtered,
        ["Invoice #", "Invoice", "Invoice Number", "Number", "Invoice No", "Invoice No."]
    )

    if invoice_col:
        invoice_search = st.sidebar.text_input("Search invoice")

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
            options = ["All"] + sorted(
                filtered[existing_col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected = st.sidebar.selectbox(label, options)

            if selected != "All":
                filtered = filtered[filtered[existing_col].astype(str) == selected]

    st.sidebar.markdown("---")
    st.sidebar.caption("Data source: Google Sheets")
    st.sidebar.caption("Status: Live sync enabled")

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
        queue[amount_col] = clean_numeric(queue[amount_col])

    priority_order = {
        "Overdue": 1,
        "Pending": 2,
        "Unpaid": 3,
    }

    queue["Priority Rank"] = queue["Priority Type"].map(priority_order).fillna(9)

    if amount_col:
        queue = queue.sort_values(
            by=["Priority Rank", amount_col],
            ascending=[True, False]
        )
    else:
        queue = queue.sort_values(by=["Priority Rank"], ascending=True)

    queue["Priority"] = queue["Priority Type"].map({
        "Overdue": "🔴 High",
        "Pending": "🟠 Medium",
        "Unpaid": "🟡 Review",
    })

    return queue


def show_header():
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">Payments Management Dashboard</div>
        <div class="dashboard-subtitle">
            Corporate finance operations dashboard for invoice monitoring,
            payment prioritisation, VAT review and monthly reporting.
            <br>
            Last updated: {datetime.now().strftime("%d %b %Y, %H:%M")}
        </div>
        <div class="status-pill">● Live Google Sheets Sync</div>
    </div>
    """, unsafe_allow_html=True)


def show_section_intro(title, subtitle):
    st.markdown(f"""
    <div class="section-title">{title}</div>
    <div class="section-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def show_action_required(priority_df):
    if priority_df.empty:
        st.markdown("""
        <div class="action-box">
            <div class="action-title">Executive Action Required</div>
            <div class="action-text">
                No urgent payment items are currently detected. The payment queue appears to be clear based on the available invoice data.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    amount_col = find_amount_column(priority_df)

    overdue_count = len(priority_df[priority_df["Priority Type"] == "Overdue"]) if "Priority Type" in priority_df.columns else 0
    pending_count = len(priority_df[priority_df["Priority Type"] == "Pending"]) if "Priority Type" in priority_df.columns else 0
    unpaid_count = len(priority_df[priority_df["Priority Type"] == "Unpaid"]) if "Priority Type" in priority_df.columns else 0

    total_items = overdue_count + pending_count + unpaid_count

    total_exposure = 0
    if amount_col:
        total_exposure = clean_numeric(priority_df[amount_col]).sum()

    if overdue_count > 0:
        urgency = "High attention is required due to overdue invoices."
    elif pending_count > 0:
        urgency = "Medium attention is required due to pending invoices."
    elif unpaid_count > 0:
        urgency = "Review is recommended for unpaid invoices."
    else:
        urgency = "No immediate payment risk is detected."

    st.markdown(f"""
    <div class="action-box">
        <div class="action-title">Executive Action Required</div>
        <div class="action-text">
            There are <strong>{total_items}</strong> invoice items requiring review.
            Current payment exposure stands at <strong>{format_currency(total_exposure)}</strong>.
            <br>
            Breakdown: <strong>{overdue_count}</strong> overdue,
            <strong>{pending_count}</strong> pending,
            <strong>{unpaid_count}</strong> unpaid.
            <br>
            {urgency}
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_smart_payment_recommendation(priority_df):
    if priority_df.empty:
        return

    amount_col = find_amount_column(priority_df)

    top_item = priority_df.iloc[0]

    invoice_col = find_column(
        priority_df,
        ["Invoice #", "Invoice", "Invoice Number", "Number", "Invoice No", "Invoice No."]
    )

    affiliate_col = find_column(
        priority_df,
        ["Affiliate", "Partner", "Display Name", "Partner/Display Name"]
    )

    platform_col = find_column(
        priority_df,
        ["Platform", "Brand"]
    )

    priority_type = top_item["Priority Type"] if "Priority Type" in priority_df.columns else "Review"

    invoice_value = top_item[invoice_col] if invoice_col else "N/A"
    affiliate_value = top_item[affiliate_col] if affiliate_col else "N/A"
    platform_value = top_item[platform_col] if platform_col else "N/A"

    amount_value = "N/A"
    if amount_col:
        amount_value = format_currency(clean_numeric(pd.Series([top_item[amount_col]])).sum())

    st.markdown(f"""
    <div class="recommendation-box">
        <div class="recommendation-title">Smart Payment Recommendation</div>
        <div class="recommendation-text">
            Recommended next review:
            <strong>{affiliate_value}</strong>
            on <strong>{platform_value}</strong>,
            invoice <strong>{invoice_value}</strong>,
            amount <strong>{amount_value}</strong>.
            <br>
            Priority level: <strong>{priority_type}</strong>.
            This item appears first because the queue prioritises overdue invoices first and then sorts by the highest available amount.
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_downloads(df, selected_tab):
    st.markdown("### Export Centre")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{selected_tab.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "Download Excel",
            data=download_excel(df),
            file_name=f"{selected_tab.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.markdown("# Payments Dashboard")
st.sidebar.markdown("Corporate finance workspace")
st.sidebar.markdown("---")

selected_tab = st.sidebar.selectbox(
    "Select section",
    list(tabs.keys())
)


# =====================================================
# LOAD DATA
# =====================================================

try:
    if selected_tab == "Payment Priority Queue":
        df = build_priority_queue()
        df = apply_filters(df)
    else:
        df = load_tab(tabs[selected_tab])
        df = apply_filters(df)

except Exception as error:
    st.error("The dashboard could not load the selected section.")
    st.exception(error)
    st.stop()


# =====================================================
# MAIN HEADER
# =====================================================

show_header()


# =====================================================
# EXECUTIVE ACTION REQUIRED
# =====================================================

try:
    priority_snapshot = build_priority_queue()
    show_action_required(priority_snapshot)
except Exception:
    st.warning("Action Required summary could not be loaded.")


# =====================================================
# EMPTY STATE
# =====================================================

if df.empty:
    show_section_intro(
        selected_tab,
        "No records are available for the selected filters."
    )

    st.warning("No data found for this section.")

else:

    # =====================================================
    # MONTHLY OVERVIEW
    # =====================================================

    if selected_tab == "Monthly Overview":
        show_section_intro(
            "Monthly Overview",
            "Executive summary of commissions, fixes, grand totals and outstanding payables."
        )

        total_commissions = safe_sum(df, "Total Commissions")
        total_fixes = safe_sum(df, "Total Fixes")
        grand_total = safe_sum(df, "Grand Total")

        omg_unpaid = safe_sum(df, "OMG Unpaid")
        ws_unpaid = safe_sum(df, "WS Unpaid")
        total_unpaid = omg_unpaid + ws_unpaid

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Commissions", format_currency(total_commissions))
        col2.metric("Total Fixes", format_currency(total_fixes))
        col3.metric("Grand Total", format_currency(grand_total))

        st.markdown("")

        col4, col5, col6 = st.columns(3)

        col4.metric("OMG Outstanding", format_currency(omg_unpaid))
        col5.metric("WS Outstanding", format_currency(ws_unpaid))
        col6.metric("Total Outstanding", format_currency(total_unpaid))

        st.markdown("### Payables Alert")

        if total_unpaid > 10000:
            st.error(f"High outstanding payables: {format_currency(total_unpaid)}")
        elif total_unpaid > 5000:
            st.warning(f"Medium outstanding payables: {format_currency(total_unpaid)}")
        else:
            st.success(f"Outstanding payables under control: {format_currency(total_unpaid)}")

        if total_unpaid > 0:
            main_exposure = (
                "OMG" if omg_unpaid > ws_unpaid
                else "WS" if ws_unpaid > omg_unpaid
                else "OMG and WS equally"
            )

            summary = (
                f"Outstanding payables currently stand at {format_currency(total_unpaid)}. "
                f"The highest exposure is associated with {main_exposure}. "
                f"These amounts should be reviewed before the upcoming payment cycle."
            )
        else:
            summary = "There are currently no outstanding payables requiring attention."

        st.info(summary)

        chart_tab1, chart_tab2 = st.tabs([
            "Grand Total Trend",
            "Outstanding Payables"
        ])

        with chart_tab1:
            if "Month" in df.columns and "Grand Total" in df.columns:
                chart_df = df.copy()
                chart_df["Grand Total"] = clean_numeric(chart_df["Grand Total"])
                st.bar_chart(chart_df[["Month", "Grand Total"]].set_index("Month"))
            else:
                st.caption("Grand Total chart is not available for this data structure.")

        with chart_tab2:
            if (
                "Month" in df.columns
                and "OMG Unpaid" in df.columns
                and "WS Unpaid" in df.columns
            ):
                chart_df = df.copy()
                chart_df["OMG Unpaid"] = clean_numeric(chart_df["OMG Unpaid"])
                chart_df["WS Unpaid"] = clean_numeric(chart_df["WS Unpaid"])
                st.bar_chart(
                    chart_df[["Month", "OMG Unpaid", "WS Unpaid"]].set_index("Month")
                )
            else:
                st.caption("Outstanding payables chart is not available for this data structure.")


    # =====================================================
    # PAYMENT PRIORITY QUEUE
    # =====================================================

    elif selected_tab == "Payment Priority Queue":
        show_section_intro(
            "Payment Priority Queue",
            "Prioritised view of overdue, pending and unpaid invoices for payment review."
        )

        amount_col = find_amount_column(df)

        high_count = len(df[df["Priority Type"] == "Overdue"]) if "Priority Type" in df.columns else 0
        pending_count = len(df[df["Priority Type"] == "Pending"]) if "Priority Type" in df.columns else 0
        unpaid_count = len(df[df["Priority Type"] == "Unpaid"]) if "Priority Type" in df.columns else 0

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Overdue Items", high_count)
        col2.metric("Pending Items", pending_count)
        col3.metric("Unpaid Items", unpaid_count)

        if amount_col:
            total_priority_amount = clean_numeric(df[amount_col]).sum()
            col4.metric("Queue Amount", format_currency(total_priority_amount))
        else:
            col4.metric("Queue Amount", "N/A")

        st.info(
            "This queue prioritises overdue payments first, followed by pending and unpaid items. "
            "Within each group, higher amounts are shown first."
        )

        show_smart_payment_recommendation(df)


    # =====================================================
    # OTHER SECTIONS
    # =====================================================

    else:
        show_section_intro(
            selected_tab,
            "Detailed operational view with totals, filters and export options."
        )

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not numeric_cols:
            possible_amount_cols = [
                "Amount",
                "Grand Total",
                "Total",
                "Net",
                "Commission",
                "Total Amount",
                "Total Commissions",
            ]

            numeric_cols = [col for col in possible_amount_cols if col in df.columns]

        if numeric_cols:
            metric_cols = st.columns(min(4, len(numeric_cols)))

            for i, col in enumerate(numeric_cols[:4]):
                metric_cols[i].metric(
                    col,
                    format_currency(safe_sum(df, col))
                )

        else:
            st.caption("No numeric totals detected for this section.")


    # =====================================================
    # DATA TABLE + EXPORTS
    # =====================================================

    st.markdown("### Data Table")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    show_downloads(df, selected_tab)
