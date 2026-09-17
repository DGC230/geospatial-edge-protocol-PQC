import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Nimbus Sans", "Helvetica", "Arial"],
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

C_SENS = dict(fill="#D3E9E4", edge="#2E8B8B")
C_GW   = dict(fill="#FBE0C6", edge="#D9822B")
C_GESP = dict(fill="#D5EAD5", edge="#3E8E4E")
C_CLOUD = dict(fill="#CFE2F3", edge="#2E6DA4")
C_ATK  = dict(fill="#F6D6D2", edge="#C0392B")
L_UP   = "#7A9CC0"
L_GW   = "#D9822B"
BAND1, BAND2, BAND3 = "#EAF5F2", "#FDF2E4", "#EEF3FB"

W_IN, H_IN = 13.4, 7.2
def lh(fs): return fs * 1.16 / 72.0

fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_IN); ax.set_ylim(0, H_IN); ax.axis("off")

BX0, BX1 = 0.05, W_IN - 0.05
BANDS = [(0.45, 2.70, BAND1), (2.70, 4.90, BAND2), (4.90, 7.05, BAND3)]
for y0, y1, c in BANDS:
    ax.add_patch(Rectangle((BX0, y0), BX1 - BX0, y1 - y0, facecolor=c,
                           edgecolor="none", zorder=0))
ax.text(0.28, 1.575, "TIER 1  -  IoT Sensing Layer", rotation=90, ha="center",
        va="center", fontsize=8.5, fontweight="bold", color="#227d7d", zorder=1)
ax.text(0.28, 3.80, "TIER 2  -  Edge Computation Layer", rotation=90, ha="center",
        va="center", fontsize=8.5, fontweight="bold", color="#c07a1e", zorder=1)
ax.text(0.28, 5.97, "TIER 3  -  GIS Cloud Layer", rotation=90, ha="center",
        va="center", fontsize=8.5, fontweight="bold", color="#2E6DA4", zorder=1)

def draw_box(cx, cy, w, h, header, body, fill, edge, hfs=8.6, bfs=7.6,
             gap_hd=0.06, lw=1.4, ls="solid"):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=lw, edgecolor=edge, facecolor=fill, linestyle=ls,
        mutation_aspect=1.0, zorder=4))
    HH, LB = lh(hfs), lh(bfs)
    block_h = HH + (gap_hd + len(body)*LB if body else 0)
    top = cy + block_h/2
    ax.text(cx, top - HH/2, header, ha="center", va="center",
            fontsize=hfs, fontweight="bold", color=edge, zorder=5)
    y = top - HH - gap_hd
    for line in body:
        ax.text(cx, y - LB/2, line, ha="center", va="center",
                fontsize=bfs, color="#1a1a1a", zorder=5)
        y -= LB

def vline(x, y0, y1, c, lw=1.2):
    ax.plot([x, x], [y0, y1], color=c, lw=lw, solid_capstyle="projecting", zorder=2)
def hline(x0, x1, y, c, lw=1.2):
    ax.plot([x0, x1], [y, y], color=c, lw=lw, solid_capstyle="projecting", zorder=2)
def arrow(x0, y0, x1, y1, color, lw=1.8, ms=16):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=3))

def bus(px, py_bot, child_xs, child_top, bus_y, color, lw=1.2):
    xmin, xmax = min(child_xs + [px]), max(child_xs + [px])
    hline(xmin, xmax, bus_y, color, lw)
    vline(px, bus_y, py_bot, color, lw)
    for cx in child_xs:
        vline(cx, child_top, bus_y, color, lw)

SENSORS = ["TMP Sensor", "Hydro Sensor", "Seismic Node", "GPS Node",
           "AgriSen Node", "SubSen Node", "Air Sensor"]
sx = [2.55 + i*(12.55-2.55)/6 for i in range(7)]
SY, SW, SH = 1.15, 1.30, 0.85
BYZ = {1, 4}
for i, (name, x) in enumerate(zip(SENSORS, sx)):
    if i in BYZ:
        draw_box(x, SY, SW, SH, name, [], C_SENS["fill"], C_ATK["edge"],
                 hfs=8.4, lw=1.8, ls="--")
        ax.text(x, SY + SH/2 + 0.13, "Byzantine", ha="center", va="bottom",
                fontsize=7.0, fontweight="bold", color=C_ATK["edge"], zorder=6,
                bbox=dict(boxstyle="round,pad=0.10", fc=BAND1, ec="none"))
    else:
        draw_box(x, SY, SW, SH, name, [], C_SENS["fill"], C_SENS["edge"], hfs=8.4)

GWY, GWW, GWH = 3.60, 1.70, 0.95
gw = [("Edge GW-A", (sx[0]+sx[2])/2, [sx[0], sx[1], sx[2]]),
      ("Edge GW-B", (sx[3]+sx[4])/2, [sx[3], sx[4]]),
      ("Edge GW-C", (sx[5]+sx[6])/2, [sx[5], sx[6]])]
for name, gxc, kids in gw:
    draw_box(gxc, GWY, GWW, GWH, name, ["ECDSA verify", "+ Consensus"],
             C_GW["fill"], C_GW["edge"], hfs=8.8, bfs=7.6)

GESP_X, GESP_Y = 7.55, 4.90
draw_box(GESP_X, GESP_Y, 3.40, 0.86, "GESP Security Module",
         ["Merkle cert store · Anomaly filter · Consensus tally"],
         C_GESP["fill"], C_GESP["edge"], hfs=9.0, bfs=7.6)

CLOUD_X, CLOUD_Y = 7.55, 6.15
draw_box(CLOUD_X, CLOUD_Y, 5.60, 1.02, "PostGIS Cloud  -  WFS / WMS Services",
         ["Spatial Analytics · Change Detection · Thematic Mapping"],
         C_CLOUD["fill"], C_CLOUD["edge"], hfs=10.0, bfs=8.0)

bus(GESP_X, GESP_Y - 0.86/2, [g[1] for g in gw], GWY + GWH/2, 4.25, L_GW, lw=1.3)
ax.text(5.90, 4.25, "TLS 1.3", ha="center", va="center", fontsize=7.4,
        style="italic", color="#9a6b1e", zorder=5,
        bbox=dict(boxstyle="round,pad=0.16", fc=BAND2, ec="none"))

for name, gxc, kids in gw:
    bus(gxc, GWY - GWH/2, kids, SY + SH/2, 2.15, L_UP, lw=1.2)
ax.text(6.71, 2.15, "LoRaWAN / NB-IoT", ha="center", va="center", fontsize=7.4,
        style="italic", color="#5f7a97", zorder=5,
        bbox=dict(boxstyle="round,pad=0.16", fc=BAND1, ec="none"))

arrow(GESP_X, GESP_Y + 0.86/2, CLOUD_X, CLOUD_Y - 1.02/2, "#3E8E4E", lw=2.0, ms=16)
ax.text(GESP_X + 0.16, (GESP_Y + 0.86/2 + CLOUD_Y - 1.02/2)/2, "Validated\nstream",
        ha="left", va="center", fontsize=7.4, style="italic", color="#3E8E4E", zorder=5)

draw_box(1.15, 2.15, 1.30, 0.92, "MitM / Spoofing", ["Attack"],
         C_ATK["fill"], C_ATK["edge"], hfs=8.4, bfs=7.8)
arrow(1.80, 2.15, sx[0] - 0.05, 2.15, C_ATK["edge"], lw=2.0, ms=15)

LEG = [("IoT Sensor Node", C_SENS["edge"]), ("Edge Gateway (GESP)", C_GW["edge"]),
       ("GESP Security Module", C_GESP["edge"]), ("GIS Cloud / PostGIS", C_CLOUD["edge"]),
       ("Byzantine / Attack", C_ATK["edge"])]
lx = [1.50, 4.05, 6.70, 9.35, 11.75]
for (label, col), x in zip(LEG, lx):
    ax.add_patch(Rectangle((x, 0.16), 0.17, 0.17, facecolor=col, edgecolor="none", zorder=5))
    ax.text(x + 0.26, 0.245, label, ha="left", va="center", fontsize=7.3,
            color="#333333", zorder=5)

outdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(outdir, exist_ok=True)
fig.savefig(os.path.join(outdir, "fig1_architecture.pdf"))
fig.savefig(os.path.join(outdir, "fig1_architecture.png"), dpi=600)
plt.close(fig)
print("wrote fig1_architecture.{png,pdf} to", os.path.abspath(outdir))

