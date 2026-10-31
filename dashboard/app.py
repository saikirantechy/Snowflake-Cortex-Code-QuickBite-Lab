"""QuickBite – Refund Crisis & Delivery Performance Intelligence.

Board-ready dashboard over QUICKBITE_DB.RAW / ANALYTICS. Credentials come from the
local Snowflake connection config (~/.snowflake/config.toml) – nothing is hard-coded.
"""
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import snowflake.connector
import streamlit as st

st.set_page_config(
    page_title="QuickBite – Refund Crisis Intelligence",
    page_icon=":material/delivery_dining:",
    layout="wide",
)

DB = "QUICKBITE_DB"
RELEASE_DATE = "2026-09-08"
LATE_MIN = 45
BASE_MONTH, CUR_MONTH = "2026-08-01", "2026-10-01"
COLORS = {"focus": "#E4572E", "other": "#7B8794", "good": "#2E86AB", "rain": "#2E86AB", "dry": "#F2A541"}


@st.cache_resource(show_spinner=False)
def get_conn():
    # Credentials are resolved from the named connection in ~/.snowflake/config.toml
    return snowflake.connector.connect(
        connection_name=os.getenv("SNOWFLAKE_DEFAULT_CONNECTION_NAME") or "default",
        role=os.getenv("QUICKBITE_ROLE", "SYSADMIN"),
        warehouse=os.getenv("QUICKBITE_WAREHOUSE", "COMPUTE_WH"),
        database=DB,
        schema="RAW",
        client_session_keep_alive=True,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def run(sql: str, params: tuple | None = None) -> pd.DataFrame:
    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        df = cur.fetch_pandas_all()
    df.columns = [c.lower() for c in df.columns]
    # Snowflake NUMBER comes back as Decimal/object – coerce to float for charts
    for c in df.columns:
        if df[c].dtype == object:
            try:
                df[c] = pd.to_numeric(df[c])
            except (ValueError, TypeError):
                pass
    return df


def inr(v: float) -> str:
    return f"₹{v / 1e5:,.2f} L" if abs(v) >= 1e5 else f"₹{v:,.0f}"


def release_marker(fig: go.Figure) -> go.Figure:
    # add_vline with annotation breaks on date axes; use shape + annotation instead
    fig.add_shape(type="line", x0=RELEASE_DATE, x1=RELEASE_DATE, y0=0, y1=1, yref="paper",
                  line=dict(color="#C0392B", dash="dash", width=2))
    fig.add_annotation(x=RELEASE_DATE, y=1, yref="paper", text="v2.3 (8 Sep)",
                       showarrow=False, xanchor="left", yanchor="bottom", font=dict(color="#C0392B"))
    # pin the x-range to the data so the annotation can't stretch the autorange
    xs = pd.concat([pd.Series(t.x) for t in fig.data])
    fig.update_xaxes(range=[pd.to_datetime(xs.min()), pd.to_datetime(xs.max())])
    return fig


def style(fig: go.Figure, h: int = 360) -> go.Figure:
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=40, b=10), legend_title_text="",
                      plot_bgcolor="white", hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEE")
    return fig


# ---------------------------------------------------------------- queries
# All percentages are computed in SQL on a 0–100 scale. Do NOT multiply by 100 again in Python.
Q_MONTHLY = f"""
SELECT DATE_TRUNC('month', o.PLACED_AT)::DATE AS month, COUNT(*) AS orders,
       SUM(o.ORDER_VALUE_INR) AS gmv, SUM(COALESCE(r.REFUND_AMOUNT_INR,0)) AS refunds,
       COUNT(r.REFUND_ID) AS refund_count,
       ROUND(100 * SUM(COALESCE(r.REFUND_AMOUNT_INR,0)) / SUM(o.ORDER_VALUE_INR), 2) AS refund_pct
FROM {DB}.RAW.ORDERS o LEFT JOIN {DB}.RAW.REFUNDS r ON r.ORDER_ID = o.ORDER_ID
GROUP BY 1 ORDER BY 1"""

Q_ZONE_DELTA = f"""
SELECT o.CITY AS city, z.ZONE_NAME AS zone, rf.REFUND_REASON AS reason,
       SUM(IFF(DATE_TRUNC('month',o.PLACED_AT) = %s, rf.REFUND_AMOUNT_INR, 0)) AS base_amt,
       SUM(IFF(DATE_TRUNC('month',o.PLACED_AT) = %s, rf.REFUND_AMOUNT_INR, 0)) AS cur_amt
FROM {DB}.RAW.ORDERS o JOIN {DB}.RAW.REFUNDS rf ON rf.ORDER_ID = o.ORDER_ID
JOIN {DB}.RAW.CITIES_ZONES z ON z.ZONE_ID = o.ZONE_ID
GROUP BY 1,2,3"""

Q_WEEKLY = f"""
SELECT DATE_TRUNC('week', o.PLACED_AT)::DATE AS week, z.ZONE_NAME AS zone, COUNT(*) AS orders,
       COUNT_IF(DATEDIFF('minute', o.PLACED_AT, o.DELIVERED_AT) > {LATE_MIN}) AS late_orders,
       SUM(o.RIDER_ASSIGN_DISTANCE_KM) AS assign_km_sum,
       SUM(DATEDIFF('second', o.ACCEPTED_AT, o.PICKED_UP_AT)) / 60 AS pickup_wait_min_sum
FROM {DB}.RAW.ORDERS o JOIN {DB}.RAW.CITIES_ZONES z ON z.ZONE_ID = o.ZONE_ID
WHERE o.PLACED_AT >= '2026-06-01'
GROUP BY 1,2"""

Q_PERIOD = f"""
SELECT IFF(z.ZONE_NAME = %s, 'sel', 'other') AS grp,
       IFF(o.PLACED_AT >= '{RELEASE_DATE}', 'post', 'pre') AS period,
       ROUND(100 * COUNT_IF(DATEDIFF('minute', o.PLACED_AT, o.DELIVERED_AT) > {LATE_MIN}) / COUNT(*), 1) AS late_pct,
       ROUND(AVG(o.RIDER_ASSIGN_DISTANCE_KM), 2) AS avg_km,
       ROUND(AVG(DATEDIFF('second', o.ACCEPTED_AT, o.PICKED_UP_AT)) / 60, 1) AS wait_min
FROM {DB}.RAW.ORDERS o JOIN {DB}.RAW.CITIES_ZONES z ON z.ZONE_ID = o.ZONE_ID
GROUP BY 1,2"""

Q_WEATHER = f"""
SELECT IFF(z.ZONE_NAME = %s, 'Selected zone', 'All other zones') AS grp,
       IFF(o.PLACED_AT >= '{RELEASE_DATE}', 'After 8 Sep', 'Before 8 Sep') AS period,
       IFF(w.RAIN_MM > 0, 'Rainy hour', 'Dry hour') AS weather,
       COUNT(*) AS orders,
       ROUND(100 * COUNT_IF(DATEDIFF('minute', o.PLACED_AT, o.DELIVERED_AT) > {LATE_MIN}) / COUNT(*), 1) AS late_pct,
       ROUND(100 * COUNT(rf.REFUND_ID) / COUNT(*), 1) AS refund_order_pct
FROM {DB}.RAW.ORDERS o JOIN {DB}.RAW.CITIES_ZONES z ON z.ZONE_ID = o.ZONE_ID
JOIN {DB}.RAW.WEATHER_HOURLY w ON w.CITY = o.CITY AND w.HOUR_TS = DATE_TRUNC('hour', o.PLACED_AT)
LEFT JOIN {DB}.RAW.REFUNDS rf ON rf.ORDER_ID = o.ORDER_ID
GROUP BY 1,2,3"""

Q_CLOUD = f"""
SELECT rs.CLUSTER AS cluster, COUNT(*) AS orders, SUM(o.ORDER_VALUE_INR) AS gmv,
       COUNT(rf.REFUND_ID) AS refunds, SUM(COALESCE(rf.REFUND_AMOUNT_INR,0)) AS refund_amt,
       COUNT_IF(rf.REFUND_REASON = 'Missing item') AS missing_item_refunds,
       SUM(IFF(rf.REFUND_REASON = 'Missing item', rf.REFUND_AMOUNT_INR, 0)) AS missing_item_amt,
       ROUND(100 * COUNT(rf.REFUND_ID) / COUNT(*), 2) AS refund_order_pct,
       ROUND(100 * COUNT_IF(rf.REFUND_REASON = 'Missing item') / COUNT(*), 2) AS missing_item_pct
FROM {DB}.RAW.ORDERS o LEFT JOIN {DB}.RAW.REFUNDS rf ON rf.ORDER_ID = o.ORDER_ID
JOIN {DB}.RAW.RESTAURANTS rs ON rs.RESTAURANT_ID = o.RESTAURANT_ID
WHERE DATE_TRUNC('month', o.PLACED_AT) = %s
GROUP BY 1"""

Q_CHATS = f"SELECT THEME AS theme, COUNT(*) AS chats FROM {DB}.ANALYTICS.WFE_CHAT_CLASSIFIED GROUP BY 1 ORDER BY 2 DESC"
Q_CHAT_SAMPLES = f"""
SELECT THEME AS theme, MESSAGE AS message FROM {DB}.ANALYTICS.WFE_CHAT_CLASSIFIED
QUALIFY ROW_NUMBER() OVER (PARTITION BY THEME ORDER BY CHAT_AT DESC) <= 3 ORDER BY theme"""
Q_SUMMARY = f"SELECT CHAT_COUNT AS chat_count, SUMMARY AS summary FROM {DB}.ANALYTICS.WFE_CHAT_SUMMARY"
Q_ZONES = f"SELECT ZONE_NAME AS zone, CITY AS city FROM {DB}.RAW.CITIES_ZONES ORDER BY CITY, ZONE_NAME"

# ---------------------------------------------------------------- header
st.title("QuickBite – Refund Crisis & Delivery Performance Intelligence")
st.caption("Understanding the 40% Refund Increase | August–October 2026  ·  Source: QUICKBITE_DB (Snowflake)")

try:
    with st.spinner("Loading data from Snowflake…"):
        monthly = run(Q_MONTHLY)
        zone_delta = run(Q_ZONE_DELTA, (BASE_MONTH, CUR_MONTH))
        zones = run(Q_ZONES)
except Exception as e:  # noqa: BLE001
    st.error(f"Could not connect to or query Snowflake: {e}")
    st.info("Check SNOWFLAKE_DEFAULT_CONNECTION_NAME and that the role can read QUICKBITE_DB.")
    st.stop()

monthly["month"] = pd.to_datetime(monthly["month"])
aug = monthly[monthly["month"] == BASE_MONTH].iloc[0]
octo = monthly[monthly["month"] == CUR_MONTH].iloc[0]
total_delta = octo["refunds"] - aug["refunds"]

zd = zone_delta.groupby(["city", "zone"], as_index=False)[["base_amt", "cur_amt"]].sum()
zd["delta"] = zd["cur_amt"] - zd["base_amt"]
zd["share_pct"] = 100 * zd["delta"] / zd["delta"].sum()
zd = zd.sort_values("delta", ascending=False)
top = zd.iloc[0]

# ---------------------------------------------------------------- 1. KPIs
st.subheader("1 · Executive summary")
k1, k2, k3, k4 = st.columns(4)
k1.metric("October refunds", inr(octo["refunds"]),
          f"{100 * (octo['refunds'] / aug['refunds'] - 1):+.1f}% vs Aug", delta_color="inverse", border=True)
k2.metric("Refund % of GMV (Oct)", f"{octo['refund_pct']:.2f}%",
          f"{octo['refund_pct'] - aug['refund_pct']:+.2f} pts vs Aug", delta_color="inverse", border=True)
k3.metric("October orders", f"{int(octo['orders']):,}",
          f"{100 * (octo['orders'] / aug['orders'] - 1):+.1f}% vs Aug", border=True)
k4.metric(f"{top['zone']} share of increase", f"{top['share_pct']:.0f}%",
          f"{inr(top['delta'])} of {inr(total_delta)}", delta_color="off", border=True)

st.info(
    f"**Verified finding:** Refunds rose {inr(total_delta)} (Aug→Oct) while orders grew only "
    f"{100 * (octo['orders'] / aug['orders'] - 1):.0f}%. **{top['zone']} ({top['city']})** alone explains "
    f"{top['share_pct']:.0f}% of the increase, starting right after the **rider-assign v2.3** release on 8 Sep 2026.",
    icon=":material/insights:",
)

# ---------------------------------------------------------------- 2. Monthly
st.subheader("2 · Monthly performance (2026)")
metric_opt = st.segmented_control(
    "Metric", ["Refunds (₹)", "GMV (₹)", "Orders", "Refund % of GMV"], default="Refunds (₹)",
    label_visibility="collapsed",
)
col_map = {"Refunds (₹)": "refunds", "GMV (₹)": "gmv", "Orders": "orders", "Refund % of GMV": "refund_pct"}
ycol = col_map[metric_opt or "Refunds (₹)"]
c1, c2 = st.columns([2, 1])
with c1:
    if ycol == "refund_pct":
        fig = px.line(monthly, x="month", y=ycol, markers=True, labels={ycol: "Refund % of GMV", "month": ""})
        fig.update_traces(line_color=COLORS["focus"])
        fig.update_yaxes(ticksuffix="%")
    else:
        fig = px.bar(monthly, x="month", y=ycol, labels={ycol: metric_opt, "month": ""})
        fig.update_traces(marker_color=[COLORS["focus"] if m >= pd.Timestamp("2026-09-01") else COLORS["other"]
                                        for m in monthly["month"]])
    st.plotly_chart(style(fig), use_container_width=True)
with c2:
    show = monthly.assign(month=monthly["month"].dt.strftime("%b %Y"))[["month", "orders", "gmv", "refunds", "refund_pct"]]
    st.dataframe(show, hide_index=True, use_container_width=True, height=360,
                 column_config={"gmv": st.column_config.NumberColumn("GMV ₹", format="%d"),
                                "refunds": st.column_config.NumberColumn("Refunds ₹", format="%d"),
                                "refund_pct": st.column_config.NumberColumn("Refund %", format="%.2f%%"),
                                "orders": st.column_config.NumberColumn("Orders", format="%d")})

# ---------------------------------------------------------------- 3. Zone
st.subheader("3 · Where did the refund increase come from? (Aug → Oct)")
c1, c2 = st.columns(2)
with c1:
    city = zd.groupby("city", as_index=False)["delta"].sum().sort_values("delta")
    fig = px.bar(city, x="delta", y="city", orientation="h", title="Refund increase by city (₹)",
                 labels={"delta": "₹ increase", "city": ""})
    fig.update_traces(marker_color=[COLORS["focus"] if c == top["city"] else COLORS["other"] for c in city["city"]])
    st.plotly_chart(style(fig), use_container_width=True)
with c2:
    z10 = zd.head(10).sort_values("delta")
    fig = px.bar(z10, x="delta", y="zone", orientation="h", title="Top 10 zones by refund increase (₹)",
                 hover_data={"city": True, "share_pct": ":.1f"}, labels={"delta": "₹ increase", "zone": ""})
    fig.update_traces(marker_color=[COLORS["focus"] if z == top["zone"] else COLORS["other"] for z in z10["zone"]])
    st.plotly_chart(style(fig), use_container_width=True)

reasons = zone_delta.assign(scope=lambda d: d["zone"].where(d["zone"] == top["zone"], "All other zones"))
reasons = reasons.groupby(["scope", "reason"], as_index=False)[["base_amt", "cur_amt"]].sum()
reasons = reasons.melt(id_vars=["scope", "reason"], value_vars=["base_amt", "cur_amt"], var_name="month", value_name="amount")
reasons["month"] = reasons["month"].map({"base_amt": "Aug 2026", "cur_amt": "Oct 2026"})
fig = px.bar(reasons, x="reason", y="amount", color="month", barmode="group", facet_col="scope",
             title="Refund amount by reason", labels={"amount": "₹", "reason": ""},
             color_discrete_map={"Aug 2026": COLORS["other"], "Oct 2026": COLORS["focus"]})
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
st.plotly_chart(style(fig, 380), use_container_width=True)

# ---------------------------------------------------------------- 4. Delivery
st.subheader("4 · Delivery performance & the rider-assign v2.3 release")
zone_list = zones["zone"].tolist()
sel = st.selectbox("Zone", zone_list, index=zone_list.index("Whitefield-East") if "Whitefield-East" in zone_list else 0)

try:
    with st.spinner("Loading weekly delivery metrics…"):
        wk = run(Q_WEEKLY)
except Exception as e:  # noqa: BLE001
    st.error(f"Weekly delivery query failed: {e}")
    wk = pd.DataFrame()

if not wk.empty:
    wk["week"] = pd.to_datetime(wk["week"])
    wk["grp"] = wk["zone"].where(wk["zone"] == sel, "All other zones")
    g = wk.groupby(["week", "grp"], as_index=False)[["orders", "late_orders", "assign_km_sum", "pickup_wait_min_sum"]].sum()
    # late_pct is a 0–100 value: late_orders / orders * 100 (computed once, here)
    g["late_pct"] = 100 * g["late_orders"] / g["orders"]
    g["avg_assign_km"] = g["assign_km_sum"] / g["orders"]
    g["avg_pickup_wait"] = g["pickup_wait_min_sum"] / g["orders"]
    # drop the partial first/last weeks
    g = g[(g["week"] > g["week"].min()) & (g["week"] < g["week"].max())]
    cmap = {sel: COLORS["focus"], "All other zones": COLORS["other"]}

    fig = px.line(g, x="week", y="late_pct", color="grp", markers=True, color_discrete_map=cmap,
                  title=f"Weekly late-delivery % (> {LATE_MIN} min)", labels={"late_pct": "Late %", "week": ""})
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    st.plotly_chart(style(release_marker(fig)), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(g, x="week", y="avg_assign_km", color="grp", color_discrete_map=cmap,
                      title="Avg rider assignment distance (km)", labels={"avg_assign_km": "km", "week": ""})
        st.plotly_chart(style(release_marker(fig), 320), use_container_width=True)
    with c2:
        fig = px.line(g, x="week", y="avg_pickup_wait", color="grp", color_discrete_map=cmap,
                      title="Avg pickup waiting time (accepted → picked up, min)",
                      labels={"avg_pickup_wait": "minutes", "week": ""})
        st.plotly_chart(style(release_marker(fig), 320), use_container_width=True)

    # Before/after split at order level (weekly buckets straddle 8 Sep)
    pp = run(Q_PERIOD, (sel,)).set_index(["grp", "period"])
    s_pre, s_post, o_pre, o_post = (pp.loc[k] for k in [("sel", "pre"), ("sel", "post"), ("other", "pre"), ("other", "post")])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{sel} late % (after 8 Sep)", f"{s_post['late_pct']:.1f}%",
              f"{s_post['late_pct'] - s_pre['late_pct']:+.1f} pts (before: {s_pre['late_pct']:.1f}%)", delta_color="inverse", border=True)
    m2.metric(f"{sel} avg assign distance", f"{s_post['avg_km']:.2f} km",
              f"{s_post['avg_km'] - s_pre['avg_km']:+.2f} km (before: {s_pre['avg_km']:.2f})", delta_color="inverse", border=True)
    m3.metric(f"{sel} pickup wait", f"{s_post['wait_min']:.1f} min",
              f"{s_post['wait_min'] - s_pre['wait_min']:+.1f} min (before: {s_pre['wait_min']:.1f})", delta_color="inverse", border=True)
    m4.metric("All other zones late % (after 8 Sep)", f"{o_post['late_pct']:.1f}%",
              f"{o_post['late_pct'] - o_pre['late_pct']:+.1f} pts (before: {o_pre['late_pct']:.1f}%)", delta_color="inverse", border=True)

# ---------------------------------------------------------------- 5. Weather
st.subheader(f"5 · Weather impact – {sel}")
try:
    with st.spinner("Joining orders with hourly weather…"):
        wx = run(Q_WEATHER, (sel,))
except Exception as e:  # noqa: BLE001
    st.error(f"Weather query failed: {e}")
    wx = pd.DataFrame()

if not wx.empty:
    wx["grp"] = wx["grp"].replace("Selected zone", sel)
    wx["period"] = pd.Categorical(wx["period"], ["Before 8 Sep", "After 8 Sep"])
    wx = wx.sort_values(["grp", "period", "weather"])
    fig = px.bar(wx, x="period", y="late_pct", color="weather", barmode="group", facet_col="grp", text="late_pct",
                 title="Late-delivery % – rainy vs dry hours (weather matched on city + order hour)",
                 labels={"late_pct": "Late %", "period": ""},
                 color_discrete_map={"Rainy hour": COLORS["rain"], "Dry hour": COLORS["dry"]},
                 category_orders={"grp": [sel, "All other zones"]})
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_yaxes(ticksuffix="%")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(style(fig, 400), use_container_width=True)
    with st.expander("Weather comparison table"):
        st.dataframe(wx, hide_index=True, use_container_width=True,
                     column_config={"late_pct": st.column_config.NumberColumn("Late %", format="%.1f%%"),
                                    "refund_order_pct": st.column_config.NumberColumn("Orders refunded %", format="%.1f%%")})
    st.caption("Correlation, not proof of causation: rain amplifies delays where riders are already assigned from far away; "
               "in zones without the distance change, rain only moves late % modestly.")

# ---------------------------------------------------------------- 6. Cloud kitchens
st.subheader("6 · Red herring check – Cloud Kitchens Hub (launched 1 Sep 2026)")
try:
    ck = run(Q_CLOUD, (CUR_MONTH,))
    ck_row = ck[ck["cluster"] == "Cloud Kitchens Hub"].iloc[0]
    std_row = ck[ck["cluster"] == "Standard"].iloc[0]
    expected = ck_row["gmv"] * std_row["refund_amt"] / std_row["gmv"]
    excess = ck_row["refund_amt"] - expected
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CK Hub Oct refunds (all new)", inr(ck_row["refund_amt"]), f"{100 * ck_row['refund_amt'] / total_delta:.1f}% of increase",
              delta_color="off", border=True)
    c2.metric("Excess vs Standard refund rate", inr(excess), f"{100 * excess / total_delta:.1f}% of increase", delta_color="off", border=True)
    c3.metric("CK Hub missing-item refunds", f"{int(ck_row['missing_item_refunds'])} · {inr(ck_row['missing_item_amt'])}",
              f"{ck_row['missing_item_pct']:.1f}% of orders vs {std_row['missing_item_pct']:.1f}%", delta_color="off", border=True)
    c4.metric(f"{top['zone']} contribution", inr(top["delta"]), f"{top['share_pct']:.1f}% of increase", delta_color="off", border=True)
    comp = pd.DataFrame({"source": ["Cloud Kitchens Hub (total)", f"{top['zone']}"],
                         "amount": [ck_row["refund_amt"], top["delta"]]})
    fig = px.bar(comp, x="amount", y="source", orientation="h", text="amount",
                 title="Contribution to the ₹ refund increase (Aug→Oct)", labels={"amount": "₹", "source": ""})
    fig.update_traces(marker_color=[COLORS["other"], COLORS["focus"]], texttemplate="₹%{text:,.0f}")
    st.plotly_chart(style(fig, 260), use_container_width=True)
    st.success("**Conclusion:** Cloud Kitchens Hub does show a higher missing-item rate, but its total refund contribution is "
               "small (a few thousand ₹ in excess). It is **not** the primary cause.", icon=":material/fact_check:")
except Exception as e:  # noqa: BLE001
    st.error(f"Cloud Kitchens query failed: {e}")

# ---------------------------------------------------------------- 7. AI
st.subheader("7 · Customer complaint intelligence (Cortex AI) – Whitefield-East chats since 8 Sep")
try:
    chats = run(Q_CHATS)
    samples = run(Q_CHAT_SAMPLES)
    summ = run(Q_SUMMARY)
    total_chats = int(chats["chats"].sum())
    chats["pct"] = 100 * chats["chats"] / total_chats
    c1, c2 = st.columns([1, 1])
    with c1:
        st.metric("Chats analysed with AI_CLASSIFY", f"{total_chats:,}",
                  f"Top theme: {chats.iloc[0]['theme']} ({int(chats.iloc[0]['chats'])})", delta_color="off", border=True)
        fig = px.pie(chats, names="theme", values="chats", hole=0.55,
                     color_discrete_sequence=[COLORS["focus"], "#F2A541", "#2E86AB", "#7B8794", "#B8C4CE"])
        fig.update_traces(textinfo="percent+label", textposition="outside")
        st.plotly_chart(style(fig, 380).update_layout(showlegend=False), use_container_width=True)
    with c2:
        st.markdown("**AI_SUMMARIZE_AGG summary**")
        st.info(summ.iloc[0]["summary"], icon=":material/smart_toy:")
        st.markdown("**Main pain points**")
        st.markdown("- Riders assigned from far away\n- Long waiting times\n- Food arriving cold\n- Rain-related delays")
    with st.expander("Representative customer messages by theme"):
        st.dataframe(samples, hide_index=True, use_container_width=True)
except Exception as e:  # noqa: BLE001
    st.warning(f"Cortex AI results unavailable (tables in {DB}.ANALYTICS not found or not readable): {e}")

# ---------------------------------------------------------------- 8. Recommendations
st.subheader("8 · Executive recommendations")
f_col, r_col = st.columns(2)
with f_col:
    st.markdown("##### Verified findings (from data)")
    st.markdown(
        f"- Refunds +{100 * (octo['refunds'] / aug['refunds'] - 1):.0f}% Aug→Oct; refund rate "
        f"{aug['refund_pct']:.2f}% → {octo['refund_pct']:.2f}% of GMV.\n"
        f"- {top['zone']} drives {top['share_pct']:.0f}% of the increase – late delivery & cold food.\n"
        "- After rider-assign v2.3 (8 Sep), Whitefield-East assignment distance ~2.1 → ~6.0 km; late % ~7% → ~26%. Other zones unchanged.\n"
        "- Rain amplifies the effect in Whitefield-East (majority of rainy-hour orders late).\n"
        "- Cloud Kitchens Hub is a minor contributor.\n"
        "- 53% of Whitefield-East complaints cite riders assigned too far away."
    )
with r_col:
    st.markdown("##### Recommendations (judgement – to be validated)")
    st.markdown(
        "1. **Roll back / review** the 10 km assignment radius from rider-assign v2.3, starting with Whitefield-East.\n"
        "2. **Cap assignment distance** (e.g. ~3 km) with a zone-level override, and A/B test before network-wide rollout.\n"
        "3. **Improve rider supply** in Whitefield-East (incentives, re-balancing from adjacent zones).\n"
        "4. **Weather-aware planning:** tighter radius + surge rider incentives during rain.\n"
        "5. **Monitor pickup waiting time** (accepted → picked up) as a release guard-rail metric.\n"
        "6. **Food temperature:** insulated bags / hold-time limits for long-distance assignments.\n"
        "7. **Track** refund % of GMV and late % by zone weekly, with alerts on deviation."
    )
st.caption("Data: synthetic QuickBite dataset in Snowflake. Late delivery = placed → delivered > 45 minutes.")
