import json
from io import BytesIO
from datetime import datetime
from html import escape

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

    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    p, span, label {
        color: inherit;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    [data-testid="stSidebar"] label {
        color: #f8fafc !important;
        font-weight: 700;
    }

    [data-testid="stSidebar"] .stCaptionContainer {
        color: #cbd5e1 !important;
    }

    [data-testid="stSidebar"] input {
        background-color: rgba(15, 23, 42, 0.98) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(148, 163, 184, 0.35) !important;
        border-radius: 12px !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: #94a3b8 !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.98) !important;
        border: 1px solid rgba(148, 163, 184, 0.35) !important;
        border-radius: 12px !important;
        min-height: 48px;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] input {
        color: #f8fafc !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #f8fafc !important;
        color: #f8fafc !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
        border-color: rgba(96, 165, 250, 0.75) !important;
        background-color: rgba(30, 41, 59, 0.98) !important;
    }

    div[data-baseweb="popover"] {
        z-index: 9999 !important;
    }

    div[data-baseweb="popover"] ul {
        background-color: #0f172a !important;
        border: 1px solid rgba(148, 163, 184, 0.35) !important;
    }

    div[data-baseweb="popover"] li {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="popover"] li:hover {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    div[data-baseweb="popover"] li span {
        color: #f8fafc !important;
    }

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

    .action-box {
        background:
            linear-gradient(135deg, rgba(124, 45, 18, 0.58) 0%, rgba(15, 23, 42, 0.96) 55%, rgba(30, 41, 59, 0.94) 100%);
        border: 1px solid rgba(251, 146, 60, 0.44);
        border-left: 6px solid #fb923c;
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 18px;
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

    .recommendation-box {
        background:
            linear-gradient(135deg, rgba(30, 64, 175, 0.50) 0%, rgba(15, 23, 42, 0.96) 55%, rgba(30, 41, 59, 0.94) 100%);
        border: 1px solid rgba(96, 165, 250, 0.44);
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

    .payables-alert-box {
        background:
            linear-gradient(135deg, rgba(127, 29, 29, 0.78) 0%, rgba(69, 10, 10, 0.72) 100%);
        border: 1px solid rgba(248, 113, 113, 0.55);
        border-left: 6px solid #f87171;
        border-radius: 18px;
        padding: 20px 22px;
        margin-top: 12px;
        margin-bottom: 20px;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.30);
    }

    .payables-alert-title {
        color: #fecaca !important;
        font-size: 16px;
        font-weight: 850;
        margin-bottom: 6px;
    }

    .payables-alert-text {
        color: #ffffff !important;
        font-size: 15px;
        font-weight: 700;
        line-height: 1.65;
    }

    .payables-info-box {
        background:
            linear-gradient(135deg, rgba(30, 64, 175, 0.72) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1px solid rgba(96, 165, 250, 0.50);
        border-left: 6px solid #60a5fa;
        border-radius: 18px;
        padding: 20px 22px;
        margin-top: 12px;
        margin-bottom: 24px;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.28);
    }

    .payables-info-title {
        color: #bfdbfe !important;
        font-size: 16px;
        font-weight: 850;
        margin-bottom: 6px;
    }

    .payables-info-text {
        color: #ffffff !important;
        font-size: 15px;
        font-weight: 650;
        line-height: 1.7;
    }

    .payables-success-box {
        background:
            linear-gradient(135deg, rgba(22, 101, 52, 0.75) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1px solid rgba(74, 222, 128, 0.45);
        border-left: 6px solid #4ade80;
        border-radius: 18px;
        padding: 20px 22px;
        margin-top: 12px;
        margin-bottom: 20px;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.28);
    }

    .payables-success-title {
        color: #bbf7d0 !important;
        font-size: 16px;
        font-weight: 850;
        margin-bottom: 6px;
    }

    .payables-success-text {
        color: #ffffff !important;
        font-size: 15px;
        font-weight: 700;
        line-height: 1.65;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
    }

    div[data-testid="stAlert"] * {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 700;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: rgba(15, 23, 42, 0.92);
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        overflow: hidden;
    }

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

    .stCaptionContainer {
        color: #cbd5e1 !important;
    }

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


def find_amount_column(df):
    possible = [
        "Amount",
        "Grand Total",
        "Total",
        "Net",
        "Commission",
        "Total Amount",
        "Total Commissions",
        "OMG Unpaid",
        "WS Unpaid",
        "Total Unpaid",
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


def parse_month_value(value):
    text = str(value).strip()

    if not text:
        return pd.NaT

    formats = [
        "%b-%y",
        "%B-%y",
        "%b %y",
        "%B %y",
        "%b-%Y",
        "%B-%Y",
        "%b %Y",
        "%B %Y",
        "%Y-%m",
        "%m-%Y",
        "%m/%Y",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)
            return pd.Timestamp(parsed.year, parsed.month, 1)
        except ValueError:
            pass

    parsed = pd.to_datetime(text, errors="coerce")

    if pd.notna(parsed):
        return pd.Timestamp(parsed.year, parsed.month, 1)

    return pd.NaT


def month_sort_key(value):
    parsed = parse_month_value(value)

    if pd.notna(parsed):
        return (parsed.year, parsed.month, str(value))

    return (0, 0, str(value))


def sort_dataframe_by_month(df):
    month_col = find_column(df, ["Month"])

    if not month_col or df.empty:
        return df

    sorted_df = df.copy()
    sorted_df["_month_sort"] = sorted_df[month_col].apply(parse_month_value)
    sorted_df["_month_sort_fallback"] = sorted_df[month_col].astype(str)

    sorted_df = sorted_df.sort_values(
        by=["_month_sort", "_month_sort_fallback"],
        ascending=[False, False],
        na_position="last"
    )

    sorted_df = sorted_df.drop(columns=["_month_sort", "_month_sort_fallback"])

    return sorted_df


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


def is_numeric_like_column(series):
    non_empty = series.dropna().astype(str).str.strip()
    non_empty = non_empty[non_empty != ""]

    if non_empty.empty:
        return False

    cleaned = (
        non_empty
        .str.replace("€", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
    )

    converted = pd.to_numeric(cleaned, errors="coerce")
    valid_ratio = converted.notna().mean()

    return valid_ratio >= 0.65


def get_numeric_like_columns(df):
    excluded_exact = {
        "month",
        "invoice",
        "invoice #",
        "invoice number",
        "invoice no",
        "invoice no.",
        "number",
        "no",
        "id",
        "date",
        "status",
        "priority",
        "priority type",
        "priority rank",
        "source",
        "affiliate",
        "partner",
        "platform",
        "brand",
        "display name",
        "partner/display name",
    }

    numeric_cols = []

    for col in df.columns:
        col_lower = str(col).strip().lower()

        if col_lower in excluded_exact:
            continue

        if pd.api.types.is_numeric_dtype(df[col]) or is_numeric_like_column(df[col]):
            numeric_cols.append(col)

    return numeric_cols


def prepare_numeric_dataframe(df):
    numeric_df = df.copy()
    numeric_cols = get_numeric_like_columns(numeric_df)

    for col in numeric_cols:
        numeric_df[col] = clean_numeric(numeric_df[col])

    return numeric_df


def prepare_display_dataframe(df):
    display_df = prepare_numeric_dataframe(df)
    numeric_cols = get_numeric_like_columns(display_df)

    for col in numeric_cols:
        display_df[col] = display_df[col].apply(lambda x: f"{float(x):,.2f}")

    return display_df


def prepare_export_dataframe(df):
    return prepare_display_dataframe(df)


def show_formatted_dataframe(df):
    display_df = prepare_display_dataframe(df)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def download_excel(df):
    output = BytesIO()

    export_df = prepare_numeric_dataframe(df)
    numeric_cols = get_numeric_like_columns(export_df)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Report")
        worksheet = writer.sheets["Report"]

        for col_index, col_name in enumerate(export_df.columns, start=1):
            if col_name in numeric_cols:
                for row in range(2, len(export_df) + 2):
                    worksheet.cell(row=row, column=col_index).number_format = '#,##0.00'

    return output.getvalue()


def get_pdf_font_size(column_count):
    if column_count <= 8:
        return 7.0
    elif column_count <= 10:
        return 6.3
    elif column_count <= 12:
        return 5.7
    elif column_count <= 15:
        return 5.0
    elif column_count <= 18:
        return 4.5
    else:
        return 4.0


def get_pdf_column_widths(columns, available_width):
    weights = []

    for col in columns:
        col_lower = str(col).strip().lower()

        if col_lower == "month":
            weight = 0.9
        elif "invoice" in col_lower:
            weight = 1.25
        elif "affiliate" in col_lower or "partner" in col_lower or "display" in col_lower:
            weight = 1.55
        elif "platform" in col_lower or "brand" in col_lower:
            weight = 1.25
        elif "status" in col_lower or "priority" in col_lower or "source" in col_lower:
            weight = 1.05
        elif "grand total with vat" in col_lower:
            weight = 1.45
        elif "commission" in col_lower:
            weight = 1.35
        elif "total" in col_lower:
            weight = 1.25
        elif "unpaid" in col_lower:
            weight = 1.2
        elif "vat" in col_lower:
            weight = 1.05
        else:
            weight = 1.0

        weights.append(weight)

    total_weight = sum(weights)

    return [
        available_width * weight / total_weight
        for weight in weights
    ]


def download_pdf(df, selected_tab):
    try:
        from reportlab.lib import colors
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A3, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return None

    output = BytesIO()

    page_size = landscape(A3)

    doc = SimpleDocTemplate(
        output,
        pagesize=page_size,
        rightMargin=0.45 * cm,
        leftMargin=0.45 * cm,
        topMargin=0.55 * cm,
        bottomMargin=0.55 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DashboardTitle",
        parent=styles["Title"],
        textColor=HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        spaceAfter=4,
    )

    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        textColor=HexColor("#475569"),
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        spaceAfter=4,
    )

    if df.empty:
        story = []
        generated_at = datetime.now().strftime("%d %b %Y, %H:%M")
        story.append(Paragraph(escape(f"{selected_tab} - Export Report"), title_style))
        story.append(Paragraph(f"Generated from Payments Management Dashboard on {generated_at}", meta_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph("No data available for the selected filters.", meta_style))
        doc.build(story)
        return output.getvalue()

    pdf_df = prepare_display_dataframe(df).copy().fillna("").astype(str)

    all_columns = list(pdf_df.columns)
    column_count = len(all_columns)

    body_font_size = get_pdf_font_size(column_count)
    header_font_size = body_font_size + 0.3

    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        textColor=HexColor("#111827"),
        fontName="Helvetica",
        fontSize=body_font_size,
        leading=body_font_size + 1.2,
        wordWrap="CJK",
    )

    header_style = ParagraphStyle(
        "HeaderText",
        parent=styles["Normal"],
        textColor=colors.white,
        fontName="Helvetica-Bold",
        fontSize=header_font_size,
        leading=header_font_size + 1.2,
        wordWrap="CJK",
    )

    story = []
    generated_at = datetime.now().strftime("%d %b %Y, %H:%M")

    story.append(Paragraph(escape(f"{selected_tab} - Export Report"), title_style))
    story.append(Paragraph(f"Generated from Payments Management Dashboard on {generated_at}", meta_style))
    story.append(Paragraph(f"Rows: {len(pdf_df)} | Columns: {len(pdf_df.columns)}", meta_style))
    story.append(Spacer(1, 6))

    table_data = []

    table_data.append([
        Paragraph(escape(str(col)), header_style)
        for col in all_columns
    ])

    for _, row in pdf_df.iterrows():
        table_data.append([
            Paragraph(escape(str(row[col])), cell_style)
            for col in all_columns
        ])

    available_width = page_size[0] - doc.leftMargin - doc.rightMargin
    col_widths = get_pdf_column_widths(all_columns, available_width)

    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT"
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.18, HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#ffffff")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))

    story.append(table)

    doc.build(story)

    return output.getvalue()


def safe_sum(df, column):
    if column in df.columns:
        return clean_numeric(df[column]).sum()

    return 0


def format_currency(value):
    return f"€{value:,.2f}"


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
            raw_options = (
                filtered[existing_col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if label == "Month":
                sorted_options = sorted(
                    raw_options,
                    key=lambda x: month_sort_key(x),
                    reverse=True
                )
            else:
                sorted_options = sorted(raw_options)

            options = ["All"] + sorted_options

            selected = st.sidebar.selectbox(label, options)

            if selected != "All":
                filtered = filtered[filtered[existing_col].astype(str) == selected]

    filtered = sort_dataframe_by_month(filtered)

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


def show_payables_alert(level, amount):
    if level == "high":
        st.markdown(f"""
        <div class="payables-alert-box">
            <div class="payables-alert-title">Payables Alert</div>
            <div class="payables-alert-text">
                High outstanding payables detected: {format_currency(amount)}.
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif level == "medium":
        st.markdown(f"""
        <div class="payables-alert-box">
            <div class="payables-alert-title">Payables Alert</div>
            <div class="payables-alert-text">
                Medium outstanding payables detected: {format_currency(amount)}.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="payables-success-box">
            <div class="payables-success-title">Payables Alert</div>
            <div class="payables-success-text">
                Outstanding payables are currently under control: {format_currency(amount)}.
            </div>
        </div>
        """, unsafe_allow_html=True)


def show_payables_summary(summary):
    st.markdown(f"""
    <div class="payables-info-box">
        <div class="payables-info-title">Executive Summary Note</div>
        <div class="payables-info-text">
            {summary}
        </div>
    </div>
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


def show_action_required_details(priority_df):
    if priority_df.empty or "Priority Type" not in priority_df.columns:
        return

    amount_col = find_amount_column(priority_df)

    with st.expander("Review Payment Action Items", expanded=False):
        st.caption(
            "These records are pulled from the Overdue Invoices, Pending Invoices and Unpaid Invoices sheets."
        )

        overdue_df = priority_df[priority_df["Priority Type"] == "Overdue"].copy()
        pending_df = priority_df[priority_df["Priority Type"] == "Pending"].copy()
        unpaid_df = priority_df[priority_df["Priority Type"] == "Unpaid"].copy()

        tab_overdue, tab_pending, tab_unpaid = st.tabs([
            f"Overdue ({len(overdue_df)})",
            f"Pending ({len(pending_df)})",
            f"Unpaid ({len(unpaid_df)})",
        ])

        with tab_overdue:
            if overdue_df.empty:
                st.success("No overdue invoices found.")
            else:
                if amount_col:
                    st.metric("Overdue Exposure", format_currency(clean_numeric(overdue_df[amount_col]).sum()))
                show_formatted_dataframe(overdue_df)

        with tab_pending:
            if pending_df.empty:
                st.success("No pending invoices found.")
            else:
                if amount_col:
                    st.metric("Pending Exposure", format_currency(clean_numeric(pending_df[amount_col]).sum()))
                show_formatted_dataframe(pending_df)

        with tab_unpaid:
            if unpaid_df.empty:
                st.success("No unpaid invoices found.")
            else:
                if amount_col:
                    st.metric("Unpaid Exposure", format_currency(clean_numeric(unpaid_df[amount_col]).sum()))
                show_formatted_dataframe(unpaid_df)


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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Download CSV",
            data=prepare_export_dataframe(df).to_csv(index=False).encode("utf-8-sig"),
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

    with col3:
        pdf_data = download_pdf(df, selected_tab)

        if pdf_data is None:
            st.warning("PDF export requires `reportlab` in requirements.txt")
        else:
            st.download_button(
                "Download PDF",
                data=pdf_data,
                file_name=f"{selected_tab.replace(' ', '_')}.pdf",
                mime="application/pdf",
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
    show_action_required_details(priority_snapshot)
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
            show_payables_alert("high", total_unpaid)
        elif total_unpaid > 5000:
            show_payables_alert("medium", total_unpaid)
        else:
            show_payables_alert("low", total_unpaid)

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

        show_payables_summary(summary)

        chart_tab1, chart_tab2 = st.tabs([
            "Grand Total Trend",
            "Outstanding Payables"
        ])

        with chart_tab1:
            if "Month" in df.columns and "Grand Total" in df.columns:
                chart_df = sort_dataframe_by_month(df.copy())
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
                chart_df = sort_dataframe_by_month(df.copy())
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

        numeric_cols = get_numeric_like_columns(df)

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

    show_formatted_dataframe(df)

    st.markdown("---")

    show_downloads(df, selected_tab)
