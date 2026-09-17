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

TH_CLIENT = dict(cont_fill="#E9F1FB", cont_edge="#3A6EA5",
                 box_fill="#D6E6F5", box_edge="#2E6DA4")
TH_SERVER = dict(cont_fill="#E6F2E6", cont_edge="#3E8E4E",
                 box_fill="#D5EAD5", box_edge="#2E7D45")
TH_DATA   = dict(cont_fill="#FBF1DC", cont_edge="#C8912B",
                 box_fill="#F5E6C8", box_edge="#B8860B")

CLIENT = ("Client Side", TH_CLIENT, [
    ("IoT Sensor Node / Workstation", ["nRF9160 SiP \u00b7 Cortex-M33",
                                        "Python 3.11 tooling"]),
    ("IDE / Jupyter Notebook",        ["ECDSA key provisioning",
                                        "SimPy \u00b7 matplotlib scripts"]),
    ("Results Monitor",               ["Detection-rate curves",
                                        "Latency & energy histograms"]),
])
SERVER = ("Server Side (Cloud / Local)", TH_SERVER, [
    ("Compute Node",            ["CPU VM \u00b7 8 vCPU \u00b7 32 GB RAM",
                                 "Edge gateway: Raspberry Pi 4",
                                 "PostgreSQL 14 / PostGIS 3.3"]),
    ("GESP Simulation Pipeline", ["Monte Carlo (SimPy · 500 nodes · 100 runs)",
                                  "ECDSA P-256 sign/verify (Scripts 1\u20133)",
                                  "Peer-consensus \u00b7 Mahalanobis / Z-score",
                                  r"$K/N$ swept 0–35% in 5% steps"]),
])
DATA = ("Data Sources", TH_DATA, [
    ("OGC Data Services",  ["WFS \u00b7 WMS \u00b7 WCS", "SensorThings API"]),
    ("GitHub Repository",  ["GESP code (Scripts 1\u20133)", "ECDSA key store"]),
    ("Simulation Inputs",  ["500-node synthetic field",
                            r"$100\times100$ km$^2$ Poisson field",
                            "WGS-84 coordinate streams"]),
])

W_IN, H_IN = 15.0, 5.8
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=9.5, bfs=8.2, gap_hd=0.08):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        linewidth=1.3, edgecolor=edge, facecolor=fill, mutation_aspect=1.0, zorder=3))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body)*LB if body else 0)
    top = cy + block_h/2
    ax.text(cx, top - HH/2, header, ha="center", va="center",
            fontsize=hfs, fontweight="bold", color=edge, zorder=4)
    y = top - HH - gap_hd
    for line in body:
        ax.text(cx, y - LB/2, line, ha="center", va="center",
                fontsize=bfs, color="#1a1a1a", zorder=4)
        y -= LB

def arrow(x0, y0, x1, y1, color="#333333", lw=1.7, ms=16):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

PAN_Y0, PAN_Y1 = 0.55, 5.05
HDR_Y = 4.80
SUB_TOP, SUB_BOT = 4.45, 0.72
panels = [(0.30, 4.60, CLIENT), (5.50, 9.90, SERVER), (10.80, 14.70, DATA)]

def draw_panel(x0, x1, spec):
    title, th, boxes = spec
    ax.add_patch(FancyBboxPatch((x0, PAN_Y0), x1-x0, PAN_Y1-PAN_Y0,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=1.6, edgecolor=th["cont_edge"], facecolor=th["cont_fill"],
        mutation_aspect=1.0, zorder=1))
    ax.text((x0+x1)/2, HDR_Y, title, ha="center", va="center",
            fontsize=11, fontweight="bold", color=th["cont_edge"], zorder=4)
    cx = (x0+x1)/2; sub_w = (x1-x0) - 0.5
    n = len(boxes)
    if n == 3:
        h = 0.98; gap = (SUB_TOP - SUB_BOT - n*h)/(n-1)
        centers = [SUB_TOP - h/2 - i*(h+gap) for i in range(n)]
        heights = [h]*n
    else:
        h0, h1 = 1.35, 1.62
        c0 = SUB_TOP - h0/2
        c1 = SUB_BOT + h1/2
        centers = [c0, c1]; heights = [h0, h1]
    for (hdr, body), cy, h in zip(boxes, centers, heights):
        draw_box(cx, cy, sub_w, h, hdr, body, th["box_fill"], th["box_edge"])

for x0, x1, spec in panels:
    draw_panel(x0, x1, spec)

mid_y = (PAN_Y0 + PAN_Y1) / 2
arrow(4.60 + 0.02, mid_y, 5.50 - 0.02, mid_y)
ax.text((4.60 + 5.50)/2, mid_y + 0.14, "HTTP / REST", ha="center", va="bottom",
        fontsize=8.3, style="italic", color="#555555", zorder=4)
arrow(9.90 + 0.02, mid_y, 10.80 - 0.02, mid_y)
ax.text((9.90 + 10.80)/2, mid_y + 0.14, "data", ha="center", va="bottom",
        fontsize=8.3, style="italic", color="#555555", zorder=4)

ax.text(W_IN/2, H_IN - 0.26,
        "GESP System Deployment Architecture for Large-Scale IoT-GIS Validation",
        ha="center", va="center", fontsize=13.5, fontweight="bold", color="#1a1a1a")
ax.text(W_IN/2, 0.24,
        "Discrete-event (SimPy) evaluation of GESP over a 500-node IoT-GIS "
        "network: sub-8.5% latency overhead, Byzantine-tolerant for $K<n/3$.",
        ha="center", va="center", fontsize=8.6, color="#444444")

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig_gesp_system.pdf"))
fig.savefig(os.path.join(outdir, "fig_gesp_system.png"), dpi=600)
plt.close(fig)
print("wrote fig_gesp_system.{png,pdf} to", os.path.abspath(outdir))

