import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="E-Commerce Customer Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.main { background-color: #0d0f14; }
.block-container { padding: 2rem 3rem; }

.metric-card {
    background: linear-gradient(135deg, #1a1d26 0%, #12151f 100%);
    border: 1px solid #2a2d3e;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #f0a500; }
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #f0a500;
    margin: 0;
}
.metric-label {
    font-size: 0.78rem;
    color: #8b8fa8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.3rem;
}

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8eaf2;
    border-left: 4px solid #f0a500;
    padding-left: 0.8rem;
    margin: 2rem 0 1rem 0;
}

.insight-box {
    background: #12151f;
    border: 1px solid #2a2d3e;
    border-left: 4px solid #f0a500;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.8rem;
    color: #c8cad8;
    font-size: 0.92rem;
    line-height: 1.6;
}

.stSelectbox label, .stMultiSelect label { color: #8b8fa8 !important; }

div[data-testid="stSidebar"] {
    background: #10121a;
    border-right: 1px solid #1e2130;
}
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    rfm       = pd.read_csv("data/Rfm_segments.csv")
    monthly   = pd.read_csv("data/Monthly_revenue.csv")
    city_rank = pd.read_csv("data/cutomer_city_rank.csv")
    running   = pd.read_csv("data/running_total_revenue_by_customer.csv")
    return rfm, monthly, city_rank, running

rfm, monthly, city_rank, running = load_data()

# ── Colour palette ────────────────────────────────────────────────────────────
SEG_COLORS = {
    "Champions":        "#f0a500",
    "Loyal Customers":  "#3ecf8e",
    "Potential Loyalists": "#4f9cf9",
    "New Customers":    "#a78bfa",
    "Need Attention":   "#fb923c",
    "At Risk":          "#f87171",
    "Cant Lose Them":   "#e879f9",
    "Lost Customers":   "#64748b",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#c8cad8"),
    margin=dict(t=40, b=30, l=20, r=20),
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 E-Com Analytics")
    st.markdown("<hr style='border-color:#1e2130'>", unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["📊 Overview", "👥 Customer Segments", "📈 Revenue Trends", "🏙️ City Analysis", "💡 Business Insights"],
        label_visibility="collapsed"
    )
    st.markdown("<hr style='border-color:#1e2130'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b8fa8;font-size:0.75rem'>SQL · Python · Plotly<br>by Munshi Masudur Rahaman</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# E-Commerce Customer Analytics")
    st.markdown("<p style='color:#8b8fa8;margin-top:-0.5rem'>RFM Segmentation · Revenue Analysis · City Intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")

    total_customers  = len(rfm)
    total_revenue    = rfm["monetary"].sum()
    avg_spend        = rfm["monetary"].mean()
    avg_recency      = rfm["recency_days"].mean()
    top_segment      = rfm.groupby("segment")["monetary"].sum().idxmax()
    peak_mom         = monthly["mom_growth_pct"].max()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, val, label in zip(
        [c1, c2, c3, c4, c5, c6],
        [total_customers, f"₹{total_revenue:,.0f}", f"₹{avg_spend:,.0f}", f"{avg_recency:.0f} days", top_segment, f"{peak_mom:.0f}%"],
        ["Total Customers", "Total Revenue", "Avg Spend/Customer", "Avg Recency", "Top Revenue Segment", "Peak MoM Growth"]
    ):
        col.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{val}</p>
            <p class="metric-label">{label}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Segment Overview</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        seg_agg = rfm.groupby("segment").agg(
            customer_count=("customer_id","count"),
            total_revenue=("monetary","sum")
        ).reset_index()

        fig = px.bar(
            seg_agg.sort_values("total_revenue", ascending=True),
            x="total_revenue", y="segment", orientation="h",
            color="segment", color_discrete_map=SEG_COLORS,
            title="Revenue by Segment (₹)",
            labels={"total_revenue":"Revenue (₹)","segment":""}
        )
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            seg_agg, values="customer_count", names="segment",
            color="segment", color_discrete_map=SEG_COLORS,
            title="Customer Distribution",
            hole=0.55
        )
        fig2.update_layout(**PLOTLY_LAYOUT)
        fig2.update_traces(textfont_size=11)
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CUSTOMER SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Customer Segments":
    st.markdown("# Customer Segments")
    st.markdown("<p style='color:#8b8fa8;margin-top:-0.5rem'>Deep dive into RFM scores and individual customers</p>", unsafe_allow_html=True)
    st.markdown("---")

    segments = rfm["segment"].unique().tolist()
    selected = st.multiselect("Filter by Segment", segments, default=segments)
    filtered = rfm[rfm["segment"].isin(selected)]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(
            filtered,
            x="recency_days", y="frequency",
            size="monetary", color="segment",
            color_discrete_map=SEG_COLORS,
            hover_data=["customer_name","monetary"],
            title="Recency vs Frequency (bubble = spend)",
            labels={"recency_days":"Days Since Last Order","frequency":"# Orders"}
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.scatter(
            filtered,
            x="frequency", y="monetary",
            color="segment", color_discrete_map=SEG_COLORS,
            hover_data=["customer_name","recency_days"],
            title="Frequency vs Monetary Value",
            labels={"frequency":"# Orders","monetary":"Total Spend (₹)"}
        )
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Customer Detail Table</div>", unsafe_allow_html=True)
    display_cols = ["customer_name","city","segment","recency_days","frequency","monetary","r_score","f_score","m_score"]
    st.dataframe(
        filtered[display_cols].rename(columns={
            "customer_name":"Customer","city":"City","segment":"Segment",
            "recency_days":"Recency (days)","frequency":"Orders",
            "monetary":"Total Spend (₹)","r_score":"R","f_score":"F","m_score":"M"
        }).sort_values("Total Spend (₹)", ascending=False).reset_index(drop=True),
        use_container_width=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — REVENUE TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Revenue Trends":
    st.markdown("# Revenue Trends")
    st.markdown("<p style='color:#8b8fa8;margin-top:-0.5rem'>Month-over-Month growth and customer purchase patterns</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly["month"], y=monthly["revenue"],
            name="Monthly Revenue",
            marker_color="#f0a500", opacity=0.85
        ))
        fig.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["revenue"],
            mode="lines+markers", name="Trend",
            line=dict(color="#3ecf8e", width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title="Monthly Revenue (₹)",
                          xaxis_title="Month", yaxis_title="Revenue (₹)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        mom_clean = monthly.dropna(subset=["mom_growth_pct"])
        colors = ["#3ecf8e" if v >= 0 else "#f87171" for v in mom_clean["mom_growth_pct"]]
        fig2 = go.Figure(go.Bar(
            x=mom_clean["month"], y=mom_clean["mom_growth_pct"],
            marker_color=colors, name="MoM Growth %"
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="#8b8fa8")
        fig2.update_layout(**PLOTLY_LAYOUT, title="Month-over-Month Growth (%)",
                           xaxis_title="Month", yaxis_title="Growth %")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Running Revenue by Customer</div>", unsafe_allow_html=True)
    customers = running["customer_name"].unique().tolist()
    sel_cust = st.multiselect("Select Customers", customers, default=customers[:4])
    run_fil = running[running["customer_name"].isin(sel_cust)]

    fig3 = px.line(
        run_fil, x="order_date", y="running_total",
        color="customer_name", markers=True,
        title="Cumulative Revenue per Customer",
        labels={"order_date":"Order Date","running_total":"Running Total (₹)","customer_name":"Customer"}
    )
    fig3.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏙️ City Analysis":
    st.markdown("# City Analysis")
    st.markdown("<p style='color:#8b8fa8;margin-top:-0.5rem'>Top spenders per city and geographic revenue distribution</p>", unsafe_allow_html=True)
    st.markdown("---")

    city_rev = city_rank.groupby("city")["total_spent"].sum().reset_index().sort_values("total_spent", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            city_rev, x="city", y="total_spent",
            color="total_spent", color_continuous_scale=["#1a1d26","#f0a500"],
            title="Total Revenue by City (₹)",
            labels={"city":"City","total_spent":"Revenue (₹)"}
        )
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            city_rev, values="total_spent", names="city",
            title="City Revenue Share", hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Top Customer per City</div>", unsafe_allow_html=True)
    top_per_city = city_rank[city_rank["city_rank"] == 1].sort_values("total_spent", ascending=False)
    st.dataframe(
        top_per_city.rename(columns={
            "customer_name":"Customer","city":"City",
            "total_spent":"Total Spent (₹)","city_rank":"City Rank"
        }).reset_index(drop=True),
        use_container_width=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — BUSINESS INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💡 Business Insights":
    st.markdown("# Business Insights & Recommendations")
    st.markdown("<p style='color:#8b8fa8;margin-top:-0.5rem'>Data-driven actions for each customer segment</p>", unsafe_allow_html=True)
    st.markdown("---")

    seg_agg = rfm.groupby("segment").agg(
        customers=("customer_id","count"),
        avg_recency=("recency_days","mean"),
        avg_orders=("frequency","mean"),
        avg_spend=("monetary","mean"),
        total_revenue=("monetary","sum")
    ).reset_index().sort_values("total_revenue", ascending=False)

    insights = {
        "Champions": ("🏆", "Your highest-value customers. They buy often and spend the most. Reward them with early access to new products, loyalty perks, or referral bonuses. They are also your best brand ambassadors."),
        "Loyal Customers": ("⭐", "Consistent buyers with strong frequency. Upsell premium products or bundles. Send personalised thank-you messages and exclusive member discounts to deepen loyalty."),
        "Potential Loyalists": ("🌱", "Recent customers with growing potential. Nurture with onboarding emails, product recommendations, and a first-loyalty-milestone reward to push them into Champions."),
        "New Customers": ("🆕", "Acquired recently but haven't returned. Focus on first-30-day re-engagement: follow-up email, review request, and a second-purchase discount before interest fades."),
        "Need Attention": ("⚠️", "Above-average RFM in the past but cooling off. Send a personalised 'We miss you' campaign with a time-limited offer. Identify the category they bought and re-target with related products."),
        "At Risk": ("🔴", "Haven't purchased in a while. Aggressive win-back campaign needed — significant discount, free shipping, or a bundled offer. Act before they move to 'Lost'."),
        "Cant Lose Them": ("🚨", "High monetary value but very low recency. These customers spent big but have gone silent. Assign account-level outreach — phone/WhatsApp — not just email."),
        "Lost Customers": ("💀", "Long-lapsed with low spend. Low ROI to re-engage at scale. Run a low-cost reactivation email once. If no response, shift budget to acquiring new customers instead."),
    }

    for _, row in seg_agg.iterrows():
        seg = row["segment"]
        icon, text = insights.get(seg, ("📌", "No specific recommendation available."))
        with st.expander(f"{icon} {seg} — {row['customers']} customers · ₹{row['total_revenue']:,.0f} revenue"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Recency", f"{row['avg_recency']:.0f} days")
            c2.metric("Avg Orders", f"{row['avg_orders']:.1f}")
            c3.metric("Avg Spend", f"₹{row['avg_spend']:,.0f}")
            st.markdown(f"<div class='insight-box'>{text}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Key Takeaways</div>", unsafe_allow_html=True)
    champion_rev = rfm[rfm["segment"]=="Loyal Customers"]["monetary"].sum()
    champion_pct = champion_rev / rfm["monetary"].sum() * 100
    at_risk_count = len(rfm[rfm["segment"].isin(["At Risk","Cant Lose Them"])])

    takeaways = [
        f"Loyal Customers + Champions drive <b>₹{champion_rev:,.0f}</b> ({champion_pct:.0f}% of total revenue) — protect this group at all costs.",
        f"<b>{at_risk_count} customers</b> are At Risk or 'Cant Lose Them' — immediate win-back campaigns could recover significant revenue.",
        f"Peak MoM growth was <b>{monthly['mom_growth_pct'].max():.0f}%</b> — identify what drove that month and replicate the conditions.",
        "Bangalore and Jaipur customers have the highest individual spend — premium product targeting in these cities could boost revenue further.",
    ]
    for t in takeaways:
        st.markdown(f"<div class='insight-box'>📌 {t}</div>", unsafe_allow_html=True)
