import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Excel Data Analyser",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f1117; }

    /* Hero banner */
    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid #2d3561;
        border-radius: 16px;
        padding: 2.5rem 2rem 2rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 700;
        color: #e8eaf6;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
    }
    .hero p {
        color: #90a4c8;
        font-size: 1.05rem;
        margin: 0;
    }
    .hero .accent { color: #5c7cfa; }

    /* Stat cards */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background: #1a1f2e;
        border: 1px solid #2a3050;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
    }
    .stat-card .label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #5c7cfa;
        margin-bottom: 0.35rem;
    }
    .stat-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e8eaf6;
    }
    .stat-card .sub {
        font-size: 0.8rem;
        color: #6b7a99;
        margin-top: 0.15rem;
    }

    /* Forecast badge */
    .badge-yes {
        display: inline-block;
        background: linear-gradient(135deg, #1b4332, #2d6a4f);
        color: #95d5b2;
        border: 1px solid #40916c;
        border-radius: 20px;
        padding: 0.3rem 0.9rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-no {
        display: inline-block;
        background: linear-gradient(135deg, #3d1a1a, #6b2c2c);
        color: #f4a261;
        border: 1px solid #9b4539;
        border-radius: 20px;
        padding: 0.3rem 0.9rem;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Column section header */
    .col-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #c5cae9;
        border-left: 4px solid #5c7cfa;
        padding-left: 0.75rem;
        margin: 0 0 0.8rem 0;
    }

    /* Info / tip box */
    .tip-box {
        background: #161b2e;
        border: 1px solid #2a3558;
        border-left: 4px solid #5c7cfa;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 2rem;
        color: #8fa5cc;
        font-size: 0.88rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📊 Excel <span class="accent">Data Analyser</span></h1>
    <p>Upload any Excel file · get histograms, mean &amp; median · see if your data is forecast-ready</p>
</div>
""", unsafe_allow_html=True)

# ── Tip box ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tip-box">
    <strong>How it works:</strong>  Upload an <code>.xlsx</code> or <code>.xls</code> file.
    Every numerical column gets a <strong>histogram</strong>, plus its <strong>mean</strong> and <strong>median</strong>.
    If mean ≈ median (within 5 %), the column is flagged as <em>forecast-ready</em> (low skew → more symmetric distribution).
</div>
""", unsafe_allow_html=True)

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Drop your Excel file here", type=["xlsx", "xls"])

# ── Helper ────────────────────────────────────────────────────────────────────
def is_forecast_ready(mean: float, median: float, threshold: float = 0.05) -> bool:
    """Return True when mean and median are within `threshold` fraction of each other."""
    if mean == 0 and median == 0:
        return True
    denom = abs(mean) if abs(mean) >= abs(median) else abs(median)
    return abs(mean - median) / denom <= threshold


def make_histogram(series: pd.Series, col_name: str, mean: float, median: float) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5, 3.2))
    fig.patch.set_facecolor("#1a1f2e")
    ax.set_facecolor("#0f1117")

    n_bins = min(30, max(10, int(np.sqrt(series.dropna().shape[0]))))
    counts, bins, patches = ax.hist(
        series.dropna(), bins=n_bins,
        color="#3d5af1", edgecolor="#0f1117", linewidth=0.4, alpha=0.85,
    )

    ax.axvline(mean,   color="#f72585", linewidth=1.8, linestyle="--", label=f"Mean   {mean:,.3f}")
    ax.axvline(median, color="#4cc9f0", linewidth=1.8, linestyle=":",  label=f"Median {median:,.3f}")

    ax.legend(fontsize=8, facecolor="#1a1f2e", edgecolor="#2a3050",
              labelcolor="#c5cae9", framealpha=0.9)

    ax.set_title(col_name, color="#c5cae9", fontsize=10, fontweight="600", pad=8)
    ax.tick_params(colors="#6b7a99", labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a3050")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{x:,.0f}" if abs(x) >= 1 else f"{x:.2f}"
    ))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Value",     color="#6b7a99", fontsize=7)
    ax.set_ylabel("Frequency", color="#6b7a99", fontsize=7)
    fig.tight_layout()
    return fig


# ── Main logic ────────────────────────────────────────────────────────────────
if uploaded:
    try:
        df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        st.warning("No numerical columns found in this file.")
        st.stop()

    # ── Dataset overview cards ────────────────────────────────────────────────
    forecast_count = sum(
        is_forecast_ready(df[c].mean(), df[c].median()) for c in numeric_cols
    )
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="label">Rows</div>
            <div class="value">{df.shape[0]:,}</div>
            <div class="sub">total records</div>
        </div>
        <div class="stat-card">
            <div class="label">Columns (total)</div>
            <div class="value">{df.shape[1]:,}</div>
            <div class="sub">in uploaded file</div>
        </div>
        <div class="stat-card">
            <div class="label">Numeric Columns</div>
            <div class="value">{len(numeric_cols)}</div>
            <div class="sub">analysed below</div>
        </div>
        <div class="stat-card">
            <div class="label">Forecast-Ready</div>
            <div class="value">{forecast_count}</div>
            <div class="sub">of {len(numeric_cols)} numeric columns</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Per-column analysis ───────────────────────────────────────────────────
    # Lay out 2 columns of panels
    col_pairs = [numeric_cols[i:i+2] for i in range(0, len(numeric_cols), 2)]

    for pair in col_pairs:
        grid = st.columns(len(pair))
        for col_widget, col_name in zip(grid, pair):
            with col_widget:
                series  = df[col_name].dropna()
                mean    = float(series.mean())
                median  = float(series.median())
                std     = float(series.std())
                ready   = is_forecast_ready(mean, median)

                st.markdown(f'<p class="col-header">{col_name}</p>', unsafe_allow_html=True)

                # Stat row
                c1, c2, c3 = st.columns(3)
                c1.metric("Mean",   f"{mean:,.4g}")
                c2.metric("Median", f"{median:,.4g}")
                c3.metric("Std Dev", f"{std:,.4g}")

                # Forecast badge
                if ready:
                    badge = '<span class="badge-yes">✅ Forecast-Ready — mean ≈ median (symmetric distribution)</span>'
                else:
                    pct = abs(mean - median) / (abs(mean) if mean else abs(median) or 1) * 100
                    badge = f'<span class="badge-no">⚠️ Skewed — mean &amp; median differ by {pct:.1f}%, forecasting needs caution</span>'
                st.markdown(badge, unsafe_allow_html=True)

                # Histogram
                fig = make_histogram(series, col_name, mean, median)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                st.markdown("<br>", unsafe_allow_html=True)

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Summary Table")

    rows = []
    for col_name in numeric_cols:
        s      = df[col_name].dropna()
        mean   = float(s.mean())
        median = float(s.median())
        skew   = float(s.skew())
        ready  = is_forecast_ready(mean, median)
        rows.append({
            "Column"         : col_name,
            "Count"          : int(s.count()),
            "Mean"           : round(mean, 4),
            "Median"         : round(median, 4),
            "Std Dev"        : round(float(s.std()), 4),
            "Skewness"       : round(skew, 4),
            "Forecast-Ready?": "✅ Yes" if ready else "⚠️ No",
        })

    summary_df = pd.DataFrame(rows).set_index("Column")
    st.dataframe(summary_df, use_container_width=True)

    # Download button
    csv_buf = io.StringIO()
    summary_df.to_csv(csv_buf)
    st.download_button(
        "⬇️ Download Summary CSV",
        csv_buf.getvalue(),
        file_name="analysis_summary.csv",
        mime="text/csv",
    )

else:
    st.info("👆 Upload an Excel file to get started.")
