import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

C1 = dict(fill="#E4D7F0", edge="#7A4FA3")
C2 = dict(fill="#F7E3C6", edge="#D9822B")
C3 = dict(fill="#FCE9B8", edge="#C79A2E")
C4 = dict(fill="#D5EAD5", edge="#3E8E4E")
CC = dict(fill="#DFF0DF", edge="#3E8E4E")
HEAD_FILL, HEAD_EDGE = "#DAD9DE", "#9A98A2"
T1_ROWS = ["#ECEBF7", "#E3E1F1"]
T2_ROWS = ["#FBEEE9", "#F6E6DE"]

W_IN, H_IN = 15.0, 9.5
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=9.2, bfs=7.6,
             gap_hd=0.10):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.09",
        linewidth=1.5, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=3))
    hlines = header.split("\n")
    HH, LB = lh(hfs), lh(bfs)
    block_h = len(hlines)*HH + (gap_hd + len(body)*LB if body else 0)
    top = cy + block_h/2
    y = top
    for hl in hlines:
        ax.text(cx, y - HH/2, hl, ha="center", va="center",
                fontsize=hfs, fontweight="bold", color=edge, zorder=4)
        y -= HH
    y -= gap_hd
    for line in body:
        ax.text(cx, y - LB/2, line, ha="center", va="center",
                fontsize=bfs, color="#1a1a1a", zorder=4)
        y -= LB

def harrow(x0, x1, y, color="#444444", lw=1.8, ms=16):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

def draw_table(x_left, y_top, col_w, row_h, header, rows, hfill, hedge, row_fills):
    edges = [x_left]
    for w in col_w:
        edges.append(edges[-1] + w)
    g = 0.06
    def cell(xl, yl, w, h, text, fill, edge, bold):
        ax.add_patch(FancyBboxPatch((xl+g/2, yl+g/2), w-g, h-g,
            boxstyle="round,pad=0.01,rounding_size=0.04",
            linewidth=1.0, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=3))
        ax.text(xl+w/2, yl+h/2, text, ha="center", va="center",
                fontsize=8.4 if bold else 8.2, fontweight="bold" if bold else "normal",
                color="#222222", zorder=4)

    for c in range(len(col_w)):
        cell(edges[c], y_top-row_h, col_w[c], row_h, header[c], hfill, hedge, True)

    for i, row in enumerate(rows):
        yl = y_top - (i+2)*row_h
        f = row_fills[i % len(row_fills)]
        for c in range(len(col_w)):
            cell(edges[c], yl, col_w[c], row_h, row[c], f, "#FFFFFF", False)

ax.text(W_IN/2, H_IN-0.32,
        "GESP Network Overhead and Latency Analysis: Monte Carlo Simulation Pipeline",
        ha="center", va="center", fontsize=15, fontweight="bold", color="#1a1a1a")

PY, BH = 7.65, 2.35
stages = [
 (1.70, "1. Packet Ingestion",
  ["Sensor packet arrival", r"Parse WGS-84 ($\varphi,\lambda$)",
   r"Payload $\rho$ · time $t$ · seq $v$", "Sliding-window buffer",
   "Per-gateway batching"], 2.70, C1),
 (4.90, "2. ECDSA Signing\n& Verification",
  [r"Build packet $P_i=(\varphi,\lambda,\rho,t,v)$",
   r"$\sigma=$ ECDSA.Sign($sk_i,h_i$)", r"$T_{\mathrm{sign}}\approx310$ ms",
   r"$T_{\mathrm{verify}}\approx580$ ms", "ARM Cortex-M33 · no HW accel."], 2.70, C2),
 (8.10, "3. Consensus\n& Anomaly Filter",
  [r"Geo-weighted tally ($\tau=2/3$)", r"Mahalanobis $D^2>\chi^2_{2,0.99}$",
   r"Z-score $|z|>3\sigma$ · $A_i$ score", r"$T_{\mathrm{consensus}}$ per vote"], 2.70, C3),
 (11.30, "4. Validated\nDispatch",
  ["Signed WGS-84 packet", "Spatial index · metadata", "PostGIS store",
   "OGC WFS / WMS / WCS"], 2.70, C4),
]
for cx, head, body, w, col in stages:
    draw_box(cx, PY, w, BH, head, body, col["fill"], col["edge"])
draw_box(13.90, PY, 1.50, 1.70, "Cloud GIS\nOutput", ["validated"],
         CC["fill"], CC["edge"], hfs=9.6)

for x0, x1 in [(3.05, 3.55), (6.25, 6.75), (9.45, 9.95)]:
    harrow(x0, x1, PY)
harrow(12.65, 13.15, PY, color="#3E8E4E")

ax.text(2.20, 6.18,
        "Simulation cluster configurations (100 Monte Carlo runs each, "
        "K varied 0-35% in 5% steps):",
        ha="left", va="center", fontsize=9.2, fontweight="bold", color="#333333")
draw_table(2.20, 5.95, [2.30, 3.00, 2.30, 3.00], 0.52,
           ["Cluster", r"Baseline $\rightarrow$ GESP", "Overhead", "Energy / cycle"],
           [["50 nodes",  r"12.4 $\rightarrow$ 13.1 ms", "+5.6%", r"142 $\mu$J"],
            ["150 nodes", r"24.8 $\rightarrow$ 26.5 ms", "+6.8%", r"158 $\mu$J"],
            ["500 nodes", r"58.2 $\rightarrow$ 63.1 ms", "+8.4%", r"187 $\mu$J"]],
           HEAD_FILL, HEAD_EDGE, T1_ROWS)

ax.text(2.20, 3.58,
        "Attack detection ($K$ = 20% compromise ratio, 100 Monte Carlo runs):",
        ha="left", va="center", fontsize=9.2, fontweight="bold", color="#333333")
draw_table(2.20, 3.35, [3.20, 2.30, 2.30, 2.80], 0.52,
           ["Attack scenario", "Detection rate", "False positive", "GESP component"],
           [["GPS coord. spoofing",     "97.0%", "< 1.2% FP", "Consensus + Mahalanobis"],
            ["Sensor payload injection", "94.0%", "< 1.8% FP", "Consensus + Z-score"],
            ["Packet replay",            "99.7%", "< 0.1% FP", "Freshness + seq-no"]],
           HEAD_FILL, HEAD_EDGE, T2_ROWS)

ax.add_patch(FancyBboxPatch((2.20, 0.42), 10.60, 0.46,
    boxstyle="round,pad=0.02,rounding_size=0.08",
    linewidth=1.0, edgecolor="#C9C7D2", facecolor="#F3F2F8", zorder=3))
ax.text(7.50, 0.65,
        r"sub-8.5% latency overhead  ·  Byzantine-tolerant $K<n/3$  ·  "
        r"142-187 $\mu$J per packet  ·  $\approx$3.9-yr battery life at 500 nodes",
        ha="center", va="center", fontsize=9.0, color="#3a3a3a", zorder=4)

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_network_latency.pdf"))
fig.savefig(os.path.join(outdir, "fig_network_latency.png"), dpi=600)
plt.close(fig)
print("wrote fig_network_latency.png,pdf to", os.path.abspath(outdir))

