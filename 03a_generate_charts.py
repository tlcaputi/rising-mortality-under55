"""
Generate three standalone chart PDFs for the heart-attack mortality figure.
LaTeX (03b_compose_figure.tex) assembles them into the final page.

Charts:
  1. stemi_cfr.pdf    — Satish et al. in-hospital STEMI case fatality
  2. mi_deaths.pdf    — CDC WONDER heart attack deaths per year
  3. mi_rate.pdf      — CDC WONDER heart attack death rate per 100K
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
OUT_DIR = os.path.join(os.path.dirname(__file__), "output", "charts")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load CDC WONDER data ─────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, "overall.csv"))
mi = df[df["cause"] == "Acute myocardial infarction (I21-I22)"].sort_values("year")

# ── In-hospital STEMI CFR from Satish et al. (2026), JAHA ────────────────
stemi_cfr = pd.DataFrame({"year": [2011, 2022], "cfr": [2.1, 3.3]})

# ── Filter to same time frame as Satish et al. (2011–2022) ──────────────
mi = mi[(mi["year"] >= 2011) & (mi["year"] <= 2022)]

# ── Key numbers ──────────────────────────────────────────────────────────
y11 = mi[mi["year"] == 2011]["deaths"].values[0]
y22 = mi[mi["year"] == 2022]["deaths"].values[0]
r11 = mi[mi["year"] == 2011]["crude_rate"].values[0]
r22 = mi[mi["year"] == 2022]["crude_rate"].values[0]
pct_deaths = (y22 - y11) / y11 * 100
pct_rate = (r22 - r11) / r11 * 100

# Write key numbers to a file so LaTeX can use them
with open(os.path.join(OUT_DIR, "numbers.tex"), "w") as f:
    f.write(f"\\newcommand{{\\yStart}}{{{y11:,.0f}}}\n")
    f.write(f"\\newcommand{{\\yEnd}}{{{y22:,.0f}}}\n")
    f.write(f"\\newcommand{{\\rStart}}{{{r11:.1f}}}\n")
    f.write(f"\\newcommand{{\\rEnd}}{{{r22:.1f}}}\n")
    f.write(f"\\newcommand{{\\pctDeaths}}{{{abs(pct_deaths):.0f}}}\n")
    f.write(f"\\newcommand{{\\pctRate}}{{{abs(pct_rate):.0f}}}\n")

# ── Style ────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
})

C_BLUE = "#1a5276"
C_RED  = "#c0392b"
C_GRAY = "#666666"

def style_ax(ax, ylabel=None):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=13, length=4)
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    if ylabel:
        ax.set_ylabel("")
        ax.text(-0.01, 1.02, ylabel, transform=ax.transAxes,
                fontsize=14, ha="left", va="bottom", color=C_GRAY)

# ═════════════════════════════════════════════════════════════════════════
# Chart 1: STEMI CFR
# ═════════════════════════════════════════════════════════════════════════
fig1, ax = plt.subplots(figsize=(7.5, 4.5), facecolor="white")
ax.plot(stemi_cfr["year"], stemi_cfr["cfr"], "--", color=C_RED,
        linewidth=2, zorder=2, dashes=(6, 4))
ax.plot(stemi_cfr["year"], stemi_cfr["cfr"], "o", color=C_RED,
        markersize=12, zorder=3, markeredgecolor="white", markeredgewidth=2)
ax.set_xlim(2008, 2025)
ax.set_ylim(0, 5)
ax.set_xticks([2011, 2022])
ax.set_xticklabels(["2011", "2022"], fontsize=13)
style_ax(ax, ylabel="In-Hospital Mortality (%)")

ax.annotate("2.1%", (2011, 2.1), textcoords="offset points",
            xytext=(-18, -24), fontsize=15, fontweight="bold", color=C_RED)
ax.annotate("3.3%", (2022, 3.3), textcoords="offset points",
            xytext=(12, -6), fontsize=15, fontweight="bold", color=C_RED)
ax.text(0.50, 0.92, "Reported endpoints only (NIS, 2011\u20132022)",
        ha="center", fontsize=13, color=C_GRAY, fontstyle="italic",
        transform=ax.transAxes)

fig1.tight_layout(pad=0.5)
fig1.savefig(os.path.join(OUT_DIR, "stemi_cfr.pdf"), dpi=300)
plt.close(fig1)
print("Saved stemi_cfr.pdf")

# ═════════════════════════════════════════════════════════════════════════
# Chart 2: MI Deaths
# ═════════════════════════════════════════════════════════════════════════
fig2, ax = plt.subplots(figsize=(7.5, 4.5), facecolor="white")
ax.fill_between(mi["year"], 0, mi["deaths"], alpha=0.15, color=C_BLUE)
ax.plot(mi["year"], mi["deaths"], "-o", color=C_BLUE,
        markersize=5, linewidth=2.5, markeredgewidth=0)
ax.set_xlim(2010, 2023)
ax.set_ylim(0, mi["deaths"].max() * 1.22)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
style_ax(ax, ylabel="Deaths")

ax.annotate(f"{y11:,.0f}", (2011, y11), textcoords="offset points",
            xytext=(10, 14), fontsize=14, fontweight="bold", color=C_BLUE)
ax.annotate(f"{y22:,.0f}", (2022, y22), textcoords="offset points",
            xytext=(-55, -20), fontsize=14, fontweight="bold", color=C_BLUE)
ax.text(2016.5, mi["deaths"].max() * 1.08, f"{pct_deaths:.0f}%",
        fontsize=34, fontweight="bold", color=C_RED,
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor="none", alpha=0.85))

fig2.tight_layout(pad=0.5)
fig2.savefig(os.path.join(OUT_DIR, "mi_deaths.pdf"), dpi=300)
plt.close(fig2)
print("Saved mi_deaths.pdf")

# ═════════════════════════════════════════════════════════════════════════
# Chart 3: MI Rate
# ═════════════════════════════════════════════════════════════════════════
fig3, ax = plt.subplots(figsize=(7.5, 4.5), facecolor="white")
ax.fill_between(mi["year"], 0, mi["crude_rate"], alpha=0.15, color=C_BLUE)
ax.plot(mi["year"], mi["crude_rate"], "-o", color=C_BLUE,
        markersize=5, linewidth=2.5, markeredgewidth=0)
ax.set_xlim(2010, 2023)
ax.set_ylim(0, mi["crude_rate"].max() * 1.22)
style_ax(ax, ylabel="Deaths per 100,000")

ax.annotate(f"{r11:.1f}", (2011, r11), textcoords="offset points",
            xytext=(10, 14), fontsize=14, fontweight="bold", color=C_BLUE)
ax.annotate(f"{r22:.1f}", (2022, r22), textcoords="offset points",
            xytext=(-48, -20), fontsize=14, fontweight="bold", color=C_BLUE)
ax.text(2016.5, mi["crude_rate"].max() * 1.08, f"{pct_rate:.0f}%",
        fontsize=34, fontweight="bold", color=C_RED,
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor="none", alpha=0.85))

fig3.tight_layout(pad=0.5)
fig3.savefig(os.path.join(OUT_DIR, "mi_rate.pdf"), dpi=300)
plt.close(fig3)
print("Saved mi_rate.pdf")
