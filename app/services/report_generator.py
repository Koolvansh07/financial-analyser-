from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _build_category_chart(spending_df: pd.DataFrame) -> BytesIO | None:
    if spending_df.empty:
        return None
    grouped = (
        spending_df.groupby("category", as_index=False)["spend"]
        .sum()
        .sort_values("spend", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.bar(grouped["category"], grouped["spend"], color="#2a9d8f")
    ax.set_title("Spend by Category")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def _build_monthly_chart(spending_df: pd.DataFrame) -> BytesIO | None:
    if spending_df.empty:
        return None
    monthly = spending_df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    grouped = monthly.groupby("month", as_index=False)["spend"].sum()
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.plot(grouped["month"], grouped["spend"], marker="o", color="#264653")
    ax.set_title("Monthly Spending Trend")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_table(data: list[list], column_widths: list[float]) -> Table:
    table = Table(data, colWidths=column_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#264653")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f6")]),
            ]
        )
    )
    return table


def _build_suggestions(spending_df: pd.DataFrame, income_total: float, spent_total: float) -> list[str]:
    if spending_df.empty:
        return ["No debit transactions found. Upload a statement with expenses for spending insights."]

    top = (
        spending_df.groupby("category", as_index=False)["spend"]
        .sum()
        .sort_values("spend", ascending=False)
    )
    suggestions: list[str] = []

    top_category = top.iloc[0]
    top_ratio = (top_category["spend"] / spent_total) if spent_total else 0.0
    suggestions.append(
        f"Top spend category is {top_category['category']} at ${top_category['spend']:.2f} ({top_ratio:.1%} of spending)."
    )

    if income_total > 0:
        savings_rate = (income_total - spent_total) / income_total
        if savings_rate < 0.1:
            suggestions.append("Savings rate is below 10%; consider reducing variable spend in top two categories.")
        elif savings_rate < 0.2:
            suggestions.append("Savings rate is moderate; trimming discretionary spend can improve buffer.")
        else:
            suggestions.append("Savings rate is strong; keep fixed costs stable and automate savings.")
    else:
        suggestions.append("No income transactions detected in this file; verify statement range or income source labels.")

    if "Subscriptions" in set(top["category"]):
        sub_spend = float(top[top["category"] == "Subscriptions"]["spend"].iloc[0])
        if sub_spend > 50:
            suggestions.append("Subscription spend is notable; review active plans and cancel low-use services.")

    return suggestions


def build_finance_report_pdf(transactions: list[dict]) -> bytes:
    df = pd.DataFrame(transactions)
    if df.empty:
        raise ValueError("No transactions available for report generation.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["category"] = df["category"].fillna("Other")
    df = df.dropna(subset=["date", "amount"]).sort_values("date")
    df["is_anomaly"] = df.get("is_anomaly", False).astype(bool)

    spending_df = df[df["amount"] < 0].copy()
    spending_df["spend"] = spending_df["amount"].abs()
    income_df = df[df["amount"] > 0]

    spent_total = float(spending_df["spend"].sum()) if not spending_df.empty else 0.0
    income_total = float(income_df["amount"].sum()) if not income_df.empty else 0.0
    net = income_total - spent_total
    anomalies = int(df["is_anomaly"].sum())

    category_summary = (
        spending_df.groupby("category", as_index=False)["spend"]
        .sum()
        .sort_values("spend", ascending=False)
    )
    monthly_summary = spending_df.assign(month=spending_df["date"].dt.to_period("M").astype(str)).groupby(
        "month", as_index=False
    )["spend"].sum()
    largest = spending_df.nlargest(10, "spend")[["date", "description", "category", "spend"]]
    largest["date"] = largest["date"].dt.strftime("%Y-%m-%d")

    suggestions = _build_suggestions(spending_df, income_total, spent_total)
    category_chart = _build_category_chart(spending_df)
    monthly_chart = _build_monthly_chart(spending_df)

    styles = getSampleStyleSheet()
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    story = [
        Paragraph("Personal Finance Report", styles["Title"]),
        Spacer(1, 8),
        Paragraph(
            f"Transactions: {len(df)} | Income: ${income_total:,.2f} | Spending: ${spent_total:,.2f} | Net: ${net:,.2f} | Anomalies: {anomalies}",
            styles["Normal"],
        ),
        Spacer(1, 14),
        Paragraph("Summary by Category", styles["Heading2"]),
    ]

    cat_table = [["Category", "Amount"]] + [
        [row["category"], f"${row['spend']:,.2f}"] for _, row in category_summary.iterrows()
    ]
    story.append(_make_table(cat_table, [3.9 * inch, 2.3 * inch]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Monthly Spending Summary", styles["Heading2"]))
    month_table = [["Month", "Amount"]] + [
        [row["month"], f"${row['spend']:,.2f}"] for _, row in monthly_summary.iterrows()
    ]
    story.append(_make_table(month_table, [3.9 * inch, 2.3 * inch]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Top 10 Largest Expenses", styles["Heading2"]))
    largest_table = [["Date", "Description", "Category", "Amount"]] + [
        [row["date"], row["description"], row["category"], f"${row['spend']:,.2f}"] for _, row in largest.iterrows()
    ]
    story.append(_make_table(largest_table, [1.2 * inch, 2.9 * inch, 1.4 * inch, 0.9 * inch]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Suggestions", styles["Heading2"]))
    for item in suggestions:
        story.append(Paragraph(f"- {item}", styles["Normal"]))
    story.append(Spacer(1, 10))

    if category_chart is not None:
        story.append(Paragraph("Category Chart", styles["Heading2"]))
        story.append(Image(category_chart, width=6.7 * inch, height=3.5 * inch))
        story.append(Spacer(1, 10))

    if monthly_chart is not None:
        story.append(Paragraph("Monthly Trend Chart", styles["Heading2"]))
        story.append(Image(monthly_chart, width=6.7 * inch, height=3.5 * inch))

    doc.build(story)
    pdf_bytes = output.getvalue()
    output.close()
    return pdf_bytes
