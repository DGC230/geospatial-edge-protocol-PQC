import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.linewidth": 0.9,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
})

BLUE, VERM, GREEN = "#0072B2", "#D55E00", "#009E73"
SKY, BASEF, GESPF = "#56B4E9", "#CDE3F4", "#3B7CB5"
GRID = "#D9D9D9"

fig, (axA, axB) = plt.subplots(1, 2, figsize=(14.0, 6.0))
fig.subplots_adjust(wspace=0.28, left=0.06, right=0.945, top=0.92, bottom=0.12)

K = np.array([0, 5, 10, 15, 20, 25, 30, 35], float)
spoof = np.array([99.8, 99.5, 99.0, 98.2, 97.0, 95.1, 93.2, 90.8])
inject = np.array([99.0, 98.5, 97.5, 96.0, 94.2, 92.0, 89.5, 86.8])
replay = np.array([99.9, 99.9, 99.85, 99.8, 99.7, 99.7, 99.6, 99.5])
b_spoof = np.array([0.25, 0.30, 0.40, 0.50, 0.65, 0.85, 1.10, 1.40])
b_inject = np.array([0.30, 0.40, 0.55, 0.70, 0.90, 1.15, 1.45, 1.80])
b_replay = np.full_like(K, 0.10)

axA.set_axisbelow(True)
axA.grid(which="major", color=GRID, linewidth=0.7, zorder=0)
axA.grid(which="minor", color=GRID, linewidth=0.35, alpha=0.5, zorder=0)

for y, b, c, mk, lab in [
        (spoof, b_spoof, BLUE, "o", "Coordinate spoofing"),
        (inject, b_inject, VERM, "s", "Data injection"),
        (replay, b_replay, GREEN, "^", "Replay attack")]:
    axA.fill_between(K, y-b, y+b, color=c, alpha=0.15, linewidth=0, zorder=1)
    axA.plot(K, y, color=c, lw=1.9, marker=mk, ms=6.5, mfc=c, mec="white",
             mew=0.8, label=lab, zorder=3)

axA.axvline(100/3, color="#C0392B", lw=1.2, ls=(0, (5, 3)), zorder=2)
axA.annotate("Byzantine\nlimit $n/3$", xy=(100/3, 87.6),
             xytext=(30.0, 86.0), fontsize=8.5, color="#C0392B", ha="right",
             va="center", linespacing=1.15,
             arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=1.0,
                             shrinkA=2, shrinkB=1))

axA.set_xlim(-1.5, 36.5)
axA.set_ylim(84, 100.4)
axA.set_xlabel("Compromise ratio $K/N$  (%)", fontsize=11)
axA.set_ylabel("Byzantine-node detection rate (%)", fontsize=11)
axA.set_title("(a)  Detection rate vs. compromise ratio", fontsize=12,
              fontweight="bold", loc="center")
axA.xaxis.set_major_locator(MultipleLocator(5))
axA.xaxis.set_minor_locator(AutoMinorLocator(5))
axA.yaxis.set_major_locator(MultipleLocator(2))
axA.yaxis.set_minor_locator(AutoMinorLocator(2))
axA.tick_params(labelsize=9.5)
axA.legend(loc="lower left", fontsize=9.5, framealpha=0.95, edgecolor="#BBBBBB")

labels = ["50 nodes", "150 nodes", "500 nodes"]
xb = np.arange(3)
baseline = np.array([12.4, 24.8, 58.2])
gesp = np.array([13.1, 26.5, 63.1])
over = ["+5.6%", "+6.9%", "+8.4%"]
energy = np.array([142, 158, 187])
w = 0.38

axB.set_axisbelow(True)
axB.grid(which="major", axis="y", color=GRID, linewidth=0.7, zorder=0)
axB.grid(which="minor", axis="y", color=GRID, linewidth=0.35, alpha=0.5, zorder=0)

bh = axB.bar(xb-w/2, baseline, w, color=BASEF, edgecolor="#5A8FBF", linewidth=1.0,
             label="Baseline (unsecured)", zorder=2)
gh = axB.bar(xb+w/2, gesp, w, color=GESPF, edgecolor="#1E4E77", linewidth=1.0,
             label="GESP (secured)", zorder=2)
for xi, gv, ov in zip(xb, gesp, over):
    axB.annotate(ov, xy=(xi+w/2, gv), xytext=(0, 4), textcoords="offset points",
                 ha="center", va="bottom", fontsize=9.2, fontweight="bold",
                 color="#C0392B", zorder=5)

axB.set_xticks(xb)
axB.set_xticklabels(labels, fontsize=10)
axB.set_xlim(-0.65, 2.65)
axB.set_ylim(0, 72)
axB.set_xlabel("Cluster size", fontsize=11)
axB.set_ylabel("End-to-end latency (ms)", fontsize=11)
axB.set_title("(b)  Latency overhead per cluster size", fontsize=12,
              fontweight="bold", loc="center")
axB.yaxis.set_major_locator(MultipleLocator(10))
axB.yaxis.set_minor_locator(AutoMinorLocator(2))
axB.tick_params(labelsize=9.5)

axE = axB.twinx()
eh, = axE.plot(xb, energy, color=VERM, lw=2.0, ls=(0, (1, 1.2)), marker="D",
               ms=9, mfc=VERM, mec="white", mew=0.9,
               label=r"Energy ($\mu$J / cycle)", zorder=4)
axE.set_ylim(120, 220)
axE.set_ylabel(r"Energy consumption ($\mu$J / cycle)", fontsize=11, color=VERM)
axE.yaxis.set_major_locator(MultipleLocator(20))
axE.yaxis.set_minor_locator(AutoMinorLocator(2))
axE.tick_params(axis="y", labelsize=9.5, colors=VERM)
axE.spines["right"].set_color(VERM)

axB.legend(handles=[bh, gh, eh],
           labels=["Baseline (unsecured)", "GESP (secured)", r"Energy ($\mu$J / cycle)"],
           loc="upper left", fontsize=9.3, framealpha=0.95, edgecolor="#BBBBBB")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig4_results.pdf"))
fig.savefig(os.path.join(outdir, "fig4_results.png"), dpi=600)
plt.close(fig)
print("wrote fig4_results.png,pdf to", os.path.abspath(outdir))

